"""HTTP boundary for optional Session Condition Snapshots."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.condition_schemas import (
    ConditionCreateRequest,
    ConditionResponse,
    ConditionUpdateRequest,
)
from raceops.sessions.condition_services import (
    create_condition_snapshot,
    get_condition_snapshot,
    update_condition_snapshot,
)
from raceops.sessions.errors import (
    ConditionSnapshotExistsError,
    InvalidConditionSnapshotError,
)

router = APIRouter()
read_conditions = require_permission(Permission.READ_CONDITIONS)
write_conditions = require_permission(Permission.WRITE_CONDITIONS)

CONDITION_EXISTS_PROBLEM = ProblemDefinition(
    "condition-snapshot-exists",
    "Condition Snapshot already exists",
    "condition_snapshot_exists",
    "This Session already has its single Condition Snapshot.",
)
INVALID_CONDITION_PROBLEM = ProblemDefinition(
    "invalid-condition-snapshot",
    "Invalid Condition Snapshot",
    "invalid_condition_snapshot",
    "Known measurements require units and the snapshot cannot be empty.",
)
CONDITION_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Snapshot not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/sessions/{session_id}/conditions",
    tags=["conditions"],
    response_model=ConditionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**CONDITION_COMMON_RESPONSES, 409: {"model": ProblemDetails}},
)
def create_conditions_endpoint(
    session_id: UUID,
    payload: ConditionCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_conditions)],
) -> ConditionResponse:
    """Create the single sparse snapshot using only client-known fields."""
    try:
        snapshot = create_condition_snapshot(
            session,
            actor,
            session_id,
            values=payload.model_dump(),
        )
    except ConditionSnapshotExistsError as error:
        raise _condition_exists() from error
    return ConditionResponse.from_model(snapshot)


@router.get(
    "/sessions/{session_id}/conditions",
    tags=["conditions"],
    response_model=ConditionResponse,
    responses=CONDITION_COMMON_RESPONSES,
)
def get_conditions_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_conditions)],
) -> ConditionResponse:
    """Read one snapshot after Team and Driver relationship filtering."""
    return ConditionResponse.from_model(
        get_condition_snapshot(session, actor, session_id)
    )


@router.patch(
    "/sessions/{session_id}/conditions",
    tags=["conditions"],
    response_model=ConditionResponse,
    responses=CONDITION_COMMON_RESPONSES,
)
def update_conditions_endpoint(
    session_id: UUID,
    payload: ConditionUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_conditions)],
) -> ConditionResponse:
    """Update known fields without interpreting missing data as zero."""
    try:
        snapshot = update_condition_snapshot(
            session,
            actor,
            session_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except InvalidConditionSnapshotError as error:
        raise _invalid_condition() from error
    return ConditionResponse.from_model(snapshot)


def _condition_exists() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=CONDITION_EXISTS_PROBLEM)


def _invalid_condition() -> ApiProblemError:
    return ApiProblemError(status_code=422, definition=INVALID_CONDITION_PROBLEM)
