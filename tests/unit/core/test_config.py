"""Tests for typed application configuration."""

import os
from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from raceops.core.config import (
    COMPOSE_DEVELOPMENT_DATABASE_URL,
    DEFAULT_DATABASE_URL,
    DEFAULT_JWT_SECRET,
    EXAMPLE_JWT_SECRET,
    Settings,
)


@pytest.fixture(autouse=True)
def isolate_raceops_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep configuration tests independent from the runner environment."""
    for variable_name in tuple(os.environ):
        if variable_name.startswith("RACEOPS_"):
            monkeypatch.delenv(variable_name, raising=False)


def test_local_settings_have_documented_development_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.env == "local"
    assert settings.database_url.get_secret_value() == DEFAULT_DATABASE_URL
    assert settings.database_connect_timeout_seconds == 3
    assert settings.jwt_secret.get_secret_value() == DEFAULT_JWT_SECRET
    assert settings.access_token_ttl_minutes == 15
    assert settings.cors_origins == ["http://localhost:3000"]


def test_environment_variables_use_raceops_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RACEOPS_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("RACEOPS_ACCESS_TOKEN_TTL_MINUTES", "30")

    settings = Settings()

    assert settings.log_level == "WARNING"
    assert settings.access_token_ttl_minutes == 30


def test_production_rejects_known_development_secrets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError, match="production requires secure values"):
        Settings(env="production")


@pytest.mark.parametrize(
    ("database_url", "jwt_secret"),
    [
        (
            "postgresql+psycopg://user:secure-password@database:5432/raceops",
            EXAMPLE_JWT_SECRET,
        ),
        (
            "postgresql+psycopg://user:secure-password@database:5432/raceops",
            "too-short",
        ),
        (
            COMPOSE_DEVELOPMENT_DATABASE_URL,
            "a-production-jwt-secret-with-at-least-32-characters",
        ),
    ],
)
def test_production_rejects_example_or_weak_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    database_url: str,
    jwt_secret: str,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError, match="production requires secure values"):
        Settings(
            env="production",
            database_url=SecretStr(database_url),
            jwt_secret=SecretStr(jwt_secret),
        )


def test_production_accepts_external_non_placeholder_secrets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    settings = Settings(
        env="production",
        database_url=SecretStr(
            "postgresql+psycopg://user:secure-password@database:5432/raceops"
        ),
        jwt_secret=SecretStr("a-production-jwt-secret-with-at-least-32-characters"),
    )

    assert settings.env == "production"
