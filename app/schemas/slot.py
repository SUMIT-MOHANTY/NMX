from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator, Field

class SlotReservationRequest(BaseModel):
    slot_id: int = Field(..., gt=0)
    reservation_date: Optional[datetime] = None

    @validator('slot_id')
    def validate_slot_id(cls, v):
        if v <= 0:
            raise ValueError('Slot ID must be a positive integer')
        return v

    @validator('reservation_date')
    def validate_reservation_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('Reservation date cannot be in the past')
        return v

class SlotReservationResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    reserved_at: datetime
    status: str
