from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field

class PersonalData(BaseModel):
    """Schema for personal data provided during booking"""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    mobile: str = Field(..., min_length=5, max_length=20)

    @validator('mobile')
    def validate_mobile(cls, v):
        # Simple validation to ensure mobile has at least digits
        if not any(char.isdigit() for char in v):
            raise ValueError('Mobile number must contain at least one digit')
        return v

class BookingCreate(BaseModel):
    """Schema for creating a booking"""
    user_id: uuid.UUID
    slot_id: uuid.UUID
    personal_data: PersonalData

class BookingInDB(BaseModel):
    """Schema for booking stored in the database"""
    id: uuid.UUID
    user_id: uuid.UUID
    slot_id: uuid.UUID
    confirmation_code: str
    status: str
    created_at: datetime
    updated_at: datetime
    email_sent: bool
    full_name: str
    email: EmailStr
    mobile: str

    class Config:
        orm_mode = True

class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: uuid.UUID
    user_id: uuid.UUID
    slot_id: uuid.UUID
    booking_time: datetime
    status: str
    confirmation_code: str

    class Config:
        orm_mode = True
