"""Typed application settings loaded from the environment."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://raceops:raceops@localhost:55432/raceops"
DEFAULT_JWT_SECRET = "local-development-only-change-me"


class Settings(BaseSettings):
    """RaceOps configuration with safe production validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RACEOPS_",
        extra="ignore",
        frozen=True,
    )

    env: Literal["local", "test", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr = SecretStr(DEFAULT_DATABASE_URL)
    database_connect_timeout_seconds: int = Field(default=3, ge=1, le=30)
    jwt_secret: SecretStr = SecretStr(DEFAULT_JWT_SECRET)
    access_token_ttl_minutes: int = Field(default=15, ge=5, le=60)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @model_validator(mode="after")
    def reject_development_secrets_in_production(self) -> Self:
        """Prevent known development credentials from reaching production."""
        if self.env != "production":
            return self

        unsafe_fields: list[str] = []
        if self.database_url.get_secret_value() == DEFAULT_DATABASE_URL:
            unsafe_fields.append("RACEOPS_DATABASE_URL")
        if self.jwt_secret.get_secret_value() == DEFAULT_JWT_SECRET:
            unsafe_fields.append("RACEOPS_JWT_SECRET")

        if unsafe_fields:
            fields = ", ".join(unsafe_fields)
            raise ValueError(f"production requires secure values for: {fields}")

        return self


@lru_cache
def get_settings() -> Settings:
    """Return one immutable-by-convention settings instance per process."""
    return Settings()
