"""SQLAlchemy engine and session-factory construction."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from raceops.core.config import Settings


def build_engine(settings: Settings) -> Engine:
    """Create the process-level engine without opening a connection."""
    return create_engine(
        settings.database_url.get_secret_value(),
        connect_args={
            "connect_timeout": settings.database_connect_timeout_seconds,
        },
        pool_pre_ping=True,
    )


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the factory that will provide one Session per use case."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
