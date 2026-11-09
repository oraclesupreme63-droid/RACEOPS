"""HTTP boundary for Track catalog and Event planning resources."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.operations.enums import EventStatus
from raceops.operations.errors import (
    EventDateRangeError,
    InvalidEventStatusTransitionError,
)
from raceops.operations.events import (
    create_event,
    get_event,
    list_events,
    transition_event_status,
    update_event,
)
from raceops.operations.schemas import (
    EventCreateRequest,
    EventPageResponse,
    EventResponse,
    EventUpdateRequest,
    TrackCreateRequest,
    TrackPageResponse,
    TrackResponse,
    TrackUpdateRequest,
)
from raceops.operations.tracks import (
    create_track,
    get_track,
    list_tracks,
    update_track,
)

track_logger = logging.getLogger("raceops.operations.tracks")
event_logger = logging.getLogger("raceops.operations.events")
router = APIRouter()

read_tracks = require_permission(Permission.READ_TRACKS)
write_tracks = require_permission(Permission.WRITE_TRACKS)
read_events = require_permission(Permission.READ_EVENTS)
write_events = require_permission(Permission.WRITE_EVENTS)

EVENT_DATE_RANGE_PROBLEM = ProblemDefinition(
    "invalid-event-date-range",
    "Invalid event date range",
    "invalid_event_date_range",
    "The event end date cannot precede its start date.",
)
INVALID_EVENT_STATUS_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-event-status-transition",
    "Invalid event status transition",
    "invalid_event_status_transition",
    "The requested event status transition is not allowed.",
)

TRACK_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Track not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}
EVENT_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Event or Track not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/tracks",
    tags=["tracks"],
    response_model=TrackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Track in the active Team",
    responses=TRACK_COMMON_RESPONSES,
)
def create_track_endpoint(
    payload: TrackCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_tracks)],
) -> TrackResponse:
    """Create a small Team-owned Track reference without telemetry metadata."""
    track = create_track(
        session,
        actor,
        name=payload.name,
        location=payload.location,
    )
    track_logger.info(
        "track created",
        extra={
            "event": "track.created",
            "track_id": str(track.track_id),
            "team_id": str(actor.team_id),
        },
    )
    return TrackResponse.from_model(track)


@router.get(
    "/tracks",
    tags=["tracks"],
    response_model=TrackPageResponse,
    summary="List Tracks in the active Team",
    responses=TRACK_COMMON_RESPONSES,
)
def list_tracks_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_tracks)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TrackPageResponse:
    """Return a stable page after Team filtering."""
    tracks, total = list_tracks(session, actor, limit=limit, offset=offset)
    return TrackPageResponse(
        items=[TrackResponse.from_model(track) for track in tracks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/tracks/{track_id}",
    tags=["tracks"],
    response_model=TrackResponse,
    summary="Read one same-Team Track",
    responses=TRACK_COMMON_RESPONSES,
)
def get_track_endpoint(
    track_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_tracks)],
) -> TrackResponse:
    """Return one Track only inside the active Team."""
    return TrackResponse.from_model(get_track(session, actor, track_id))


@router.patch(
    "/tracks/{track_id}",
    tags=["tracks"],
    response_model=TrackResponse,
    summary="Update Track metadata",
    responses=TRACK_COMMON_RESPONSES,
)
def update_track_endpoint(
    track_id: UUID,
    payload: TrackUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_tracks)],
) -> TrackResponse:
    """Update name or optional location while preserving ownership."""
    track = update_track(
        session,
        actor,
        track_id,
        change_name="name" in payload.model_fields_set,
        name=payload.name,
        change_location="location" in payload.model_fields_set,
        location=payload.location,
    )
    track_logger.info(
        "track updated",
        extra={
            "event": "track.updated",
            "track_id": str(track.track_id),
            "team_id": str(actor.team_id),
        },
    )
    return TrackResponse.from_model(track)


@router.post(
    "/events",
    tags=["events"],
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an Event in the active Team",
    responses=EVENT_COMMON_RESPONSES,
)
def create_event_endpoint(
    payload: EventCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_events)],
) -> EventResponse:
    """Create a PLANNED Event linked to one same-Team Track."""
    try:
        event = create_event(
            session,
            actor,
            track_id=payload.track_id,
            name=payload.name,
            starts_on=payload.starts_on,
            ends_on=payload.ends_on,
            description=payload.description,
        )
    except EventDateRangeError as error:
        raise _event_date_range_problem() from error
    event_logger.info(
        "event created",
        extra={
            "event": "event.created",
            "event_id": str(event.event_id),
            "team_id": str(actor.team_id),
        },
    )
    return EventResponse.from_model(event)


@router.get(
    "/events",
    tags=["events"],
    response_model=EventPageResponse,
    summary="List Events in the active Team",
    responses=EVENT_COMMON_RESPONSES,
)
def list_events_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_events)],
    event_status: Annotated[EventStatus | None, Query(alias="status")] = None,
    track_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EventPageResponse:
    """Return a stable page after Team, status, and Track filtering."""
    events, total = list_events(
        session,
        actor,
        status=event_status,
        track_id=track_id,
        limit=limit,
        offset=offset,
    )
    return EventPageResponse(
        items=[EventResponse.from_model(event) for event in events],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/events/{event_id}",
    tags=["events"],
    response_model=EventResponse,
    summary="Read one same-Team Event",
    responses=EVENT_COMMON_RESPONSES,
)
def get_event_endpoint(
    event_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_events)],
) -> EventResponse:
    """Return one Event only inside the actor's active Team."""
    return EventResponse.from_model(get_event(session, actor, event_id))


