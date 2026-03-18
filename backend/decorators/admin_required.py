from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging
from datetime import datetime
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
security = HTTPBearer()

def admin_required():
    """
    Dependency to check if the user has admin role.
    This decorator extracts the JWT token from the request,
    verifies the user has role="admin" in the token payload,
    and returns 403 if not an admin.
    """
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            # Get token from Authorization header
            token = credentials.credentials

            # Decode token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # Extract user role
            role = payload.get("role", "user")

            # Check if user has admin role
            if role != "admin":
                logger.warning(f"Non-admin access attempt at {datetime.now().isoformat()} - User ID: {payload.get('sub')}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )

            # Return payload for potential later use
            return payload

        except jwt.PyJWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    return Depends(dependency)
