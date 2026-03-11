"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Security
    API_KEY: str = ""

    # CORS (comma-separated string)
    ALLOWED_ORIGINS: str = "http://localhost:5173,https://your-frontend.vercel.app"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # LLM Provider Configuration
    LLM_PROVIDER: Literal["gemini", "groq"] = "gemini"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-70b-8192"

    # Email Provider Configuration
    EMAIL_PROVIDER: Literal["sendgrid", "resend"] = "sendgrid"
    SENDGRID_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "insights@rabbittai.com"

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 10

    # Rate Limiting
    RATE_LIMIT: str = "10/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()
