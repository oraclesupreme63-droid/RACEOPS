"""Database readiness checks."""

from typing import Protocol

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


class DatabaseUnavailableError(RuntimeError):
    """Raised when PostgreSQL cannot serve the readiness probe."""


class DatabaseHealthChecker(Protocol):
    """Port used by the HTTP layer to verify database readiness."""

    def check(self) -> None:
        """Raise DatabaseUnavailableError when the database is unavailable."""
        ...


class SqlAlchemyDatabaseHealthChecker:
    """PostgreSQL readiness check backed by a SQLAlchemy engine."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def check(self) -> None:
        """Open a short connection and execute a side-effect-free query."""
        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            raise DatabaseUnavailableError from error
