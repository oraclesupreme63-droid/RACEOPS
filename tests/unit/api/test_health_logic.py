"""Network-free tests for health and readiness behavior."""

from starlette.responses import Response

from raceops import __version__
from raceops.api.health import get_health, get_readiness
from raceops.db.health import DatabaseUnavailableError


class PassingDatabaseHealthChecker:
    """Test double representing an available database."""

    def check(self) -> None:
        pass


class FailingDatabaseHealthChecker:
    """Test double representing an unavailable database."""

    def check(self) -> None:
        raise DatabaseUnavailableError


def test_health_logic_does_not_depend_on_database() -> None:
    result = get_health()

    assert result.model_dump() == {
        "status": "ok",
        "service": "raceops-api",
        "version": __version__,
    }


def test_readiness_logic_reports_available_database() -> None:
    response = Response()

    result = get_readiness(response, PassingDatabaseHealthChecker())

    assert response.status_code == 200
    assert result.model_dump() == {
        "status": "ready",
        "service": "raceops-api",
        "database": "up",
        "version": __version__,
    }


def test_readiness_logic_reports_unavailable_database() -> None:
    response = Response()

    result = get_readiness(response, FailingDatabaseHealthChecker())

    assert response.status_code == 503
    assert result.model_dump() == {
        "status": "unavailable",
        "service": "raceops-api",
        "database": "down",
        "version": __version__,
    }
