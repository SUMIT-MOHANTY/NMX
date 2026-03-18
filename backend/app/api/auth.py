from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging

from ..core.security import create_access_token, verify_password
from ..core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock user database - replace with actual database in production
MOCK_USER_DB = {
    "testuser@example.com": {
        "email": "testuser@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "is_active": True,
    }
}

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str  # Using username to maintain OAuth2 compatibility (can be email)
    password: str

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        # Authenticate the user
        user = MOCK_USER_DB.get(form_data.username)
        if not user:
            logger.warning(f"Login attempt failed for non-existent user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(form_data.password, user["hashed_password"]):
            logger.warning(f"Invalid password attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user["is_active"]:
            logger.warning(f"Login attempt by inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user["email"], expires_delta=access_token_expires
        )

        logger.info(f"User successfully logged in: {form_data.username}")
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions to maintain status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
