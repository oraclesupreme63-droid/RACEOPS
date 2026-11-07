"""HTTP contract tests for the dependency readiness endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from raceops import __version__
from raceops.api.dependencies import get_database_health_checker
from raceops.db.health import DatabaseUnavailableError
from raceops.main import create_app


class PassingDatabaseHealthChecker:
    """Test double representing an available PostgreSQL dependency."""

    def check(self) -> None:
        pass


class FailingDatabaseHealthChecker:
    """Test double representing an unavailable PostgreSQL dependency."""

    def check(self) -> None:
        raise DatabaseUnavailableError


@pytest.mark.anyio
async def test_ready_returns_200_when_database_is_available() -> None:
    application = create_app()
    application.dependency_overrides[get_database_health_checker] = (
        PassingDatabaseHealthChecker
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "raceops-api",
        "database": "up",
        "version": __version__,
    }


@pytest.mark.anyio
async def test_ready_returns_503_when_database_is_unavailable() -> None:
    application = create_app()
    application.dependency_overrides[get_database_health_checker] = (
        FailingDatabaseHealthChecker
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "service": "raceops-api",
        "database": "down",
        "version": __version__,
    }
