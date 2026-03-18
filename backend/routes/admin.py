from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid
import logging
from datetime import date, time, datetime
from app.db.session import get_db
from backend.decorators.admin_required import admin_required
from app.models.slot import Slot
from app.models.booking import Booking

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

# Pydantic models
class SlotCreate(BaseModel):
    office_id: uuid.UUID
    slot_date: date
    slot_time: time
    capacity: int = Field(gt=0)

class SlotResponse(BaseModel):
    id: uuid.UUID
    office_id: uuid.UUID
    slot_date: date
    slot_time: time
    capacity: int
    created_at: datetime

class SlotsCreateResponse(BaseModel):
    created: int
    slots: List[SlotResponse]

@router.post("/slots", response_model=SlotsCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_slots(
    slots: List[SlotCreate],
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required())
):
    """
    Create multiple appointment slots.
    Only accessible to administrators.
    """
    logger.info(f"Admin creating {len(slots)} slots")

    created_slots = []

    for slot_data in slots:
        # Check if slot already exists for the same office, date and time
        existing_slot = db.query(Slot).filter(
            Slot.office_id == slot_data.office_id,
            Slot.slot_date == slot_data.slot_date,
            Slot.slot_time == slot_data.slot_time
        ).first()

        if existing_slot:
            logger.warning(f"Slot already exists for office {slot_data.office_id} on {slot_data.slot_date} at {slot_data.slot_time}")
            continue

        # Create new slot
        new_slot = Slot(
            office_id=slot_data.office_id,
            slot_date=slot_data.slot_date,
            slot_time=slot_data.slot_time,
            capacity=slot_data.capacity
        )

        db.add(new_slot)
        created_slots.append(new_slot)

    # Commit all changes to database
    db.commit()

    # Refresh all slots to get their IDs
    for slot in created_slots:
        db.refresh(slot)

    # Create response
    response_slots = [
        SlotResponse(
            id=slot.id,
            office_id=slot.office_id,
            slot_date=slot.slot_date,
            slot_time=slot.slot_time,
            capacity=slot.capacity,
            created_at=slot.created_at
        ) for slot in created_slots
    ]

    logger.info(f"Successfully created {len(created_slots)} slots")
    return SlotsCreateResponse(created=len(created_slots), slots=response_slots)

@router.delete("/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required())
):
    """
    Delete an appointment slot by ID.
    Only accessible to administrators.
    Cannot delete slots that have existing bookings.
    """
    logger.info(f"Admin attempting to delete slot {slot_id}")

    # Check if slot exists
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        logger.warning(f"Slot {slot_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    # Check if slot has any bookings
    bookings_count = db.query(Booking).filter(Booking.slot_id == slot_id).count()
    if bookings_count > 0:
        logger.warning(f"Cannot delete slot {slot_id} with {bookings_count} existing bookings")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete slot that has existing bookings"
        )

    # Delete the slot
    db.delete(slot)
    db.commit()

    logger.info(f"Successfully deleted slot {slot_id}")
    return None
