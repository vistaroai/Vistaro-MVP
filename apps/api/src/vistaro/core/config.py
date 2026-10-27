"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings shared by the API and workers."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    web_origin: str = "http://localhost:5173"
    api_base_url: str = "http://127.0.0.1:8000"
    database_url: str = "postgresql://vistaro:vistaro_local_only@localhost:5432/vistaro"
    migrator_database_url: str = "postgresql://vistaro:vistaro_local_only@localhost:5432/vistaro"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_requests: int = Field(default=120, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    # AUTH-001: sessions and emails.
    session_lifetime_seconds: int = Field(default=604800, ge=60)
    verification_token_ttl_seconds: int = Field(default=86400, ge=60)
    email_from: str = "Vistaro <no-reply@vistaro.local>"
    smtp_host: str = "localhost"
    smtp_port: int = Field(default=1025, ge=1)
    resend_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()


settings = get_settings()
