from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.models.booking import Booking
from app.models.slot import Slot
from app.models.user import User

async def create_booking(
    db: AsyncSession,
    user_id: UUID,
    slot_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    Create a booking for a user on a specific slot with proper race condition handling.
    Returns the booking data with slot details if successful, None if the slot is full.
    """
    async with db.begin():
        # Lock the slot for update to prevent race conditions
        stmt = select(Slot).where(Slot.id == slot_id).with_for_update()
        result = await db.execute(stmt)
        slot = result.scalars().first()

        if not slot:
            return None

        # Check if the slot is already full
        if slot.taken >= slot.capacity:
            return None

        try:
            # Create the booking
            booking = Booking(
                user_id=user_id,
                slot_id=slot_id,
                status="confirmed"
            )
            db.add(booking)

            # Increment the taken count atomically
            slot.taken += 1

            # Commit changes (will automatically release the lock)
            await db.commit()

            # Get the office location for the booking response
            stmt = select(Slot).options(
                selectinload(Slot.office)
            ).where(Slot.id == slot_id)
            result = await db.execute(stmt)
            slot_with_office = result.scalars().first()

            # Create response with slot details
            booking_data = {
                "id": booking.id,
                "user_id": booking.user_id,
                "slot_id": booking.slot_id,
                "status": booking.status,
                "booked_at": booking.booked_at,
                "slot_details": {
                    "slot_date": slot_with_office.slot_date,
                    "slot_time": slot_with_office.slot_time,
                    "office_location": slot_with_office.office.name if slot_with_office.office else "Unknown"
                }
            }

            return booking_data

        except IntegrityError:
            # Handle case where user already has booking for this slot
            await db.rollback()
            return None

async def check_existing_booking(
    db: AsyncSession,
    user_id: UUID,
    slot_id: UUID
) -> bool:
    """
    Check if a user already has a booking for a specific slot.
    Returns True if booking exists, False otherwise.
    """
    stmt = select(Booking).where(
        Booking.user_id == user_id,
        Booking.slot_id == slot_id
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    return existing is not None

async def get_user_bookings(
    db: AsyncSession,
    user_id: UUID
) -> List[Booking]:
    """
    Retrieve all bookings for a specific user.
    """
    stmt = select(Booking).where(Booking.user_id == user_id).order_by(Booking.booked_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_booking_by_id(
    db: AsyncSession,
    booking_id: UUID
) -> Optional[Booking]:
    """
    Retrieve a specific booking by ID.
    """
    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def update_booking_status(
    db: AsyncSession,
    booking_id: UUID,
    status: str
) -> Optional[Booking]:
    """
    Update the status of a booking.
    """
    stmt = update(Booking).where(Booking.id == booking_id).values(status=status)
    await db.execute(stmt)
    await db.commit()

    # Return the updated booking
    return await get_booking_by_id(db, booking_id)
