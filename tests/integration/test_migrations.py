"""PostgreSQL round-trip test for the complete Alembic history."""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from raceops.core.config import Settings

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
HEAD_REVISION = "20261109_0004_sessions"


@pytest.mark.integration
@pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
def test_migrations_upgrade_downgrade_and_upgrade() -> None:
    settings = Settings()
    alembic_config = Config("alembic.ini")
    engine = create_engine(
        settings.database_url.get_secret_value(),
        connect_args={
            "connect_timeout": settings.database_connect_timeout_seconds,
        },
    )

    try:
        command.upgrade(alembic_config, "head")
        assert _current_revision(engine) == HEAD_REVISION

        command.downgrade(alembic_config, "base")
        assert _current_revision(engine) is None

        command.upgrade(alembic_config, "head")
        assert _current_revision(engine) == HEAD_REVISION
    finally:
        command.upgrade(alembic_config, "head")
        engine.dispose()


def _current_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
