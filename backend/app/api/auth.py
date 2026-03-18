from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.schemas.auth import UserRegister, UserResponse
from backend.app.services.auth import AuthService
from backend.app.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint validates the user data, creates a new user record
    with a securely hashed password, and returns the created user.
    """
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        new_user = AuthService.register_user(db, user_data)

        # Convert the user object to a response
        return {
            "id": str(new_user.id),
            "full_name": new_user.full_name,
            "email": new_user.email,
            "mobile": new_user.mobile,
            "created_at": new_user.created_at
        }

    except ValueError as e:
        error_message = str(e)
        if "Email already registered" in error_message:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        else:
            logger.warning(f"Registration failed - validation error: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
