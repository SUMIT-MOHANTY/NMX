import os
from pydantic import BaseSettings, validator
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Slot Reservation API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGEME_IN_PRODUCTION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "CHANGEME_IN_PRODUCTION" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be changed in production environment")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
