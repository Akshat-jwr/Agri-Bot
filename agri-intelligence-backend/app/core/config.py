from typing import List,Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Agricultural Intelligence API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database (required; set in .env)
    DATABASE_URL: str
    
    # Security (required; set in .env)
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # CORS origins (required; set in .env as comma-separated string)
    ALLOWED_ORIGINS: str
    
    # Email (required; set in .env)
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str

    jina_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    agmarknet_api_key: Optional[str] = None
    imd_api_key: Optional[str] = None
    isro_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None  # 🆕 Add this too
    google_search_engine_id: Optional[str] = None  # 🆕 And this

    # Configure environment file using pydantic-settings
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=False  # Allow case-insensitive matching
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(',') if o.strip()]

settings = Settings()
