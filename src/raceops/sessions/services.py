"""Application services for Session planning and relationship-scoped reads."""

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from raceops.iam.enums import Role
from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.operations.enums import DriverStatus, EventStatus, VehicleStatus
from raceops.operations.models import Driver, Event, Vehicle
from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.errors import (
    EventTrackLockedError,
    SessionAssignmentConflictError,
    SessionNotEditableError,
)
from raceops.sessions.models import RaceSession


def create_race_session(
    session: Session,
    actor: CurrentIdentity,
    *,
    event_id: UUID,
    driver_id: UUID,
    vehicle_id: UUID,
    session_type: str,
    scheduled_at: datetime,
) -> RaceSession:
    """Atomically validate and create one planned same-Team Session."""
    _require_event_for_update(session, actor.team_id, event_id)
    _require_eligible_assignment(
        session,
        actor.team_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
    )
    race_session = RaceSession(
        team_id=actor.team_id,
        event_id=event_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        session_type=session_type,
        scheduled_at=scheduled_at,
    )
    session.add(race_session)
    session.commit()
    session.refresh(race_session)
    return race_session


def list_race_sessions(
    session: Session,
    actor: CurrentIdentity,
    *,
    event_id: UUID | None,
    driver_id: UUID | None,
    vehicle_id: UUID | None,
    status: SessionStatus | None,
    results_status: ResultsStatus | None,
    limit: int,
    offset: int,
) -> tuple[list[RaceSession], int]:
    """List Sessions after ownership and Driver relationship filtering."""
    filters: list[ColumnElement[bool]] = [RaceSession.team_id == actor.team_id]
    if actor.role is Role.DRIVER:
        filters.append(_driver_session_relationship(actor))
    if event_id is not None:
        filters.append(RaceSession.event_id == event_id)
    if driver_id is not None:
        filters.append(RaceSession.driver_id == driver_id)
    if vehicle_id is not None:
        filters.append(RaceSession.vehicle_id == vehicle_id)
    if status is not None:
        filters.append(RaceSession.status == status)
    if results_status is not None:
        filters.append(RaceSession.results_status == results_status)

    total = session.scalar(
        select(func.count()).select_from(RaceSession).where(*filters)
    )
    statement = (
        select(RaceSession)
        .where(*filters)
        .order_by(RaceSession.scheduled_at, RaceSession.session_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_race_session(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
) -> RaceSession:
    """Read one Session without exposing another Team or Driver assignment."""
    filters: list[ColumnElement[bool]] = [
        RaceSession.session_id == session_id,
        RaceSession.team_id == actor.team_id,
    ]
    if actor.role is Role.DRIVER:
        filters.append(_driver_session_relationship(actor))
    race_session = session.scalar(select(RaceSession).where(*filters))
    if race_session is None:
        raise ResourceNotFoundError
    return race_session


def update_race_session(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    changes: Mapping[str, object],
) -> RaceSession:
    """Edit permitted fields and revalidate assignment while PLANNED."""
    race_session = session.scalar(
        select(RaceSession)
        .where(
            RaceSession.session_id == session_id,
            RaceSession.team_id == actor.team_id,
        )
        .with_for_update()
    )
    if race_session is None:
        raise ResourceNotFoundError
    if race_session.status is not SessionStatus.PLANNED:
        session.rollback()
        raise SessionNotEditableError

    driver_id = changes.get("driver_id", race_session.driver_id)
    vehicle_id = changes.get("vehicle_id", race_session.vehicle_id)
    if not isinstance(driver_id, UUID) or not isinstance(vehicle_id, UUID):
        raise TypeError("validated assignment identifiers must be UUIDs")
    if "driver_id" in changes or "vehicle_id" in changes:
        _require_eligible_assignment(
            session,
            actor.team_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
        )

    for field, value in changes.items():
        setattr(race_session, field, value)
    session.commit()
    session.refresh(race_session)
    return race_session


def ensure_event_track_change_allowed(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
    requested_track_id: UUID,
) -> None:
    """Serialize Event moves against Session creation and preserve Track history."""
    event = _require_event_for_update(session, actor.team_id, event_id)
    if event.track_id == requested_track_id:
        return
    has_sessions = session.scalar(
        select(
            exists().where(
                RaceSession.team_id == actor.team_id,
                RaceSession.event_id == event_id,
            )
        )
    )
    if has_sessions:
        session.rollback()
        raise EventTrackLockedError


def list_related_events(
    session: Session,
    actor: CurrentIdentity,
    *,
    status: EventStatus | None,
    track_id: UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Event], int]:
    """List only Events attached to the authenticated Driver's Sessions."""
    filters: list[ColumnElement[bool]] = [
        Event.team_id == actor.team_id,
        _related_event_exists(actor),
    ]
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


def get_related_event(
    session: Session,
    actor: CurrentIdentity,
    event_id: UUID,
) -> Event:
    """Read one Event only when it is related to the Driver actor."""
    event = session.scalar(
        select(Event).where(
            Event.event_id == event_id,
            Event.team_id == actor.team_id,
            _related_event_exists(actor),
        )
    )
    if event is None:
        raise ResourceNotFoundError
    return event


def list_related_vehicles(
    session: Session,
    actor: CurrentIdentity,
    *,
    status: VehicleStatus | None,
    limit: int,
    offset: int,
) -> tuple[list[Vehicle], int]:
    """List only Vehicles attached to the authenticated Driver's Sessions."""
    filters: list[ColumnElement[bool]] = [
        Vehicle.team_id == actor.team_id,
        _related_vehicle_exists(actor),
    ]
    if status is not None:
        filters.append(Vehicle.status == status)
    total = session.scalar(select(func.count()).select_from(Vehicle).where(*filters))
    statement = (
        select(Vehicle)
        .where(*filters)
        .order_by(Vehicle.created_at, Vehicle.vehicle_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_related_vehicle(
    session: Session,
    actor: CurrentIdentity,
    vehicle_id: UUID,
) -> Vehicle:
    """Read one Vehicle only when it is related to the Driver actor."""
    vehicle = session.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_id == vehicle_id,
            Vehicle.team_id == actor.team_id,
            _related_vehicle_exists(actor),
        )
    )
    if vehicle is None:
        raise ResourceNotFoundError
    return vehicle


def _require_event_for_update(
    session: Session,
    team_id: UUID,
    event_id: UUID,
) -> Event:
    event = session.scalar(
        select(Event)
        .where(Event.event_id == event_id, Event.team_id == team_id)
        .with_for_update()
    )
    if event is None:
        raise ResourceNotFoundError
    return event


def _require_eligible_assignment(
    session: Session,
    team_id: UUID,
    *,
    driver_id: UUID,
    vehicle_id: UUID,
) -> None:
    driver = session.scalar(
        select(Driver)
        .where(Driver.driver_id == driver_id, Driver.team_id == team_id)
        .with_for_update()
    )
    vehicle = session.scalar(
        select(Vehicle)
        .where(Vehicle.vehicle_id == vehicle_id, Vehicle.team_id == team_id)
        .with_for_update()
    )
    if driver is None or vehicle is None:
        raise ResourceNotFoundError
    if (
        driver.status is not DriverStatus.ACTIVE
        or vehicle.status is not VehicleStatus.READY
    ):
        session.rollback()
        raise SessionAssignmentConflictError


def _driver_session_relationship(actor: CurrentIdentity) -> ColumnElement[bool]:
    return exists().where(
        Driver.driver_id == RaceSession.driver_id,
        Driver.team_id == RaceSession.team_id,
        Driver.user_id == actor.user_id,
    )


def _related_event_exists(actor: CurrentIdentity) -> ColumnElement[bool]:
    return exists().where(
        RaceSession.event_id == Event.event_id,
        RaceSession.team_id == Event.team_id,
        Driver.driver_id == RaceSession.driver_id,
        Driver.team_id == RaceSession.team_id,
        Driver.user_id == actor.user_id,
    )


def _related_vehicle_exists(actor: CurrentIdentity) -> ColumnElement[bool]:
    return exists().where(
        RaceSession.vehicle_id == Vehicle.vehicle_id,
        RaceSession.team_id == Vehicle.team_id,
        Driver.driver_id == RaceSession.driver_id,
        Driver.team_id == RaceSession.team_id,
        Driver.user_id == actor.user_id,
    )
