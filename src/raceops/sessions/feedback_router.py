"""HTTP boundary for Session Driver Feedback."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.feedback_schemas import (
    FeedbackCreateRequest,
    FeedbackPageResponse,
    FeedbackResponse,
    FeedbackUpdateRequest,
)
from raceops.sessions.feedback_services import (
    create_driver_feedback,
    get_driver_feedback,
    list_driver_feedback,
    update_driver_feedback,
)

logger = logging.getLogger("raceops.feedback")
router = APIRouter()

read_feedback = require_permission(Permission.READ_DRIVER_FEEDBACK)
create_feedback = require_permission(Permission.CREATE_DRIVER_FEEDBACK)
update_feedback = require_permission(Permission.UPDATE_DRIVER_FEEDBACK)

FEEDBACK_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Feedback not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/sessions/{session_id}/feedback",
    tags=["driver-feedback"],
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    responses=FEEDBACK_COMMON_RESPONSES,
)
def create_feedback_endpoint(
    session_id: UUID,
    payload: FeedbackCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(create_feedback)],
) -> FeedbackResponse:
    """Record own or verbally communicated feedback for the assigned Driver."""
    feedback = create_driver_feedback(
        session,
        actor,
        session_id,
        values=payload.model_dump(),
    )
    logger.info(
        "driver feedback created",
        extra={
            "event": "driver_feedback.created",
            "feedback_id": str(feedback.feedback_id),
            "session_id": str(session_id),
            "team_id": str(actor.team_id),
        },
    )
    return FeedbackResponse.from_model(feedback)


@router.get(
    "/sessions/{session_id}/feedback",
    tags=["driver-feedback"],
    response_model=FeedbackPageResponse,
    responses=FEEDBACK_COMMON_RESPONSES,
)
def list_feedback_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_feedback)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FeedbackPageResponse:
    """Return the visible feedback page for one authorized Session."""
    feedback, total = list_driver_feedback(
        session, actor, session_id, limit=limit, offset=offset
    )
    return FeedbackPageResponse(
        items=[FeedbackResponse.from_model(item) for item in feedback],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/feedback/{feedback_id}",
    tags=["driver-feedback"],
    response_model=FeedbackResponse,
    responses=FEEDBACK_COMMON_RESPONSES,
)
def get_feedback_endpoint(
    feedback_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_feedback)],
) -> FeedbackResponse:
    """Read one record after Team, relationship, and visibility checks."""
    return FeedbackResponse.from_model(get_driver_feedback(session, actor, feedback_id))


@router.patch(
    "/feedback/{feedback_id}",
    tags=["driver-feedback"],
    response_model=FeedbackResponse,
    responses=FEEDBACK_COMMON_RESPONSES,
)
def update_feedback_endpoint(
    feedback_id: UUID,
    payload: FeedbackUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(update_feedback)],
) -> FeedbackResponse:
    """Update an Engineer-authorized record or the Driver's own record."""
    feedback = update_driver_feedback(
        session,
        actor,
        feedback_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return FeedbackResponse.from_model(feedback)
