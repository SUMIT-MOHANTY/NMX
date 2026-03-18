from typing import Any
import uuid
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func

from app.db.session import get_db
from app.models.booking import Booking
from app.models.slot import Slot
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.email_service import send_booking_confirmation
from app.core.security import get_current_user

router = APIRouter()

def generate_confirmation_code() -> str:
    """Generate a random confirmation code."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    *,
    db: Session = Depends(get_db),
    booking_in: BookingCreate,
    current_user = Depends(get_current_user)
) -> Any:
    """
    Create a new booking for an appointment slot.

    - Validates that the slot exists and is available
    - Prevents duplicate bookings for the same slot
    - Generates a confirmation code
    - Sends a confirmation email to the user
    """
    # Verify that the user_id in request matches the authenticated user
    if booking_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only book appointments for yourself"
        )

    # Check if slot exists and has availability
    slot = db.query(Slot).filter(Slot.id == booking_in.slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    # Count existing bookings for this slot
    booking_count = db.query(func.count(Booking.id)).filter(
        Booking.slot_id == booking_in.slot_id,
        Booking.status != "cancelled"
    ).scalar()

    if booking_count >= slot.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot is no longer available"
        )

    # Check if user already has a booking for this slot
    existing_booking = db.query(Booking).filter(
        and_(
            Booking.user_id == booking_in.user_id,
            Booking.slot_id == booking_in.slot_id,
            Booking.status != "cancelled"
        )
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a booking for this slot"
        )

    # Create a new booking with a confirmation code
    confirmation_code = generate_confirmation_code()

    db_booking = Booking(
        user_id=booking_in.user_id,
        slot_id=booking_in.slot_id,
        confirmation_code=confirmation_code,
        status="confirmed",
        full_name=booking_in.personal_data.full_name,
        email=booking_in.personal_data.email,
        mobile=booking_in.personal_data.mobile
    )

    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot is no longer available"
        )

    # Send confirmation email
    try:
        send_booking_confirmation(
            email=db_booking.email,
            name=db_booking.full_name,
            booking_id=str(db_booking.id),
            confirmation_code=db_booking.confirmation_code,
            slot_date=slot.slot_date,
            slot_time=slot.slot_time,
            office_location=slot.office.name if hasattr(slot, 'office') else "N/A"
        )

        # Update the email_sent flag
        db_booking.email_sent = True
        db.commit()

    except Exception as e:
        # Log the error but don't fail the booking
        print(f"Failed to send confirmation email: {e}")

    return BookingResponse(
        id=db_booking.id,
        user_id=db_booking.user_id,
        slot_id=db_booking.slot_id,
        booking_time=db_booking.created_at,
        status=db_booking.status,
        confirmation_code=db_booking.confirmation_code
    )
