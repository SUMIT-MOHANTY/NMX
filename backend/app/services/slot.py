from typing import List, Tuple, Optional
from datetime import date
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.slot import Slot
from app.models.office import Office

class SlotService:
    def __init__(self, db: Session):
        self.db = db

    def get_available_slots(
        self,
        location: Optional[str] = None,
        date: Optional[date] = None,
        page: int = 1,
        size: int = 30
    ) -> Tuple[List[dict], int]:
        """
        Get available slots filtered by location and date with pagination.
        Only returns slots that have available capacity (available > 0).

        Args:
            location: Office location to filter by
            date: Date to filter slots by
            page: Page number (1-indexed)
            size: Number of items per page

        Returns:
            Tuple of (list of slot dictionaries, total count)
        """
        # Start with base query joining slots with offices
        query = self.db.query(
            Slot.id,
            Slot.office_id,
            Slot.slot_date,
            Slot.slot_time,
            Slot.capacity,
            Slot.taken,
            (Slot.capacity - Slot.taken).label('available')
        ).join(Office, Slot.office_id == Office.id)

        # Apply filters
        query = query.filter(Slot.capacity > Slot.taken)  # Only show slots with availability

        if location:
            query = query.filter(func.lower(Office.location).contains(func.lower(location)))

        if date:
            query = query.filter(Slot.slot_date == date)

        # Get total count for pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(Slot.slot_date, Slot.slot_time).offset(offset).limit(size)

        # Execute query and convert to dictionaries
        result = query.all()
        slots = [
            {
                "id": str(row.id),
                "office_id": str(row.office_id),
                "slot_date": row.slot_date.isoformat(),
                "slot_time": str(row.slot_time),
                "capacity": row.capacity,
                "taken": row.taken,
                "available": row.available
            }
            for row in result
        ]

        return slots, total
