"""HTTP boundary for Session planning and lifecycle resources."""

import logging
from collections.abc import Callable
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
    InvalidResultsStatusTransitionError,
    InvalidSessionStatusTransitionError,
    SessionAssignmentConflictError,
    SessionDriverLockedByFeedbackError,
    SessionNotEditableError,
)
from raceops.sessions.models import RaceSession
from raceops.sessions.schemas import (
    SessionCreateRequest,
    SessionPageResponse,
    SessionResponse,
    SessionUpdateRequest,
)
from raceops.sessions.services import (
    cancel_race_session,
    complete_race_session,
    create_race_session,
    get_race_session,
    list_race_sessions,
    lock_race_session_results,
    pause_race_session,
    resume_race_session,
    start_race_session,
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
INVALID_SESSION_STATUS_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-session-status-transition",
    "Invalid Session status transition",
    "invalid_session_status_transition",
    "The requested Session activity transition is not allowed.",
)
INVALID_RESULTS_STATUS_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-results-status-transition",
    "Invalid results status transition",
    "invalid_results_status_transition",
    "Results can only be locked once a Session is terminal and still open.",
)
SESSION_DRIVER_LOCKED_BY_FEEDBACK_PROBLEM = ProblemDefinition(
    "session-driver-locked-by-feedback",
    "Session Driver is locked by feedback",
    "session_driver_locked_by_feedback",
    "A Session with Driver Feedback cannot be assigned to another Driver.",
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
    except SessionDriverLockedByFeedbackError as error:
        raise _session_driver_locked_by_feedback() from error
    logger.info(
        "session updated",
        extra={
            "event": "session.updated",
            "session_id": str(race_session.session_id),
            "team_id": str(actor.team_id),
        },
    )
    return SessionResponse.from_model(race_session)


@router.post(
    "/sessions/{session_id}/start",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Start a planned Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Assignment or state conflict."},
    },
)
def start_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Start after atomically revalidating Driver and Vehicle eligibility."""
    try:
        race_session = start_race_session(session, actor, session_id)
    except SessionAssignmentConflictError as error:
        raise _session_assignment_conflict() from error
    except InvalidSessionStatusTransitionError as error:
        raise _invalid_session_status_transition() from error
    return _log_status_change(race_session, actor)


@router.post(
    "/sessions/{session_id}/pause",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Pause an active Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def pause_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Pause an active Session without changing its first start time."""
    return _run_status_command(session, actor, session_id, pause_race_session)


@router.post(
    "/sessions/{session_id}/resume",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Resume a paused Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def resume_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Resume a paused Session while preserving its first start time."""
    return _run_status_command(session, actor, session_id, resume_race_session)


@router.post(
    "/sessions/{session_id}/complete",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Complete a Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def complete_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Complete an active or paused Session with a server-side end time."""
    return _run_status_command(session, actor, session_id, complete_race_session)


@router.post(
    "/sessions/{session_id}/cancel",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Cancel a non-terminal Session",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def cancel_session_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Cancel a planned, active, or paused Session."""
    return _run_status_command(session, actor, session_id, cancel_race_session)


@router.post(
    "/sessions/{session_id}/lock-results",
    tags=["sessions"],
    response_model=SessionResponse,
    summary="Lock terminal Session results",
    responses={
        **SESSION_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid results transition."},
    },
)
def lock_session_results_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_sessions)],
) -> SessionResponse:
    """Lock terminal results once and preserve actor and server time."""
    try:
        race_session = lock_race_session_results(session, actor, session_id)
    except InvalidResultsStatusTransitionError as error:
        raise _invalid_results_status_transition() from error
    logger.info(
        "session results locked",
        extra={
            "event": "session.results_locked",
            "session_id": str(race_session.session_id),
            "team_id": str(actor.team_id),
            "actor_user_id": str(actor.user_id),
        },
    )
    return SessionResponse.from_model(race_session)


def _run_status_command(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    command: Callable[[Session, CurrentIdentity, UUID], RaceSession],
) -> SessionResponse:
    try:
        race_session = command(session, actor, session_id)
    except InvalidSessionStatusTransitionError as error:
        raise _invalid_session_status_transition() from error
    return _log_status_change(race_session, actor)


def _log_status_change(
    race_session: RaceSession,
    actor: CurrentIdentity,
) -> SessionResponse:
    logger.info(
        "session status changed",
        extra={
            "event": "session.status_changed",
            "session_id": str(race_session.session_id),
            "team_id": str(actor.team_id),
            "session_status": race_session.status.value,
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


def _session_driver_locked_by_feedback() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=SESSION_DRIVER_LOCKED_BY_FEEDBACK_PROBLEM,
    )


def _invalid_session_status_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=INVALID_SESSION_STATUS_TRANSITION_PROBLEM,
    )


def _invalid_results_status_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=INVALID_RESULTS_STATUS_TRANSITION_PROBLEM,
    )
