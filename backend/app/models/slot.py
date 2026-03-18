from datetime import date, time
from typing import List, Optional
from sqlalchemy import Column, Date, Time, SmallInteger, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Session
import uuid

from ..db.session import Base
from .office import Office

class Slot(Base):
    """Model for appointment slots in the database."""

    __tablename__ = "slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=False)
    slot_date = Column(Date, nullable=False)
    slot_time = Column(Time, nullable=False)
    capacity = Column(SmallInteger, nullable=False)
    taken = Column(SmallInteger, nullable=False, default=0)

    # Relationships
    office = relationship("Office", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot")

    # Constraints
    __table_args__ = (
        CheckConstraint("slot_time >= '08:00:00'::time AND slot_time <= '17:00:00'::time",
                       name="check_slot_time_in_working_hours"),
        CheckConstraint("EXTRACT(MINUTE FROM slot_time) IN (0, 30)",
                       name="check_slot_time_interval"),
        CheckConstraint("taken <= capacity",
                       name="check_taken_lte_capacity"),
    )

    @property
    def available(self) -> int:
        """Calculate the number of available slots."""
        return self.capacity - self.taken

    @classmethod
    def available_slots(cls, db: Session, location: Optional[str] = None,
                       date_filter: Optional[date] = None,
                       skip: int = 0, limit: int = 30) -> List["Slot"]:
        """
        Retrieve available slots filtered by city and date.

        Args:
            db: Database session
            location: City name to filter by
            date_filter: Date to filter by
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of available slots
        """
        import logging
        from sqlalchemy import func

        query = db.query(cls).filter(cls.taken < cls.capacity)

        if location:
            logging.info(f"Filtering slots by location: {location}")
            query = query.join(Office).filter(func.lower(Office.city) == func.lower(location))

        if date_filter:
            logging.info(f"Filtering slots by date: {date_filter}")
            query = query.filter(cls.slot_date == date_filter)

        # Order by date and time for consistent results
        query = query.order_by(cls.slot_date, cls.slot_time)

        logging.info(f"Pagination: skip={skip}, limit={limit}")
        return query.offset(skip).limit(limit).all()

    @classmethod
    def count_available_slots(cls, db: Session, location: Optional[str] = None,
                             date_filter: Optional[date] = None) -> int:
        """
        Count the total number of available slots with filters.

        Args:
            db: Database session
            location: City name to filter by
            date_filter: Date to filter by

        Returns:
            Total count of available slots
        """
        from sqlalchemy import func

        query = db.query(func.count(cls.id)).filter(cls.taken < cls.capacity)

        if location:
            query = query.join(Office).filter(func.lower(Office.city) == func.lower(location))

        if date_filter:
            query = query.filter(cls.slot_date == date_filter)

        return query.scalar()
