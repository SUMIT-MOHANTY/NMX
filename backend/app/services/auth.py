import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from backend.app.schemas.auth import UserRegister

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister):
        """
        Register a new user in the system.

        Args:
            db: Database session
            user_data: Validated user registration data

        Returns:
            Newly created user object or None if registration fails

        Raises:
            ValueError: If email is already registered
        """
        try:
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {user_data.email}")
                raise ValueError("Email already registered")

            # Create new user
            new_user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                mobile=user_data.mobile,
                role="user"
            )
            new_user.set_password(user_data.password)

            # Save to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            logger.info(f"New user registered successfully: {new_user.id}")
            return new_user

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error during registration: {str(e)}")
            raise ValueError("Email already registered")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during user registration: {str(e)}")
            raise
