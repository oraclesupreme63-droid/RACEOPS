"""HTTP dependency providers."""

from typing import cast

from fastapi import Request

from raceops.db.health import DatabaseHealthChecker


def get_database_health_checker(request: Request) -> DatabaseHealthChecker:
    """Resolve the database health checker owned by the application."""
    return cast(DatabaseHealthChecker, request.app.state.database_health_checker)
