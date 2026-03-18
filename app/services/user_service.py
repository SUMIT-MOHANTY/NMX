from typing import Optional, Dict, Any, List
import logging
import hashlib
import os
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class User(BaseModel):
    id: str
    email: str
    password_hash: str
    is_active: bool = True

class UserService:
    def __init__(self):
        # In-memory user database for demo - in production, use a real database
        self.users = {}

        # Add a test user
        self._create_test_user()

    def _create_test_user(self):
        # For testing only - create a sample user
        email = "test@example.com"
        password = "securepassword123"
        user_id = "1"

        # Hash the password (use a secure method in production)
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        ).hex() + ":" + salt.hex()

        self.users[user_id] = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            is_active=True
        )

        logger.info(f"Test user created: {email}")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email (case insensitive)
        """
        try:
            email = email.lower()
            for user in self.users.values():
                if user.email.lower() == email:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        """
        try:
            return self.users.get(user_id)
        except Exception as e:
            logger.error(f"Error finding user by ID: {str(e)}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        """
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None

            # Verify password
            stored_password = user.password_hash
            if ":" not in stored_password:
                logger.error(f"Invalid password hash format for user: {email}")
                return None

            hash_part, salt_part = stored_password.split(":", 1)
            salt = bytes.fromhex(salt_part)

            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            ).hex()

            if password_hash != hash_part:
                logger.warning(f"Failed password verification for user: {email}")
                return None

            return user
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

# Create a singleton instance
user_service = UserService()
