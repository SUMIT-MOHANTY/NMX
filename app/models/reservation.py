from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reservation_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="confirmed", nullable=False)

    # Relationships
    user = relationship("User", back_populates="reservations")
    slot = relationship("Slot", back_populates="reservations")
