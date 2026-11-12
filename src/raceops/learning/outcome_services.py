"""Transactional rules for Action Outcomes and learning-chain retrieval."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.iam.enums import Role
from raceops.iam.errors import InsufficientPermissionsError, ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.learning.decision_services import get_action, get_priority
from raceops.learning.enums import (
    ActionOutcomeClassification,
    ActionStatus,
    HypothesisStatus,
    TargetIntent,
)
from raceops.learning.errors import (
    ActionOutcomeConflictError,
    InvalidActionOutcomeError,
)
from raceops.learning.models import (
    Action,
    ActionOutcome,
    Hypothesis,
    Priority,
    SessionAnalysis,
)
from raceops.sessions.services import get_race_session


def create_action_outcome(
    session: Session,
    actor: CurrentIdentity,
    action_id: UUID,
    *,
    evaluation_session_id: UUID,
    classification: ActionOutcomeClassification,
    public_conclusion: str | None,
    confidential_conclusion: str | None,
    concluded_hypothesis_status: HypothesisStatus | None,
) -> ActionOutcome:
    """Evaluate completed work against one actual later Session exactly once."""
    action = get_action(session, actor, action_id, for_update=True)
    if not _can_write_outcome(actor, action):
        raise InsufficientPermissionsError
    if action.status is not ActionStatus.COMPLETED:
        raise InvalidActionOutcomeError
    if action.outcome is not None:
        raise ActionOutcomeConflictError
    if confidential_conclusion is not None and actor.role is not Role.ENGINEER:
        raise InsufficientPermissionsError
    if actor.role is not Role.ENGINEER and public_conclusion is None:
        raise InvalidActionOutcomeError

    source = get_race_session(session, actor, action.source_session_id)
    evaluation = get_race_session(session, actor, evaluation_session_id)
    if evaluation.scheduled_at <= source.scheduled_at:
        raise InvalidActionOutcomeError
    if (
        action.target_intent is TargetIntent.SPECIFIC_SESSION
        and action.target_session_id != evaluation.session_id
    ):
        raise InvalidActionOutcomeError

    hypothesis = _resolve_effective_hypothesis(session, action)
    if concluded_hypothesis_status is not None:
        if actor.role is not Role.ENGINEER:
            raise InsufficientPermissionsError
        if hypothesis is None or hypothesis.status is not HypothesisStatus.PROPOSED:
            raise InvalidActionOutcomeError

    priority = None
    if action.priority_id is not None:
        priority = session.scalar(
            select(Priority)
            .where(
                Priority.priority_id == action.priority_id,
                Priority.team_id == action.team_id,
            )
            .with_for_update()
        )
        if priority is None:
            raise InvalidActionOutcomeError

    action.target_intent = TargetIntent.SPECIFIC_SESSION
    action.target_session_id = evaluation.session_id
    action.target_scope_id = evaluation.session_id
    if priority is not None and priority.target_intent is TargetIntent.NEXT_SESSION:
        priority.target_intent = TargetIntent.SPECIFIC_SESSION
        priority.target_session_id = evaluation.session_id
        priority.target_scope_id = evaluation.session_id
    outcome = ActionOutcome(
        team_id=actor.team_id,
        action_id=action.action_id,
        evaluation_session_id=evaluation.session_id,
        classification=classification,
        public_conclusion=public_conclusion,
        confidential_conclusion=confidential_conclusion,
        concluded_hypothesis_status=concluded_hypothesis_status,
        author_user_id=actor.user_id,
    )
    if hypothesis is not None and concluded_hypothesis_status is not None:
        hypothesis.status = concluded_hypothesis_status
    try:
        session.add(outcome)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ActionOutcomeConflictError from error
    session.refresh(outcome)
    return outcome


def get_action_evaluation(
    session: Session, actor: CurrentIdentity, action_id: UUID
) -> Action:
    """Return the visible Action; absence of Outcome derives NOT_EVALUATED."""
    return get_action(session, actor, action_id)


def get_learning_chain(
    session: Session,
    actor: CurrentIdentity,
    action_id: UUID,
) -> tuple[
    Action,
    Priority | None,
    Hypothesis | None,
    SessionAnalysis | None,
]:
    """Traverse only nodes the current audience may receive."""
    action = get_action(session, actor, action_id)
    priority = None
    if action.priority_id is not None:
        try:
            priority = get_priority(session, actor, action.priority_id)
        except ResourceNotFoundError:
            priority = None

    if actor.role is not Role.ENGINEER:
        return action, priority, None, None

    hypothesis = _resolve_effective_hypothesis(session, action, priority=priority)
    analysis = None
    if hypothesis is not None:
        analysis = session.scalar(
            select(SessionAnalysis).where(
                SessionAnalysis.analysis_id == hypothesis.analysis_id,
                SessionAnalysis.team_id == actor.team_id,
            )
        )
    return action, priority, hypothesis, analysis


def _resolve_effective_hypothesis(
    session: Session,
    action: Action,
    *,
    priority: Priority | None = None,
) -> Hypothesis | None:
    hypothesis_id = action.hypothesis_id
    if hypothesis_id is None:
        if priority is None and action.priority_id is not None:
            priority = session.scalar(
                select(Priority).where(
                    Priority.priority_id == action.priority_id,
                    Priority.team_id == action.team_id,
                )
            )
        if priority is not None:
            hypothesis_id = priority.hypothesis_id
    if hypothesis_id is None:
        return None
    return session.scalar(
        select(Hypothesis)
        .where(
            Hypothesis.hypothesis_id == hypothesis_id,
            Hypothesis.team_id == action.team_id,
        )
        .with_for_update()
    )


def _can_write_outcome(actor: CurrentIdentity, action: Action) -> bool:
    if actor.role in {Role.ENGINEER, Role.TEAM_MANAGER}:
        return True
    return (
        actor.role is Role.MECHANIC
        and action.assignee_role is Role.MECHANIC
        and (action.assignee_user_id in {None, actor.user_id})
    )
