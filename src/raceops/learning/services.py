"""Transactional services for visible, non-causal Observations."""

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import and_, exists, false, func, or_, select, true
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.iam.errors import InsufficientPermissionsError, ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.learning.models import Observation
from raceops.operations.models import Driver
from raceops.operations.vehicles import get_vehicle
from raceops.sessions.models import RaceSession
from raceops.sessions.services import get_race_session


def create_observation(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
    description: str,
    category: str | None,
    visibility_level: Visibility,
) -> Observation:
    """Create evidence after validating context and confidentiality authority."""
    _validate_visibility_writer(actor, visibility_level)
    _require_targets(session, actor, session_id=session_id, vehicle_id=vehicle_id)
    observation = Observation(
        team_id=actor.team_id,
        session_id=session_id,
        vehicle_id=vehicle_id,
        author_user_id=actor.user_id,
        description=description,
        category=category,
        visibility_level=visibility_level,
    )
    session.add(observation)
    session.commit()
    session.refresh(observation)
    return observation


def list_observations(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Observation], int]:
    """List only records visible to the actor before counting and paging."""
    filters: list[ColumnElement[bool]] = [
        Observation.team_id == actor.team_id,
        _observation_visibility_filter(actor),
    ]
    if session_id is not None:
        filters.append(Observation.session_id == session_id)
    if vehicle_id is not None:
        filters.append(Observation.vehicle_id == vehicle_id)
    total = session.scalar(
        select(func.count()).select_from(Observation).where(*filters)
    )
    statement = (
        select(Observation)
        .where(*filters)
        .order_by(Observation.created_at, Observation.observation_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_observation(
    session: Session,
    actor: CurrentIdentity,
    observation_id: UUID,
) -> Observation:
    """Read one visible record without disclosing why another is hidden."""
    observation = session.scalar(
        select(Observation).where(
            Observation.observation_id == observation_id,
            Observation.team_id == actor.team_id,
            _observation_visibility_filter(actor),
        )
    )
    if observation is None:
        raise ResourceNotFoundError
    return observation


def update_observation(
    session: Session,
    actor: CurrentIdentity,
    observation_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Observation:
    """Update visible evidence text without changing context or visibility."""
    observation = session.scalar(
        select(Observation)
        .where(
            Observation.observation_id == observation_id,
            Observation.team_id == actor.team_id,
            _observation_visibility_filter(actor),
        )
        .with_for_update()
    )
    if observation is None:
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(observation, field, value)
    session.commit()
    session.refresh(observation)
    return observation


def _validate_visibility_writer(
    actor: CurrentIdentity,
    visibility_level: Visibility,
) -> None:
    if (
        visibility_level is Visibility.ENGINEERING_CONFIDENTIAL
        and actor.role is not Role.ENGINEER
    ):
        raise InsufficientPermissionsError


def _require_targets(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
) -> None:
    if session_id is not None:
        get_race_session(session, actor, session_id)
    if vehicle_id is not None:
        get_vehicle(session, actor, vehicle_id)


def _observation_visibility_filter(actor: CurrentIdentity) -> ColumnElement[bool]:
    if actor.role is Role.ENGINEER:
        return true()
    if actor.role in {Role.TEAM_MANAGER, Role.MECHANIC}:
        return Observation.visibility_level.in_(
            (Visibility.TEAM, Visibility.ROLE_RESTRICTED)
        )
    if actor.role is Role.ADMINISTRATOR:
        return Observation.visibility_level == Visibility.TEAM
    if actor.role is Role.DRIVER:
        return and_(
            Observation.visibility_level == Visibility.TEAM,
            _driver_observation_relationship(actor),
        )
    return false()


def _driver_observation_relationship(actor: CurrentIdentity) -> ColumnElement[bool]:
    return exists().where(
        Driver.team_id == actor.team_id,
        Driver.user_id == actor.user_id,
        RaceSession.team_id == actor.team_id,
        RaceSession.driver_id == Driver.driver_id,
        or_(
            and_(
                Observation.session_id.is_not(None),
                RaceSession.session_id == Observation.session_id,
            ),
            and_(
                Observation.session_id.is_(None),
                Observation.vehicle_id.is_not(None),
                RaceSession.vehicle_id == Observation.vehicle_id,
            ),
        ),
    )
