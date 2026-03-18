from datetime import datetime
from pydantic import BaseModel, EmailStr, validator, Field
import re

class UserRegister(BaseModel):
    full_name: str = Field(..., max_length=120)
    email: EmailStr = Field(..., max_length=120)
    mobile: str = Field(..., max_length=20)
    password: str
    confirm_password: str

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Full name is required')
        return v

    @validator('mobile')
    def validate_mobile(cls, v):
        # Simple mobile validation - adjust based on your requirements
        if not re.match(r'^\+?[0-9]{8,15}$', v):
            raise ValueError('Invalid mobile number format')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    mobile: str
    created_at: datetime

    class Config:
        orm_mode = True
