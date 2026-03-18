import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Booking(Base):
    """
    Database model for a booking made by a user for a specific slot.
    """
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("slots.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    booked_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'slot_id', name='uix_user_slot'),
        CheckConstraint("status IN ('confirmed', 'cancelled')", name='valid_status_check'),
    )

    def __repr__(self):
        return f"<Booking id={self.id} user_id={self.user_id} slot_id={self.slot_id} status={self.status}>"
