"""HTTP boundary for Action evaluation and authorized learning chains."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.learning.decision_schemas import ActionResponse, PriorityResponse
from raceops.learning.errors import (
    ActionOutcomeConflictError,
    InvalidActionOutcomeError,
)
from raceops.learning.outcome_schemas import (
    ActionEvaluationResponse,
    ActionOutcomeCreateRequest,
    ActionOutcomeResponse,
    LearningChainResponse,
)
from raceops.learning.outcome_services import (
    create_action_outcome,
    get_action_evaluation,
    get_learning_chain,
)
from raceops.learning.schemas import HypothesisResponse, SessionAnalysisResponse

logger = logging.getLogger("raceops.outcomes")
router = APIRouter()

read_actions = require_permission(Permission.READ_ACTIONS)
write_outcomes = require_permission(Permission.WRITE_ACTION_OUTCOMES)

INVALID_OUTCOME_PROBLEM = ProblemDefinition(
    "invalid-action-outcome",
    "Invalid Action Outcome",
    "invalid_action_outcome",
    "The Action, evaluation Session, or conclusion cannot form this Outcome.",
)
OUTCOME_CONFLICT_PROBLEM = ProblemDefinition(
    "action-outcome-conflict",
    "Action Outcome conflict",
    "action_outcome_conflict",
    "This Action already has its P0 Outcome.",
)
OUTCOME_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Resource not found."},
    409: {"model": ProblemDetails, "description": "Invalid or duplicate Outcome."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/actions/{action_id}/outcome",
    tags=["outcomes"],
    response_model=ActionOutcomeResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=OUTCOME_RESPONSES,
)
def create_action_outcome_endpoint(
    action_id: UUID,
    payload: ActionOutcomeCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_outcomes)],
) -> ActionOutcomeResponse:
    try:
        outcome = create_action_outcome(
            session,
            actor,
            action_id,
            evaluation_session_id=payload.evaluation_session_id,
            classification=payload.classification,
            public_conclusion=payload.public_conclusion,
            confidential_conclusion=payload.confidential_conclusion,
            concluded_hypothesis_status=payload.concluded_hypothesis_status,
        )
    except InvalidActionOutcomeError as error:
        raise _invalid_outcome() from error
    except ActionOutcomeConflictError as error:
        raise _outcome_conflict() from error
    logger.info(
        "action outcome created",
        extra={
            "event": "action.outcome_created",
            "action_id": str(action_id),
            "outcome_id": str(outcome.outcome_id),
            "team_id": str(actor.team_id),
        },
    )
    return ActionOutcomeResponse.from_model(outcome, actor.role)


@router.get(
    "/actions/{action_id}/outcome",
    tags=["outcomes"],
    response_model=ActionEvaluationResponse,
    response_model_exclude_none=True,
    responses=OUTCOME_RESPONSES,
)
def get_action_outcome_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_actions)],
) -> ActionEvaluationResponse:
    action = get_action_evaluation(session, actor, action_id)
    return ActionEvaluationResponse.from_action(action, actor.role)


@router.get(
    "/actions/{action_id}/learning-chain",
    tags=["outcomes"],
    response_model=LearningChainResponse,
    response_model_exclude_none=True,
    responses=OUTCOME_RESPONSES,
)
def get_learning_chain_endpoint(
    action_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_actions)],
) -> LearningChainResponse:
    action, priority, hypothesis, analysis = get_learning_chain(
        session, actor, action_id
    )
    return LearningChainResponse(
        action=ActionResponse.from_model(action, actor.role),
        priority=(
            PriorityResponse.from_model(priority, actor.role)
            if priority is not None
            else None
        ),
        hypothesis=(
            HypothesisResponse.from_model(hypothesis)
            if hypothesis is not None
            else None
        ),
        analysis=(
            SessionAnalysisResponse.from_model(analysis)
            if analysis is not None
            else None
        ),
        evaluation=ActionEvaluationResponse.from_action(action, actor.role),
    )


def _invalid_outcome() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=INVALID_OUTCOME_PROBLEM)


def _outcome_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=OUTCOME_CONFLICT_PROBLEM)
