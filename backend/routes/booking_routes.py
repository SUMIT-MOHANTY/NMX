"""
Routes for booking management.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.booking import BookingCreate, BookingResponse
from app.models.user import User
from app.models.booking import Booking
from app.models.slot import Slot
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.email_service import email_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new booking for the current user.

    Args:
        booking: Booking data
        db: Database session
        current_user: Authenticated user

    Returns:
        BookingResponse: Created booking information
    """
    # Get the requested slot
    slot = db.query(Slot).filter(Slot.id == booking.slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    # Check if slot has available capacity
    if slot.remaining_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No capacity available for this slot"
        )

    # Create the booking
    booking_reference = f"PB-{current_user.id[:6]}-{slot.id[:6]}"
    new_booking = Booking(
        user_id=current_user.id,
        slot_id=booking.slot_id,
        booking_reference=booking_reference
    )

    # Update slot capacity
    slot.remaining_capacity -= 1

    # Commit changes to database
    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        # Prepare booking data for response and email
        booking_response = {
            "id": new_booking.id,
            "slot": {
                "id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "location": {
                    "id": slot.location.id,
                    "name": slot.location.name,
                    "address": slot.location.address
                }
            },
            "created_at": new_booking.created_at,
            "booking_reference": booking_reference
        }

        # Prepare email data
        email_data = {
            "booking_reference": booking_reference,
            "date": slot.start_time.strftime("%A, %B %d, %Y"),
            "time": f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}",
            "location_name": slot.location.name,
            "location_address": slot.location.address,
            "user_name": current_user.full_name,
            "management_url": f"https://passport-booking-system.example.com/bookings/{new_booking.id}"
        }

        # Send confirmation email asynchronously (non-blocking)
        # Note: In a real FastAPI app, consider using background tasks
        success, error = email_service.send_confirmation_email(
            current_user.email,
            email_data
        )

        if not success:
            # Log error but don't fail the booking process
            logger.error(f"Failed to send confirmation email: {error}")

        return booking_response

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )
