"""Transactional services for relationship-scoped Driver Feedback."""

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import false, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from raceops.iam.authorization import Visibility, enforce_visibility
from raceops.iam.enums import Role
from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.models import DriverFeedback, RaceSession
from raceops.sessions.services import get_race_session

FEEDBACK_READER_ROLES = frozenset({Role.TEAM_MANAGER, Role.ENGINEER})


def create_driver_feedback(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    values: Mapping[str, object],
) -> DriverFeedback:
    """Record self or communicated feedback using the Session's Driver."""
    authorized_session = get_race_session(session, actor, session_id)
    locked_session = session.scalar(
        select(RaceSession)
        .where(
            RaceSession.session_id == authorized_session.session_id,
            RaceSession.team_id == actor.team_id,
        )
        .with_for_update()
    )
    if locked_session is None:
        raise ResourceNotFoundError
    feedback = DriverFeedback(
        team_id=actor.team_id,
        session_id=locked_session.session_id,
        driver_id=locked_session.driver_id,
        author_user_id=actor.user_id,
        visibility_level=Visibility.ROLE_RESTRICTED,
        **values,
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


def list_driver_feedback(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    limit: int,
    offset: int,
) -> tuple[list[DriverFeedback], int]:
    """List only feedback visible to the actor for an authorized Session."""
    get_race_session(session, actor, session_id)
    filters: list[ColumnElement[bool]] = [
        DriverFeedback.team_id == actor.team_id,
        DriverFeedback.session_id == session_id,
    ]
    filters.append(_feedback_visibility_filter(actor))
    total = session.scalar(
        select(func.count()).select_from(DriverFeedback).where(*filters)
    )
    statement = (
        select(DriverFeedback)
        .where(*filters)
        .order_by(DriverFeedback.created_at, DriverFeedback.feedback_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_driver_feedback(
    session: Session,
    actor: CurrentIdentity,
    feedback_id: UUID,
) -> DriverFeedback:
    """Read one record without leaking Team, Session, or visibility failures."""
    feedback = session.scalar(
        select(DriverFeedback).where(
            DriverFeedback.feedback_id == feedback_id,
            DriverFeedback.team_id == actor.team_id,
        )
    )
    if feedback is None:
        raise ResourceNotFoundError
    get_race_session(session, actor, feedback.session_id)
    enforce_visibility(
        actor,
        resource_team_id=feedback.team_id,
        visibility=feedback.visibility_level,
        allowed_roles=FEEDBACK_READER_ROLES,
        is_related=_is_related(actor, feedback),
    )
    return feedback


def update_driver_feedback(
    session: Session,
    actor: CurrentIdentity,
    feedback_id: UUID,
    *,
    changes: Mapping[str, object],
) -> DriverFeedback:
    """Let Engineers edit visible records and Drivers edit only their own."""
    feedback = session.scalar(
        select(DriverFeedback)
        .where(
            DriverFeedback.feedback_id == feedback_id,
            DriverFeedback.team_id == actor.team_id,
        )
        .with_for_update()
    )
    if feedback is None:
        raise ResourceNotFoundError
    get_race_session(session, actor, feedback.session_id)
    if actor.role is Role.DRIVER and feedback.author_user_id != actor.user_id:
        session.rollback()
        raise ResourceNotFoundError
    if actor.role not in {Role.DRIVER, Role.ENGINEER}:
        session.rollback()
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(feedback, field, value)
    session.commit()
    session.refresh(feedback)
    return feedback


def _feedback_visibility_filter(actor: CurrentIdentity) -> ColumnElement[bool]:
    if actor.role in FEEDBACK_READER_ROLES or actor.role is Role.DRIVER:
        return DriverFeedback.visibility_level == Visibility.ROLE_RESTRICTED
    if actor.role is Role.MECHANIC:
        return (DriverFeedback.visibility_level == Visibility.ROLE_RESTRICTED) & (
            DriverFeedback.author_user_id == actor.user_id
        )
    return false()


def _is_related(actor: CurrentIdentity, feedback: DriverFeedback) -> bool:
    if actor.role is Role.DRIVER:
        return True
    return actor.role is Role.MECHANIC and feedback.author_user_id == actor.user_id
