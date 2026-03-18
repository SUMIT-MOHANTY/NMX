from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Booking(Base):
    """
    Database model for appointment bookings.
    Stores the relationship between users and appointment slots.
    """
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("slots.id"), nullable=False)
    confirmation_code = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="confirmed")  # confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    email_sent = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")

    # Personal data for the booking
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    def __repr__(self):
        return f"<Booking {self.id}: User {self.user_id} for Slot {self.slot_id}>"