@router.patch(
    "/events/{event_id}",
    tags=["events"],
    response_model=EventResponse,
    summary="Update Event metadata",
    responses=EVENT_COMMON_RESPONSES,
)
def update_event_endpoint(
    event_id: UUID,
    payload: EventUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_events)],
) -> EventResponse:
    """Update Event metadata; status remains an explicit command."""
    try:
        event = update_event(
            session,
            actor,
            event_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except EventDateRangeError as error:
        raise _event_date_range_problem() from error
    event_logger.info(
        "event updated",
        extra={
            "event": "event.updated",
            "event_id": str(event.event_id),
            "team_id": str(actor.team_id),
        },
    )
    return EventResponse.from_model(event)


@router.post(
    "/events/{event_id}/activate",
    tags=["events"],
    response_model=EventResponse,
    summary="Activate a planned Event",
    responses={
        **EVENT_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def activate_event_endpoint(
    event_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_events)],
) -> EventResponse:
    """Move a PLANNED Event to ACTIVE."""
    return _change_event_status(session, actor, event_id, EventStatus.ACTIVE)


@router.post(
    "/events/{event_id}/complete",
    tags=["events"],
    response_model=EventResponse,
    summary="Complete an Event",
    responses={
        **EVENT_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def complete_event_endpoint(
    event_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_events)],
) -> EventResponse:
    """Complete a PLANNED or ACTIVE Event without requiring live capture."""
    return _change_event_status(session, actor, event_id, EventStatus.COMPLETED)


@router.post(
    "/events/{event_id}/cancel",
    tags=["events"],
    response_model=EventResponse,
    summary="Cancel an Event",
    responses={
        **EVENT_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def cancel_event_endpoint(
    event_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_events)],
) -> EventResponse:
    """Cancel a PLANNED or ACTIVE Event into a terminal state."""
    return _change_event_status(session, actor, event_id, EventStatus.CANCELLED)


def _change_event_status(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
    target_status: EventStatus,
) -> EventResponse:
    try:
        event = transition_event_status(
            session,
            actor,
            event_id,
            target_status,
        )
    except InvalidEventStatusTransitionError as error:
        raise _invalid_event_status_transition() from error
    event_logger.info(
        "event status changed",
        extra={
            "event": "event.status_changed",
            "event_id": str(event.event_id),
            "team_id": str(actor.team_id),
            "event_status": event.status.value,
        },
    )
    return EventResponse.from_model(event)


def _event_date_range_problem() -> ApiProblemError:
    return ApiProblemError(
        status_code=422,
        definition=EVENT_DATE_RANGE_PROBLEM,
    )


def _invalid_event_status_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=INVALID_EVENT_STATUS_TRANSITION_PROBLEM,
    )
