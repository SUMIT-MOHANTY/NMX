import os
from pydantic import BaseSettings, Field
import secrets
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application settings with secure defaults
    """
    # JWT Settings
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.environ.get("JWT_SECRET_KEY") or secrets.token_hex(32),
        description="Secret key for JWT token signing (auto-generated if not provided)"
    )
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        default=1800,  # 30 minutes
        description="Seconds until access token expires"
    )
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(
        default=604800,  # 7 days
        description="Seconds until refresh token expires"
    )

    # Security Settings
    ENFORCE_HTTPS: bool = Field(
        default=False,
        description="Enforce HTTPS by redirecting HTTP requests"
    )
    CORS_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )

    # Rate Limiting
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Time window in seconds for rate limiting"
    )
    RATE_LIMIT_MAX: int = Field(
        default=30,
        description="Maximum requests per window for rate limiting"
    )

    # Server Settings
    PORT: int = Field(
        default=8000,
        description="Port to run the application on"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )

    # Database Settings
    # Add database settings as needed

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Warn if JWT_SECRET_KEY is auto-generated
if "JWT_SECRET_KEY" not in os.environ:
    logger.warning(
        "JWT_SECRET_KEY not provided in environment! Using auto-generated key. "
        "This is insecure for production environments."
    )
