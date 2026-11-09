"""Application services for same-Team Event planning and lifecycle."""

from collections.abc import Mapping, Set
from datetime import date
from types import MappingProxyType
from typing import Final
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.operations.enums import EventStatus
from raceops.operations.errors import (
    EventDateRangeError,
    InvalidEventStatusTransitionError,
)
from raceops.operations.models import Event, Track

EVENT_STATUS_TRANSITIONS: Final[Mapping[EventStatus, Set[EventStatus]]] = (
    MappingProxyType(
        {
            EventStatus.PLANNED: frozenset(
                {
                    EventStatus.ACTIVE,
                    EventStatus.COMPLETED,
                    EventStatus.CANCELLED,
                }
            ),
            EventStatus.ACTIVE: frozenset(
                {EventStatus.COMPLETED, EventStatus.CANCELLED}
            ),
            EventStatus.COMPLETED: frozenset(),
            EventStatus.CANCELLED: frozenset(),
        }
    )
)


def create_event(
    session: Session,
    actor: CurrentIdentity,
    *,
    track_id: UUID,
    name: str,
    starts_on: date,
    ends_on: date | None,
    description: str | None,
) -> Event:
    """Create one PLANNED Event linked to a Track in the active Team."""
    _require_same_team_track(session, actor.team_id, track_id)
    _validate_date_range(starts_on, ends_on)
    event = Event(
        team_id=actor.team_id,
        track_id=track_id,
        name=name,
        starts_on=starts_on,
        ends_on=ends_on,
        description=description,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def list_events(
    session: Session,
    actor: CurrentIdentity,
    *,
    status: EventStatus | None,
    track_id: UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Event], int]:
    """List Events in the active Team with small operational filters."""
    filters = [Event.team_id == actor.team_id]
    if status is not None:
        filters.append(Event.status == status)
    if track_id is not None:
        filters.append(Event.track_id == track_id)
    total = session.scalar(select(func.count()).select_from(Event).where(*filters))
    statement = (
        select(Event)
        .where(*filters)
        .order_by(Event.starts_on, Event.event_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_event(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
) -> Event:
    """Read one same-Team Event without revealing foreign resources."""
    event = session.scalar(
        select(Event).where(
            Event.event_id == event_id,
            Event.team_id == actor.team_id,
        )
    )
    if event is None:
        raise ResourceNotFoundError
    return event


def update_event(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Event:
    """Update Event metadata while preserving Team and date invariants."""
    event = _get_event_for_update(session, actor.team_id, event_id)
    track_id = changes.get("track_id", event.track_id)
    name = changes.get("name", event.name)
    starts_on = changes.get("starts_on", event.starts_on)
    ends_on = changes.get("ends_on", event.ends_on)
    description = changes.get("description", event.description)

    if not isinstance(track_id, UUID):
        raise TypeError("validated track_id must be a UUID")
    if not isinstance(name, str):
        raise TypeError("validated name must be a string")
    if not isinstance(starts_on, date):
        raise TypeError("validated starts_on must be a date")
    if ends_on is not None and not isinstance(ends_on, date):
        raise TypeError("validated ends_on must be a date or None")
    if description is not None and not isinstance(description, str):
        raise TypeError("validated description must be a string or None")

    _require_same_team_track(session, actor.team_id, track_id)
    _validate_date_range(starts_on, ends_on)
    event.track_id = track_id
    event.name = name
    event.starts_on = starts_on
    event.ends_on = ends_on
    event.description = description
    session.commit()
    session.refresh(event)
    return event


def transition_event_status(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
    target_status: EventStatus,
) -> Event:
    """Apply one explicit valid Event transition without implicit reopening."""
    event = _get_event_for_update(session, actor.team_id, event_id)
    if target_status not in EVENT_STATUS_TRANSITIONS[event.status]:
        session.rollback()
        raise InvalidEventStatusTransitionError
    event.status = target_status
    session.commit()
    session.refresh(event)
    return event


def _get_event_for_update(
    session: Session,
    team_id: UUID,
    event_id: UUID,
) -> Event:
    event = session.scalar(
        select(Event)
        .where(
            Event.event_id == event_id,
            Event.team_id == team_id,
        )
        .with_for_update()
    )
    if event is None:
        raise ResourceNotFoundError
    return event


def _require_same_team_track(
    session: Session,
    team_id: UUID,
    track_id: UUID,
) -> None:
    found = session.scalar(
        select(Track.track_id).where(
            Track.track_id == track_id,
            Track.team_id == team_id,
        )
    )
    if found is None:
        raise ResourceNotFoundError


def _validate_date_range(starts_on: date, ends_on: date | None) -> None:
    if ends_on is not None and ends_on < starts_on:
        raise EventDateRangeError
