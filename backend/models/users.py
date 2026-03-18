from sqlalchemy import Column, String, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    mobile = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum("user", "admin", name="user_roles"), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
