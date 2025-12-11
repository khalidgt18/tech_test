from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "sqlite:///./tickets.db"

    # API
    api_title: str = "Ticket Management API"
    api_version: str = "1.0.0"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
