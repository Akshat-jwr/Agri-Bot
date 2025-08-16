from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

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

    # Configure environment file using pydantic-settings
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(',') if o.strip()]

settings = Settings()
