from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

def authenticate_user(db: Session, login_data: LoginRequest) -> User:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        raise AuthenticationError("Invalid email or password")

    if not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user

def create_user_token(user: User) -> TokenResponse:
    """Create a token for an authenticated user."""
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }

    token = create_access_token(token_data)

    return TokenResponse(
        token=token,
        user_id=str(user.id),
        role=user.role
    )
