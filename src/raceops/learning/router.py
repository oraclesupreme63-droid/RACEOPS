"""HTTP boundary for technical Observations."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.learning.schemas import (
    ObservationCreateRequest,
    ObservationPageResponse,
    ObservationResponse,
    ObservationUpdateRequest,
)
from raceops.learning.services import (
    create_observation,
    get_observation,
    list_observations,
    update_observation,
)

logger = logging.getLogger("raceops.observations")
router = APIRouter()

read_observations = require_permission(Permission.READ_OBSERVATIONS)
write_observations = require_permission(Permission.WRITE_OBSERVATIONS)

OBSERVATION_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Observation not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/observations",
    tags=["observations"],
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses=OBSERVATION_COMMON_RESPONSES,
)
def create_observation_endpoint(
    payload: ObservationCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_observations)],
) -> ObservationResponse:
    """Record evidence without introducing any causal assertion."""
    observation = create_observation(
        session,
        actor,
        session_id=payload.session_id,
        vehicle_id=payload.vehicle_id,
        description=payload.description,
        category=payload.category,
        visibility_level=payload.visibility_level,
    )
    logger.info(
        "observation created",
        extra={
            "event": "observation.created",
            "observation_id": str(observation.observation_id),
            "team_id": str(actor.team_id),
            "visibility_level": observation.visibility_level.value,
        },
    )
    return ObservationResponse.from_model(observation)


@router.get(
    "/observations",
    tags=["observations"],
    response_model=ObservationPageResponse,
    responses=OBSERVATION_COMMON_RESPONSES,
)
def list_observations_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_observations)],
    session_id: UUID | None = None,
    vehicle_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ObservationPageResponse:
    """Return a page after visibility filtering and optional context filters."""
    observations, total = list_observations(
        session,
        actor,
        session_id=session_id,
        vehicle_id=vehicle_id,
        limit=limit,
        offset=offset,
    )
    return ObservationPageResponse(
        items=[ObservationResponse.from_model(item) for item in observations],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/observations/{observation_id}",
    tags=["observations"],
    response_model=ObservationResponse,
    responses=OBSERVATION_COMMON_RESPONSES,
)
def get_observation_endpoint(
    observation_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_observations)],
) -> ObservationResponse:
    """Read one Observation only when its visibility permits it."""
    return ObservationResponse.from_model(
        get_observation(session, actor, observation_id)
    )


@router.patch(
    "/observations/{observation_id}",
    tags=["observations"],
    response_model=ObservationResponse,
    responses=OBSERVATION_COMMON_RESPONSES,
)
def update_observation_endpoint(
    observation_id: UUID,
    payload: ObservationUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_observations)],
) -> ObservationResponse:
    """Correct visible evidence text without changing protected metadata."""
    observation = update_observation(
        session,
        actor,
        observation_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return ObservationResponse.from_model(observation)
