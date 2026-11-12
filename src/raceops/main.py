"""FastAPI application factory and default ASGI application."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from raceops import __version__
from raceops.api.errors import register_exception_handlers
from raceops.api.health import router as health_router
from raceops.api.middleware import RequestContextMiddleware
from raceops.api.router import api_router
from raceops.core.config import Settings, get_settings
from raceops.core.logging import configure_logging
from raceops.db.health import SqlAlchemyDatabaseHealthChecker
from raceops.db.session import build_engine, build_session_factory
from raceops.web_client import router as web_client_router

logger = logging.getLogger("raceops.lifecycle")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a configured RaceOps FastAPI application."""
    application_settings = settings or get_settings()
    configure_logging(
        level=application_settings.log_level,
        environment=application_settings.env,
    )
    engine = build_engine(application_settings)
    session_factory = build_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "RaceOps application started",
            extra={"event": "application_started"},
        )
        try:
            yield
        finally:
            engine.dispose()
            logger.info(
                "RaceOps application stopped",
                extra={"event": "application_stopped"},
            )

    application = FastAPI(
        title="RaceOps API",
        summary="Motorsport team operations and performance API.",
        version=__version__,
        lifespan=lifespan,
    )
    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    register_exception_handlers(application)
    application.state.settings = application_settings
    application.state.db_engine = engine
    application.state.db_session_factory = session_factory
    application.state.database_health_checker = SqlAlchemyDatabaseHealthChecker(engine)
    application.include_router(health_router)
    application.include_router(api_router)
    application.include_router(web_client_router)
    return application


app = create_app()
