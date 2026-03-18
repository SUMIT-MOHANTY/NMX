from datetime import timedelta
from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, SECRET_KEY, ALGORITHM
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.db.session import get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    try:
        user = User.get_by_email(db, email=email)
        if not user:
            logger.warning(f"Authentication failed: User not found for email {email}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

def create_user_token(user_id: int) -> dict:
    """Create token for user"""
    try:
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Missing user_id in token payload")
            raise credentials_exception
        token_data = TokenPayload(sub=int(user_id))
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        logger.warning(f"User not found for id {token_data.sub}")
        raise credentials_exception
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.email}")
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
