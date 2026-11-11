"""Transactional rules for priorities and Action execution."""

from collections.abc import Mapping
from typing import cast
from uuid import UUID

from sqlalchemy import and_, exists, false, func, or_, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.errors import InsufficientPermissionsError, ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import TeamMembership, User
from raceops.learning.enums import ActionStatus, ActionType, TargetIntent
from raceops.learning.errors import (
    InvalidActionStatusTransitionError,
    InvalidDecisionContextError,
    PriorityScopeConflictError,
)
from raceops.learning.models import Action, Hypothesis, Priority, SessionAnalysis
from raceops.operations.models import Driver
from raceops.sessions.models import RaceSession
from raceops.sessions.services import get_race_session

ACTION_TRANSITIONS: Mapping[ActionStatus, frozenset[ActionStatus]] = {
    ActionStatus.PROPOSED: frozenset({ActionStatus.PLANNED, ActionStatus.CANCELLED}),
    ActionStatus.PLANNED: frozenset({ActionStatus.IN_PROGRESS, ActionStatus.CANCELLED}),
    ActionStatus.IN_PROGRESS: frozenset(
        {ActionStatus.COMPLETED, ActionStatus.CANCELLED}
    ),
    ActionStatus.COMPLETED: frozenset(),
    ActionStatus.CANCELLED: frozenset(),
}


def create_priority(
    session: Session,
    actor: CurrentIdentity,
    *,
    source_session_id: UUID,
    target_intent: TargetIntent,
    target_session_id: UUID | None,
    hypothesis_id: UUID | None,
    recipient_role: Role,
    recipient_user_id: UUID | None,
    description: str,
    is_main: bool,
    rank: int | None,
) -> Priority:
    """Create a recipient-scoped focus and atomically enforce the main three."""
    source, target_scope_id = _require_target(
        session,
        actor,
        source_session_id=source_session_id,
        target_intent=target_intent,
        target_session_id=target_session_id,
    )
    _require_hypothesis_for_source(
        session, actor, hypothesis_id, source_session_id=source_session_id
    )
    _require_recipient(
        session,
        actor,
        source,
        role=recipient_role,
        user_id=recipient_user_id,
    )
    resolved_rank = _resolve_priority_rank(
        session,
        actor.team_id,
        target_scope_id=target_scope_id,
        recipient_role=recipient_role,
        recipient_user_id=recipient_user_id,
        is_main=is_main,
        requested_rank=rank,
    )
    priority = Priority(
        team_id=actor.team_id,
        source_session_id=source_session_id,
        target_session_id=target_session_id,
        target_scope_id=target_scope_id,
        hypothesis_id=hypothesis_id,
        target_intent=target_intent,
        recipient_role=recipient_role,
        recipient_user_id=recipient_user_id,
        description=description,
        is_main=is_main,
        rank=resolved_rank,
    )
    try:
        session.add(priority)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise PriorityScopeConflictError from error
    session.refresh(priority)
    return priority


