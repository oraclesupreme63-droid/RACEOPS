"""Transactional services for optional per-Session Condition Snapshots."""

from collections.abc import Mapping
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.errors import (
    ConditionSnapshotExistsError,
    InvalidConditionSnapshotError,
)
from raceops.sessions.models import ConditionSnapshot, RaceSession
from raceops.sessions.services import get_race_session


def create_condition_snapshot(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    values: Mapping[str, object],
) -> ConditionSnapshot:
    """Create the one sparse snapshot after locking its parent Session."""
    _require_session_for_update(session, actor.team_id, session_id)
    snapshot = ConditionSnapshot(
        team_id=actor.team_id,
        session_id=session_id,
        **values,
    )
    _validate_snapshot(snapshot)
    session.add(snapshot)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ConditionSnapshotExistsError from error
    session.refresh(snapshot)
    return snapshot


def get_condition_snapshot(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
) -> ConditionSnapshot:
    """Read conditions through Team and Driver-to-Session authorization."""
    get_race_session(session, actor, session_id)
    snapshot = session.scalar(
        select(ConditionSnapshot).where(
            ConditionSnapshot.session_id == session_id,
            ConditionSnapshot.team_id == actor.team_id,
        )
    )
    if snapshot is None:
        raise ResourceNotFoundError
    return snapshot


def update_condition_snapshot(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    changes: Mapping[str, object],
) -> ConditionSnapshot:
    """Update known fields while preserving pair and non-empty invariants."""
    _require_session_for_update(session, actor.team_id, session_id)
    snapshot = session.scalar(
        select(ConditionSnapshot)
        .where(
            ConditionSnapshot.session_id == session_id,
            ConditionSnapshot.team_id == actor.team_id,
        )
        .with_for_update()
    )
    if snapshot is None:
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(snapshot, field, value)
    try:
        _validate_snapshot(snapshot)
    except InvalidConditionSnapshotError:
        session.rollback()
        raise
    session.commit()
    session.refresh(snapshot)
    return snapshot


def _require_session_for_update(
    session: Session,
    team_id: UUID,
    session_id: UUID,
) -> RaceSession:
    race_session = session.scalar(
        select(RaceSession)
        .where(
            RaceSession.session_id == session_id,
            RaceSession.team_id == team_id,
        )
        .with_for_update()
    )
    if race_session is None:
        raise ResourceNotFoundError
    return race_session


def _validate_snapshot(snapshot: ConditionSnapshot) -> None:
    _validate_measurement_pair(
        snapshot.ambient_temperature,
        snapshot.ambient_temperature_unit,
    )
    _validate_measurement_pair(
        snapshot.track_temperature,
        snapshot.track_temperature_unit,
    )
    if all(
        getattr(snapshot, field) is None
        for field in (
            "ambient_temperature",
            "track_temperature",
            "weather",
            "track_condition",
        )
    ):
        raise InvalidConditionSnapshotError


def _validate_measurement_pair(
    value: Decimal | None,
    unit: str | None,
) -> None:
    if (value is None) != (unit is None):
        raise InvalidConditionSnapshotError
