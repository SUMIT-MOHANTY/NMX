import os
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend API"
    API_V1_STR: str = "/api/v1"

    # JWT Token settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "highly_secure_secret_key_please_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()
