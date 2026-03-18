import os
import time
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

class JWTHandler:
    def __init__(self):
        # Get JWT secret from environment variable, or use a secure default for development
        self.secret = os.getenv("JWT_SECRET_KEY")
        if not self.secret:
            logger.warning("JWT_SECRET_KEY not set in environment! Using insecure default for development only.")
            self.secret = "insecure_development_key_change_in_production"

        # Get JWT expiration time from environment, default to 30 minutes
        try:
            self.access_token_expires = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "1800"))  # 30 minutes
            self.refresh_token_expires = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))  # 7 days
        except ValueError:
            logger.error("Invalid JWT expiration time in environment, using defaults")
            self.access_token_expires = 1800
            self.refresh_token_expires = 604800

        self.algorithm = "HS256"
        self.security = HTTPBearer()

    def create_access_token(self, user_id: str) -> str:
        """
        Create JWT access token for a user
        """
        payload = {
            "user_id": user_id,
            "type": "access_token",
            "exp": time.time() + self.access_token_expires,
            "iat": time.time()
        }

        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            logger.info(f"Access token created for user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not create access token")

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token for a user
        """
        payload = {
            "user_id": user_id,
            "type": "refresh_token",
            "exp": time.time() + self.refresh_token_expires,
            "iat": time.time()
        }

        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            logger.info(f"Refresh token created for user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not create refresh token")

    def decode_token(self, token: str) -> Dict:
        """
        Decode and validate a JWT token
        """
        try:
            decoded_token = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            # Check if token has expired
            if decoded_token["exp"] < time.time():
                logger.warning(f"Expired token used: {decoded_token.get('user_id', 'unknown')}")
                raise HTTPException(status_code=401, detail="Token expired")

            return decoded_token
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Dict:
        """
        Wrapper for token authentication to use as a dependency
        """
        return self.decode_token(auth.credentials)

    def get_current_user_id(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> str:
        """
        Extract the user ID from a valid JWT token
        """
        decoded = self.decode_token(auth.credentials)
        return decoded["user_id"]

# Create a singleton instance
jwt_handler = JWTHandler()
