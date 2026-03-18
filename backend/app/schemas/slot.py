from datetime import date, time
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from datetime import datetime

class SlotBase(BaseModel):
    """Base schema for slot data."""
    office_id: UUID
    slot_date: date
    slot_time: time
    capacity: int = Field(..., gt=0)

    @validator('slot_time')
    def validate_slot_time(cls, v):
        """Validate that slot time is between 8:00-17:00 and at 30-minute intervals."""
        if v < time(8, 0) or v > time(17, 0):
            raise ValueError("Slot time must be between 08:00 and 17:00")

        if v.minute not in (0, 30):
            raise ValueError("Slot time must be at 30-minute intervals (00 or 30 minutes)")

        return v

class SlotCreate(SlotBase):
    """Schema for creating a new slot."""
    pass

class SlotInDB(SlotBase):
    """Schema for slot data from the database."""
    id: UUID
    taken: int = 0

    class Config:
        orm_mode = True

class SlotResponse(SlotInDB):
    """Schema for slot response with additional available property."""
    available: int

    class Config:
        orm_mode = True

class SlotPaginatedResponse(BaseModel):
    """Schema for paginated slot results."""
    items: List[SlotResponse]
    total: int
    page: int
    size: int
    pages: int

class SlotSearch(BaseModel):
    """Schema for slot search parameters."""
    location: Optional[str] = None
    date: Optional[date] = None
    page: int = Field(1, ge=1)
    size: int = Field(30, ge=1, le=100)
