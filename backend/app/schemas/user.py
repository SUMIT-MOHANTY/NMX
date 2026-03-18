from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str

    @validator('mobile')
    def validate_mobile(cls, v):
        # Basic mobile number validation (adjust pattern as needed for country format)
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid mobile number format')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('password')
    def validate_password(cls, v):
        # Password strength validation
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class UserInDB(UserBase):
    id: UUID
    hashed_password: str
    role: str = "user"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
