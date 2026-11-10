"""HTTP boundary for Session planning resources."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.errors import (
    SessionAssignmentConflictError,
    SessionNotEditableError,
)
from raceops.sessions.schemas import (
    SessionCreateRequest,
    SessionPageResponse,
    SessionResponse,
    SessionUpdateRequest,
)
from raceops.sessions.services import (
    create_race_session,
    get_race_session,
    list_race_sessions,
    update_race_session,
)

logger = logging.getLogger("raceops.sessions")
router = APIRouter()

read_sessions = require_permission(Permission.READ_SESSIONS)
write_sessions = require_permission(Permission.WRITE_SESSIONS)

SESSION_ASSIGNMENT_CONFLICT_PROBLEM = ProblemDefinition(
    "session-assignment-conflict",
    "Session assignment conflict",
    "session_assignment_conflict",
    "The selected Driver or Vehicle is not eligible for this Session.",
)
SESSION_NOT_EDITABLE_PROBLEM = ProblemDefinition(
    "session-not-editable",
    "Session is not editable",
    "session_not_editable",
    "Only a planned Session may be edited.",
)

SESSION_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Session or assignment not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/sessions",
    tags=["sessions"],
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a planned Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Assignment conflict."},
    },
)
def create_session_endpoint(
    payload: SessionCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Create a Session after atomic same-Team assignment validation."""
    try:
        race_session = create_race_session(
            session,
            actor,
            event_id=payload.event_id,
            driver_id=payload.driver_id,
            vehicle_id=payload.vehicle_id,
            session_type=payload.session_type,
            scheduled_at=payload.scheduled_at,
        )
    except SessionAssignmentConflictError as error:
        raise _session_assignment_conflict() from error
    logger.info(
        "session created",
        extra={
            "event": "session.created",
            "session_id": str(race_session.session_id),
            "team_id": str(actor.team_id),
        },
    )
    return SessionResponse.from_model(race_session)


@router.get(
    "/sessions",
    tags=["sessions"],
    response_model=SessionPageResponse,
    summary="List authorized Sessions",
    responses=SESSION_COMMON_RESPONSES,
)
def list_sessions_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_sessions)],
    event_id: UUID | None = None,
    driver_id: UUID | None = None,
    vehicle_id: UUID | None = None,
    session_status: Annotated[SessionStatus | None, Query(alias="status")] = None,
    results_status: ResultsStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SessionPageResponse:
    """Return a page after Team, Driver relationship, and query filtering."""
    sessions, total = list_race_sessions(
        session,
        actor,
        event_id=event_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        status=session_status,
        results_status=results_status,
        limit=limit,
        offset=offset,
    )
    return SessionPageResponse(
        items=[SessionResponse.from_model(item) for item in sessions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/sessions/{session_id}",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Read one authorized Session",
    responses=SESSION_COMMON_RESPONSES,
)
def get_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_sessions)],
) -> SessionResponse:
    """Return one same-Team Session visible to the current actor."""
    return SessionResponse.from_model(get_race_session(session, actor, session_id))


@router.patch(
    "/sessions/{session_id}",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Edit a planned Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Assignment or state conflict."},
    },
)
def update_session_endpoint(
    session_id: UUID,
    payload: SessionUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Edit mutable planning fields while the Session remains PLANNED."""
    try:
        race_session = update_race_session(
            session,
            actor,
            session_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except SessionAssignmentConflictError as error:
        raise _session_assignment_conflict() from error
    except SessionNotEditableError as error:
        raise _session_not_editable() from error
    logger.info(
        "session updated",
        extra={
            "event": "session.updated",
            "session_id": str(race_session.session_id),
            "team_id": str(actor.team_id),
        },
    )
    return SessionResponse.from_model(race_session)


def _session_assignment_conflict() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=SESSION_ASSIGNMENT_CONFLICT_PROBLEM,
    )


def _session_not_editable() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=SESSION_NOT_EDITABLE_PROBLEM)