def list_priorities(
    session: Session,
    actor: CurrentIdentity,
    *,
    source_session_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[Priority], int]:
    """Filter by audience before counting or paging priorities."""
    get_race_session(session, actor, source_session_id)
    filters = (
        Priority.team_id == actor.team_id,
        Priority.source_session_id == source_session_id,
        _priority_visibility_filter(actor),
    )
    total = session.scalar(select(func.count()).select_from(Priority).where(*filters))
    statement = (
        select(Priority)
        .where(*filters)
        .order_by(
            Priority.is_main.desc(),
            Priority.rank.asc().nulls_last(),
            Priority.created_at,
            Priority.priority_id,
        )
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_priority(
    session: Session,
    actor: CurrentIdentity,
    priority_id: UUID,
    *,
    for_update: bool = False,
    require_visible: bool = True,
) -> Priority:
    filters: list[ColumnElement[bool]] = [
        Priority.priority_id == priority_id,
        Priority.team_id == actor.team_id,
    ]
    if require_visible:
        filters.append(_priority_visibility_filter(actor))
    statement = select(Priority).where(*filters)
    if for_update:
        statement = statement.with_for_update()
    priority = session.scalar(statement)
    if priority is None:
        raise ResourceNotFoundError
    return priority


def update_priority(
    session: Session,
    actor: CurrentIdentity,
    priority_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Priority:
    """Revise an Engineer-owned focus while preserving scope and audience."""
    priority = get_priority(
        session, actor, priority_id, for_update=True, require_visible=False
    )
    if "description" in changes:
        priority.description = str(changes["description"])
    if "is_main" in changes:
        is_main = bool(changes["is_main"])
        requested_rank = changes.get("rank")
        priority.is_main = is_main
        priority.rank = _resolve_priority_rank(
            session,
            actor.team_id,
            target_scope_id=priority.target_scope_id,
            recipient_role=priority.recipient_role,
            recipient_user_id=priority.recipient_user_id,
            is_main=is_main,
            requested_rank=(
                cast(int, requested_rank) if requested_rank is not None else None
            ),
            exclude_priority_id=priority.priority_id,
        )
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise PriorityScopeConflictError from error
    session.refresh(priority)
    return priority


def create_action(
    session: Session,
    actor: CurrentIdentity,
    *,
    source_session_id: UUID,
    target_intent: TargetIntent,
    target_session_id: UUID | None,
    hypothesis_id: UUID | None,
    priority_id: UUID | None,
    assignee_user_id: UUID | None,
    assignee_role: Role,
    action_type: ActionType,
    public_summary: str | None,
    confidential_detail: str | None,
) -> Action:
    """Create assigned work without implying any performance outcome."""
    source, target_scope_id = _require_target(
        session,
        actor,
        source_session_id=source_session_id,
        target_intent=target_intent,
        target_session_id=target_session_id,
    )
    if confidential_detail is not None and actor.role is not Role.ENGINEER:
        raise InsufficientPermissionsError
    if actor.role is Role.MECHANIC and (
        action_type is not ActionType.MECHANICAL
        or assignee_role is not Role.MECHANIC
        or assignee_user_id not in {None, actor.user_id}
    ):
        raise InsufficientPermissionsError
    _require_hypothesis_for_source(
        session, actor, hypothesis_id, source_session_id=source_session_id
    )
    priority = None
    if priority_id is not None:
        priority = get_priority(session, actor, priority_id)
        if (
            priority.source_session_id != source_session_id
            or priority.target_scope_id != target_scope_id
        ):
            raise InvalidDecisionContextError
        if (
            hypothesis_id is not None
            and priority.hypothesis_id is not None
            and priority.hypothesis_id != hypothesis_id
        ):
            raise InvalidDecisionContextError
    _require_recipient(
        session,
        actor,
        source,
        role=assignee_role,
        user_id=assignee_user_id,
    )
    action = Action(
        team_id=actor.team_id,
        source_session_id=source_session_id,
        target_session_id=target_session_id,
        target_scope_id=target_scope_id,
        hypothesis_id=hypothesis_id,
        priority_id=priority_id,
        assignee_user_id=assignee_user_id,
        assignee_role=assignee_role,
        target_intent=target_intent,
        action_type=action_type,
        public_summary=public_summary,
        confidential_detail=confidential_detail,
    )
    session.add(action)
    session.commit()
    session.refresh(action)
    return action


def list_actions(
    session: Session,
    actor: CurrentIdentity,
    *,
    source_session_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[Action], int]:
    """List only visible work before counts and pagination are calculated."""
    get_race_session(session, actor, source_session_id)
    filters = (
        Action.team_id == actor.team_id,
        Action.source_session_id == source_session_id,
        _action_visibility_filter(actor),
    )
    total = session.scalar(select(func.count()).select_from(Action).where(*filters))
    statement = (
        select(Action)
        .where(*filters)
        .order_by(Action.created_at, Action.action_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_action(
    session: Session,
    actor: CurrentIdentity,
    action_id: UUID,
    *,
    for_update: bool = False,
) -> Action:
    statement = select(Action).where(
        Action.action_id == action_id,
        Action.team_id == actor.team_id,
        _action_visibility_filter(actor),
    )
    if for_update:
        statement = statement.with_for_update()
    action = session.scalar(statement)
    if action is None:
        raise ResourceNotFoundError
    return action


def transition_action(
    session: Session,
    actor: CurrentIdentity,
    action_id: UUID,
    target_status: ActionStatus,
    *,
    cancellation_reason: str | None = None,
) -> Action:
    """Advance execution only for a coordinator or the assigned audience."""
    action = get_action(session, actor, action_id, for_update=True)
    if not _can_update_action(actor, action):
        raise InsufficientPermissionsError
    if target_status not in ACTION_TRANSITIONS[action.status]:
        raise InvalidActionStatusTransitionError
    if target_status is ActionStatus.CANCELLED:
        if cancellation_reason is None:
            raise InvalidDecisionContextError
        action.cancellation_reason = cancellation_reason
    action.status = target_status
    session.commit()
    session.refresh(action)
    return action


def _require_target(
    session: Session,
    actor: CurrentIdentity,
    *,
    source_session_id: UUID,
    target_intent: TargetIntent,
    target_session_id: UUID | None,
) -> tuple[RaceSession, UUID]:
    source = get_race_session(session, actor, source_session_id)
    if target_intent is TargetIntent.NEXT_SESSION:
        if target_session_id is not None:
            raise InvalidDecisionContextError
        return source, source.session_id
    if target_session_id is None:
        raise InvalidDecisionContextError
    target = get_race_session(session, actor, target_session_id)
    if (
        target.session_id == source.session_id
        or target.scheduled_at <= source.scheduled_at
    ):
        raise InvalidDecisionContextError
    return source, target.session_id


def _require_hypothesis_for_source(
    session: Session,
    actor: CurrentIdentity,
    hypothesis_id: UUID | None,
    *,
    source_session_id: UUID,
) -> Hypothesis | None:
    if hypothesis_id is None:
        return None
    if actor.role is not Role.ENGINEER:
        raise ResourceNotFoundError
    hypothesis = session.scalar(
        select(Hypothesis)
        .join(
            SessionAnalysis,
            and_(
                SessionAnalysis.analysis_id == Hypothesis.analysis_id,
                SessionAnalysis.team_id == Hypothesis.team_id,
            ),
        )
        .where(
            Hypothesis.hypothesis_id == hypothesis_id,
            Hypothesis.team_id == actor.team_id,
            SessionAnalysis.session_id == source_session_id,
        )
    )
    if hypothesis is None:
        raise ResourceNotFoundError
    return hypothesis


def _require_recipient(
    session: Session,
    actor: CurrentIdentity,
    source: RaceSession,
    *,
    role: Role,
    user_id: UUID | None,
) -> None:
    if role not in {Role.DRIVER, Role.ENGINEER, Role.MECHANIC}:
        raise InvalidDecisionContextError
    if user_id is not None:
        membership = session.scalar(
            select(TeamMembership)
            .join(User, User.user_id == TeamMembership.user_id)
            .where(
                TeamMembership.team_id == actor.team_id,
                TeamMembership.user_id == user_id,
                TeamMembership.role == role,
                TeamMembership.status == IdentityStatus.ACTIVE,
                User.status == IdentityStatus.ACTIVE,
            )
        )
        if membership is None:
            raise ResourceNotFoundError
    if role is Role.DRIVER and user_id is not None:
        matches_session_driver = session.scalar(
            select(
                exists().where(
                    Driver.driver_id == source.driver_id,
                    Driver.team_id == actor.team_id,
                    Driver.user_id == user_id,
                )
            )
        )
        if not matches_session_driver:
            raise InvalidDecisionContextError


def _resolve_priority_rank(
    session: Session,
    team_id: UUID,
    *,
    target_scope_id: UUID,
    recipient_role: Role,
    recipient_user_id: UUID | None,
    is_main: bool,
    requested_rank: int | None,
    exclude_priority_id: UUID | None = None,
) -> int | None:
    if not is_main:
        return None
    filters: list[ColumnElement[bool]] = [
        Priority.team_id == team_id,
        Priority.target_scope_id == target_scope_id,
        Priority.recipient_role == recipient_role,
        Priority.is_main.is_(True),
    ]
    if recipient_user_id is None:
        filters.append(Priority.recipient_user_id.is_(None))
    else:
        filters.append(Priority.recipient_user_id == recipient_user_id)
    if exclude_priority_id is not None:
        filters.append(Priority.priority_id != exclude_priority_id)
    used = set(session.scalars(select(Priority.rank).where(*filters).with_for_update()))
    if requested_rank is not None:
        if requested_rank in used:
            raise PriorityScopeConflictError
        return requested_rank
    for candidate in (1, 2, 3):
        if candidate not in used:
            return candidate
    raise PriorityScopeConflictError


def _priority_visibility_filter(actor: CurrentIdentity) -> ColumnElement[bool]:
    if actor.role in {Role.ENGINEER, Role.TEAM_MANAGER}:
        return true()
    if actor.role is Role.MECHANIC:
        return and_(
            Priority.recipient_role == Role.MECHANIC,
            or_(
                Priority.recipient_user_id.is_(None),
                Priority.recipient_user_id == actor.user_id,
            ),
        )
    if actor.role is Role.DRIVER:
        return and_(
            Priority.recipient_role == Role.DRIVER,
            or_(
                Priority.recipient_user_id.is_(None),
                Priority.recipient_user_id == actor.user_id,
            ),
            _driver_source_relationship(actor, Priority.source_session_id),
        )
    return false()


def _action_visibility_filter(actor: CurrentIdentity) -> ColumnElement[bool]:
    if actor.role in {Role.ENGINEER, Role.TEAM_MANAGER}:
        return true()
    if actor.role is Role.MECHANIC:
        return and_(
            Action.assignee_role == Role.MECHANIC,
            or_(
                Action.assignee_user_id.is_(None),
                Action.assignee_user_id == actor.user_id,
            ),
        )
    if actor.role is Role.DRIVER:
        return and_(
            _driver_source_relationship(actor, Action.source_session_id),
            or_(
                Action.public_summary.is_not(None),
                and_(
                    Action.assignee_role == Role.DRIVER,
                    or_(
                        Action.assignee_user_id.is_(None),
                        Action.assignee_user_id == actor.user_id,
                    ),
                ),
            ),
        )
    return false()


def _driver_source_relationship(
    actor: CurrentIdentity, source_session_column: object
) -> ColumnElement[bool]:
    return exists().where(
        Driver.team_id == actor.team_id,
        Driver.user_id == actor.user_id,
        RaceSession.team_id == actor.team_id,
        RaceSession.driver_id == Driver.driver_id,
        RaceSession.session_id == source_session_column,
    )


def _can_update_action(actor: CurrentIdentity, action: Action) -> bool:
    if actor.role in {Role.ENGINEER, Role.TEAM_MANAGER}:
        return True
    return action.assignee_role is actor.role and action.assignee_user_id in {
        None,
        actor.user_id,
    }
