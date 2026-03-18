from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.models.slot import Slot
from app.models.office import Office
from app.schemas.slot import SlotResponse, PaginatedSlotResponse
from app.services.slot import SlotService

router = APIRouter()

@router.get("/", response_model=PaginatedSlotResponse)
def get_available_slots(
    location: Optional[str] = None,
    date: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for available appointment slots filtered by location and date.
    Returns only slots with remaining capacity (available > 0).
    """
    slot_service = SlotService(db)

    # Get slots with pagination
    slots, total = slot_service.get_available_slots(
        location=location,
        date=date,
        page=page,
        size=size
    )

    # Calculate pagination metadata
    pages = (total + size - 1) // size if size > 0 else 0

    return {
        "items": slots,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }
