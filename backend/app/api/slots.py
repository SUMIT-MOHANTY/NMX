import logging
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.slot import Slot
from ..schemas.slot import SlotPaginatedResponse
from ..core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/slots", response_model=SlotPaginatedResponse)
def search_slots(
    location: Optional[str] = None,
    date: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(30, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Search for available appointment slots filtered by city and date.

    Args:
        location: Filter slots by city/location
        date: Filter slots by date (YYYY-MM-DD format)
        page: Pagination page number (starts from 1)
        size: Number of items per page (default 30, max 100)
        db: Database session dependency

    Returns:
        Paginated list of available slots
    """
    logger.info(f"Searching slots with filters: location={location}, date={date}, page={page}, size={size}")

    # Parse date string to date object if provided
    date_filter = None
    if date:
        try:
            date_filter = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {date}")
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

    # Calculate pagination parameters
    skip = (page - 1) * size

    # Get total count for pagination
    total_slots = Slot.count_available_slots(
        db=db, location=location, date_filter=date_filter
    )

    # Get paginated results
    slots = Slot.available_slots(
        db=db, location=location, date_filter=date_filter, skip=skip, limit=size
    )

    # Calculate total pages
    total_pages = (total_slots + size - 1) // size if total_slots > 0 else 0

    logger.info(f"Found {len(slots)} slots (total: {total_slots})")

    return {
        "items": slots,
        "total": total_slots,
        "page": page,
        "size": size,
        "pages": total_pages,
    }
