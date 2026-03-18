from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from fastapi.security import HTTPBearer
from typing import Dict, Optional
import logging
from datetime import datetime

from app.models.auth import LoginRequest, TokenResponse, RefreshTokenRequest, ErrorResponse
from app.auth.jwt_handler import jwt_handler
from app.services.user_service import user_service

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)

security = HTTPBearer()

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: Request, login_data: LoginRequest):
    """
    Authenticate a user and return JWT tokens
    """
    try:
        # Log the login attempt (without password)
        logger.info(f"Login attempt for user: {login_data.email} from IP: {request.client.host if request.client else 'unknown'}")

        # Verify user credentials
        user = await user_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate tokens
        access_token = jwt_handler.create_access_token(str(user.id))
        refresh_token = jwt_handler.create_refresh_token(str(user.id))

        # Log successful login
        logger.info(f"Successful login for user: {login_data.email}")

        # Return tokens
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error occurred"
        )

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, refresh_data: RefreshTokenRequest):
    """
    Issue a new access token using a valid refresh token
    """
    try:
        # Decode refresh token
        decoded = jwt_handler.decode_token(refresh_data.refresh_token)

        # Verify it's a refresh token
        if decoded.get("type") != "refresh_token":
            logger.warning(f"Invalid token type used for refresh: {decoded.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = decoded.get("user_id")
        if not user_id:
            logger.warning("Refresh token missing user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if user still exists and is active
        user = await user_service.get_user_by_id(user_id)
        if not user:
            logger.warning(f"Refresh token used for deleted user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists"
            )

        if not user.is_active:
            logger.warning(f"Refresh token used for inactive user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Generate new tokens
        access_token = jwt_handler.create_access_token(user_id)
        refresh_token = jwt_handler.create_refresh_token(user_id)

        # Log token refresh
        logger.info(f"Tokens refreshed for user: {user_id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, auth: Dict = Depends(jwt_handler.auth_wrapper)):
    """
    Logout a user (client should discard tokens)
    """
    try:
        user_id = auth.get("user_id")
        logger.info(f"User logged out: {user_id}")

        # In a more comprehensive implementation, we would invalidate the token
        # This would require a token blacklist or database of revoked tokens

        return {"detail": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_token(auth: Dict = Depends(jwt_handler.auth_wrapper)):
    """
    Verify if the token is valid
    """
    return {"detail": "Token is valid", "user_id": auth.get("user_id")}
