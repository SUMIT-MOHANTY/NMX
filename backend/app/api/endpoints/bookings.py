from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.booking import BookingCreate, BookingResponse
from app.crud import booking as booking_crud
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book an appointment slot",
    description="Create a booking for the logged-in user for the specified slot."
)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Create a booking for the authenticated user.

    - Verifies the slot exists and has capacity
    - Ensures user doesn't have a duplicate booking
    - Atomically increments slot capacity
    - Handles race conditions with database locks
    """
    # Extract user_id from the JWT token
    user_id = current_user["id"]

    # Check if the user already has a booking for this slot
    existing_booking = await booking_crud.check_existing_booking(
        db=db, user_id=user_id, slot_id=booking_data.slot_id
    )
    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a booking for this slot"
        )

    try:
        # Attempt to create the booking with race condition handling
        booking_result = await booking_crud.create_booking(
            db=db, user_id=user_id, slot_id=booking_data.slot_id
        )

        if not booking_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found or fully booked"
            )

        return booking_result

    except IntegrityError as e:
        # Handle any database integrity errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking could not be created: {str(e)}"
        )
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
