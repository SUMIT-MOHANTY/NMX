from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    # Validate email format
    @validator('email')
    def email_must_be_valid(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()  # Normalize emails to lowercase

    # Basic password validation
    @validator('password')
    def password_must_be_valid(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ErrorResponse(BaseModel):
    detail: str
