from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, validator

class BookingBase(BaseModel):
    """Base schema for booking data."""
    slot_id: UUID

class BookingCreate(BookingBase):
    """Schema for creating a booking."""
    pass

class BookingResponse(BaseModel):
    """Schema for booking response."""
    id: UUID
    user_id: UUID
    slot_id: UUID
    status: str
    booked_at: datetime
    slot_details: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "slot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status": "confirmed",
                "booked_at": "2023-01-01T12:00:00Z",
                "slot_details": {
                    "slot_date": "2023-01-15",
                    "slot_time": "14:30:00",
                    "office_location": "New York Office"
                }
            }
        }

class BookingInDB(BookingResponse):
    """Schema for booking model stored in DB."""
    pass

class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v not in ['confirmed', 'cancelled']:
            raise ValueError('Status must be either "confirmed" or "cancelled"')
        return v
