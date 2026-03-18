from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
import uuid
from typing import Optional
import logging

from app.db.base_class import Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def get_by_email(cls, db_session, email: str) -> Optional["User"]:
        """Get user by email with error handling."""
        try:
            return db_session.query(cls).filter(cls.email == email).first()
        except Exception as e:
            logger.error(f"Database error when getting user by email: {e}")
            return None

    @classmethod
    def create(cls, db_session, **kwargs) -> Optional["User"]:
        """Create new user with error handling."""
        try:
            db_obj = cls(**kwargs)
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
            return db_obj
        except Exception as e:
            db_session.rollback()
            logger.error(f"Database error when creating user: {e}")
            return None
