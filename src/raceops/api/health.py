"""Process health endpoint."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from raceops import __version__
from raceops.api.dependencies import get_database_health_checker
from raceops.db.health import DatabaseHealthChecker, DatabaseUnavailableError

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    """Stable response contract for the liveness endpoint."""

    status: Literal["ok"]
    service: Literal["raceops-api"]
    version: str


class ReadinessResponse(BaseModel):
    """Stable response contract for the dependency readiness endpoint."""

    status: Literal["ready", "unavailable"]
    service: Literal["raceops-api"]
    database: Literal["up", "down"]
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API process health",
    description="Confirms that the RaceOps API process can serve requests.",
)
def get_health() -> HealthResponse:
    """Return process liveness without checking external dependencies."""
    return HealthResponse(
        status="ok",
        service="raceops-api",
        version=__version__,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ReadinessResponse,
            "description": "PostgreSQL is unavailable.",
        }
    },
    summary="Check API dependency readiness",
    description="Confirms that PostgreSQL can serve a minimal query.",
)
def get_readiness(
    response: Response,
    checker: Annotated[
        DatabaseHealthChecker,
        Depends(get_database_health_checker),
    ],
) -> ReadinessResponse:
    """Return whether the API has the dependencies required for traffic."""
    try:
        checker.check()
    except DatabaseUnavailableError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unavailable",
            service="raceops-api",
            database="down",
            version=__version__,
        )

    return ReadinessResponse(
        status="ready",
        service="raceops-api",
        database="up",
        version=__version__,
    )
