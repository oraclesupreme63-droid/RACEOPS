"""HTTP boundary for priorities and Action execution."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.learning.decision_schemas import (
    ActionCancellationRequest,
    ActionCreateRequest,
    ActionPageResponse,
    ActionResponse,
    PriorityCreateRequest,
    PriorityPageResponse,
    PriorityResponse,
    PriorityUpdateRequest,
)
from raceops.learning.decision_services import (
    create_action,
    create_priority,
    get_action,
    get_priority,
    list_actions,
    list_priorities,
    transition_action,
    update_priority,
)
from raceops.learning.enums import ActionStatus
from raceops.learning.errors import (
    InvalidActionStatusTransitionError,
    InvalidDecisionContextError,
    PriorityScopeConflictError,
)

logger = logging.getLogger("raceops.decisions")
router = APIRouter()

read_priorities = require_permission(Permission.READ_PRIORITIES)
create_priorities = require_permission(Permission.WRITE_PRIORITIES)
update_priorities = require_permission(Permission.UPDATE_PRIORITIES)
read_actions = require_permission(Permission.READ_ACTIONS)
create_actions = require_permission(Permission.CREATE_ACTIONS)
update_actions = require_permission(Permission.UPDATE_ASSIGNED_ACTIONS)

PRIORITY_SCOPE_CONFLICT_PROBLEM = ProblemDefinition(
    "priority-scope-conflict",
    "Priority scope conflict",
    "priority_scope_conflict",
    "The selected main-priority rank is unavailable or the scope already has three.",
)
INVALID_DECISION_CONTEXT_PROBLEM = ProblemDefinition(
    "invalid-decision-context",
    "Invalid decision context",
    "invalid_decision_context",
    "The selected target, motivation, recipient, or assignee is not valid.",
)
INVALID_ACTION_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-action-status-transition",
    "Invalid Action status transition",
    "invalid_action_status_transition",
    "The requested Action execution transition is not allowed.",
)

DECISION_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Resource not found."},
    409: {"model": ProblemDetails, "description": "State or scope conflict."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/sessions/{source_session_id}/priorities",
    tags=["priorities"],
    response_model=PriorityResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=DECISION_COMMON_RESPONSES,
)
def create_priority_endpoint(
    source_session_id: UUID,
    payload: PriorityCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(create_priorities)],
) -> PriorityResponse:
    try:
        priority = create_priority(
            session,
            actor,
            source_session_id=source_session_id,
            target_intent=payload.target_intent,
            target_session_id=payload.target_session_id,
            hypothesis_id=payload.hypothesis_id,
            recipient_role=payload.recipient_role,
            recipient_user_id=payload.recipient_user_id,
            description=payload.description,
            is_main=payload.is_main,
            rank=payload.rank,
        )
    except PriorityScopeConflictError as error:
        raise _priority_conflict() from error
    except InvalidDecisionContextError as error:
        raise _invalid_context() from error
    return PriorityResponse.from_model(priority, actor.role)


@router.get(
    "/sessions/{source_session_id}/priorities",
    tags=["priorities"],
    response_model=PriorityPageResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def list_priorities_endpoint(
    source_session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_priorities)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PriorityPageResponse:
    priorities, total = list_priorities(
        session,
        actor,
        source_session_id=source_session_id,
        limit=limit,
        offset=offset,
    )
    return PriorityPageResponse(
        items=[PriorityResponse.from_model(item, actor.role) for item in priorities],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/priorities/{priority_id}",
    tags=["priorities"],
    response_model=PriorityResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def get_priority_endpoint(
    priority_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_priorities)],
) -> PriorityResponse:
    return PriorityResponse.from_model(
        get_priority(session, actor, priority_id), actor.role
    )


@router.patch(
    "/priorities/{priority_id}",
    tags=["priorities"],
    response_model=PriorityResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def update_priority_endpoint(
    priority_id: UUID,
    payload: PriorityUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_priorities)],
) -> PriorityResponse:
    try:
        priority = update_priority(
            session,
            actor,
            priority_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except PriorityScopeConflictError as error:
        raise _priority_conflict() from error
    return PriorityResponse.from_model(priority, actor.role)


@router.post(
    "/sessions/{source_session_id}/actions",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=DECISION_COMMON_RESPONSES,
)
def create_action_endpoint(
    source_session_id: UUID,
    payload: ActionCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(create_actions)],
) -> ActionResponse:
    try:
        action = create_action(
            session,
            actor,
            source_session_id=source_session_id,
            target_intent=payload.target_intent,
            target_session_id=payload.target_session_id,
            hypothesis_id=payload.hypothesis_id,
            priority_id=payload.priority_id,
            assignee_user_id=payload.assignee_user_id,
            assignee_role=payload.assignee_role,
            action_type=payload.action_type,
            public_summary=payload.public_summary,
            confidential_detail=payload.confidential_detail,
        )
    except InvalidDecisionContextError as error:
        raise _invalid_context() from error
    logger.info(
        "action created",
        extra={
            "event": "action.created",
            "action_id": str(action.action_id),
            "team_id": str(actor.team_id),
        },
    )
    return ActionResponse.from_model(action, actor.role)


@router.get(
    "/sessions/{source_session_id}/actions",
    tags=["actions"],
    response_model=ActionPageResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def list_actions_endpoint(
    source_session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_actions)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ActionPageResponse:
    actions, total = list_actions(
        session,
        actor,
        source_session_id=source_session_id,
        limit=limit,
        offset=offset,
    )
    return ActionPageResponse(
        items=[ActionResponse.from_model(item, actor.role) for item in actions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/actions/{action_id}",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def get_action_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_actions)],
) -> ActionResponse:
    return ActionResponse.from_model(get_action(session, actor, action_id), actor.role)


def _transition(
    session: Session,
    actor: CurrentIdentity,
    action_id: UUID,
    target_status: ActionStatus,
    *,
    cancellation_reason: str | None = None,
) -> ActionResponse:
    try:
        action = transition_action(
            session,
            actor,
            action_id,
            target_status,
            cancellation_reason=cancellation_reason,
        )
    except InvalidActionStatusTransitionError as error:
        raise _invalid_transition() from error
    except InvalidDecisionContextError as error:
        raise _invalid_context() from error
    return ActionResponse.from_model(action, actor.role)


@router.post(
    "/actions/{action_id}/plan",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def plan_action_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_actions)],
) -> ActionResponse:
    return _transition(session, actor, action_id, ActionStatus.PLANNED)


@router.post(
    "/actions/{action_id}/start",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def start_action_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_actions)],
) -> ActionResponse:
    return _transition(session, actor, action_id, ActionStatus.IN_PROGRESS)


@router.post(
    "/actions/{action_id}/complete",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def complete_action_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_actions)],
) -> ActionResponse:
    return _transition(session, actor, action_id, ActionStatus.COMPLETED)


@router.post(
    "/actions/{action_id}/cancel",
    tags=["actions"],
    response_model=ActionResponse,
    response_model_exclude_none=True,
    responses=DECISION_COMMON_RESPONSES,
)
def cancel_action_endpoint(
    action_id: UUID,
    payload: ActionCancellationRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_actions)],
) -> ActionResponse:
    return _transition(
        session,
        actor,
        action_id,
        ActionStatus.CANCELLED,
        cancellation_reason=payload.reason,
    )


def _priority_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=PRIORITY_SCOPE_CONFLICT_PROBLEM)


def _invalid_context() -> ApiProblemError:
    return ApiProblemError(status_code=422, definition=INVALID_DECISION_CONTEXT_PROBLEM)


def _invalid_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409, definition=INVALID_ACTION_TRANSITION_PROBLEM
    )
