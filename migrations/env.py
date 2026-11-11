"""Alembic environment for the RaceOps PostgreSQL schema."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from raceops.core.config import Settings
from raceops.db.base import Base
from raceops.iam import models as iam_models
from raceops.learning import models as learning_models
from raceops.operations import models as operations_models
from raceops.sessions import models as session_models

_ = iam_models, learning_models, operations_models, session_models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Load the migration URL without exposing it through alembic.ini."""
    return Settings().database_url.get_secret_value()


def configure_context(connection: Connection) -> None:
    """Configure common migration comparison behavior."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations using a short-lived non-pooled connection."""
    settings = Settings()
    connectable = create_engine(
        settings.database_url.get_secret_value(),
        connect_args={
            "connect_timeout": settings.database_connect_timeout_seconds,
        },
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            configure_context(connection)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
