"""HTTP boundary for team-scoped maintenance records."""

import logging
from collections.abc import Callable
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.errors import (
    InvalidMaintenanceStatusTransitionError,
    MaintenanceContextConflictError,
    MaintenanceRecordLockedError,
    MaintenanceResponsibleConflictError,
)
from raceops.maintenance.models import MaintenanceRecord
from raceops.maintenance.schemas import (
    MaintenanceCancelRequest,
    MaintenanceCausalChainResponse,
    MaintenanceCompleteRequest,
    MaintenanceCreateRequest,
    MaintenancePageResponse,
    MaintenanceResponse,
    MaintenanceUpdateRequest,
)
from raceops.maintenance.services import (
    cancel_maintenance_record,
    complete_maintenance_record,
    create_maintenance_record,
    get_maintenance_causal_chain,
    get_maintenance_record,
    list_maintenance_records,
    start_maintenance_record,
    update_maintenance_record,
)

logger = logging.getLogger("raceops.maintenance")
router = APIRouter()

read_maintenance = require_permission(Permission.READ_MAINTENANCE)
write_maintenance = require_permission(Permission.WRITE_MAINTENANCE)

RESPONSIBLE_CONFLICT_PROBLEM = ProblemDefinition(
    "maintenance-responsible-conflict",
    "Maintenance responsible conflict",
    "maintenance_responsible_conflict",
    "The responsible user is not active in the selected team.",
)
INVALID_STATUS_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-maintenance-status-transition",
    "Invalid maintenance status transition",
    "invalid_maintenance_status_transition",
    "The requested maintenance status transition is not allowed.",
)
RECORD_LOCKED_PROBLEM = ProblemDefinition(
    "maintenance-record-locked",
    "Maintenance record locked",
    "maintenance_record_locked",
    "A maintenance record can only be edited while it is open.",
)
CONTEXT_CONFLICT_PROBLEM = ProblemDefinition(
    "maintenance-context-conflict",
    "Maintenance context conflict",
    "maintenance_context_conflict",
    "The Session, Observation, Action, and Vehicle do not form one valid context.",
)

COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Record or Vehicle not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/maintenance-records",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a maintenance record in the active Team",
    responses={
        **COMMON_RESPONSES,
        409: {
            "model": ProblemDetails,
            "description": "Responsible or causal context conflict.",
        },
    },
)
def create_maintenance_record_endpoint(
    payload: MaintenanceCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_maintenance)],
) -> MaintenanceResponse:
    """Create an OPEN record without accepting lifecycle or ownership fields."""
    try:
        record = create_maintenance_record(
            session,
            actor,
            vehicle_id=payload.vehicle_id,
            responsible_user_id=payload.responsible_user_id,
            session_id=payload.session_id,
            observation_id=payload.observation_id,
            action_id=payload.action_id,
            maintenance_type=payload.maintenance_type,
            description=payload.description,
        )
    except MaintenanceResponsibleConflictError as error:
        raise ApiProblemError(
            status_code=409,
            definition=RESPONSIBLE_CONFLICT_PROBLEM,
        ) from error
    except MaintenanceContextConflictError as error:
        raise _context_conflict() from error
    logger.info(
        "maintenance record created",
        extra={
            "event": "maintenance.created",
            "maintenance_id": str(record.maintenance_id),
            "vehicle_id": str(record.vehicle_id),
            "team_id": str(actor.team_id),
        },
    )
    return MaintenanceResponse.from_model(record)


@router.get(
    "/maintenance-records",
    tags=["maintenance"],
    response_model=MaintenancePageResponse,
    summary="List maintenance records in the active Team",
    responses=COMMON_RESPONSES,
)
def list_maintenance_records_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_maintenance)],
    vehicle_id: Annotated[UUID | None, Query()] = None,
    session_id: Annotated[UUID | None, Query()] = None,
    maintenance_type: Annotated[MaintenanceType | None, Query()] = None,
    maintenance_status: Annotated[
        MaintenanceStatus | None, Query(alias="status")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> MaintenancePageResponse:
    """Return a stable page after Team and optional record filtering."""
    records, total = list_maintenance_records(
        session,
        actor,
        vehicle_id=vehicle_id,
        session_id=session_id,
        maintenance_type=maintenance_type,
        status=maintenance_status,
        limit=limit,
        offset=offset,
    )
    return MaintenancePageResponse(
        items=[MaintenanceResponse.from_model(record) for record in records],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/maintenance-records/{maintenance_id}",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    summary="Read one maintenance record from the active Team",
    responses=COMMON_RESPONSES,
)
def get_maintenance_record_endpoint(
    maintenance_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_maintenance)],
) -> MaintenanceResponse:
    """Return one authorized record without revealing foreign resources."""
    return MaintenanceResponse.from_model(
        get_maintenance_record(session, actor, maintenance_id)
    )


@router.get(
    "/maintenance-records/{maintenance_id}/causal-chain",
    tags=["maintenance"],
    response_model=MaintenanceCausalChainResponse,
    summary="Read the explicit causal context of one maintenance record",
    responses=COMMON_RESPONSES,
)
def get_maintenance_causal_chain_endpoint(
    maintenance_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_maintenance)],
) -> MaintenanceCausalChainResponse:
    """Traverse only references explicitly stored on an authorized record."""
    record, race_session, observation, action = get_maintenance_causal_chain(
        session, actor, maintenance_id
    )
    return MaintenanceCausalChainResponse.from_models(
        record,
        race_session,
        observation,
        action,
        actor.role,
    )


@router.patch(
    "/maintenance-records/{maintenance_id}",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    summary="Edit one OPEN maintenance record",
    responses={
        **COMMON_RESPONSES,
        409: {
            "model": ProblemDetails,
            "description": "Responsible conflict or non-open record.",
        },
    },
)
def update_maintenance_record_endpoint(
    maintenance_id: UUID,
    payload: MaintenanceUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_maintenance)],
) -> MaintenanceResponse:
    """Edit only responsible, type, and description while status is OPEN."""
    try:
        record = update_maintenance_record(
            session,
            actor,
            maintenance_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except MaintenanceResponsibleConflictError as error:
        raise _responsible_conflict() from error
    except MaintenanceRecordLockedError as error:
        raise _record_locked() from error
    _log_lifecycle_event("maintenance.updated", record, actor)
    return MaintenanceResponse.from_model(record)


@router.post(
    "/maintenance-records/{maintenance_id}/start",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    summary="Start one OPEN maintenance intervention",
    responses={
        **COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def start_maintenance_record_endpoint(
    maintenance_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_maintenance)],
) -> MaintenanceResponse:
    """Move an OPEN record to IN_PROGRESS using a server timestamp."""
    record = _transition_without_payload(
        start_maintenance_record,
        session,
        actor,
        maintenance_id,
    )
    _log_lifecycle_event("maintenance.started", record, actor)
    return MaintenanceResponse.from_model(record)


@router.post(
    "/maintenance-records/{maintenance_id}/complete",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    summary="Complete one maintenance intervention",
    responses={
        **COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def complete_maintenance_record_endpoint(
    maintenance_id: UUID,
    payload: MaintenanceCompleteRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_maintenance)],
) -> MaintenanceResponse:
    """Finish an OPEN or IN_PROGRESS record with an explicit conclusion."""
    try:
        record = complete_maintenance_record(
            session,
            actor,
            maintenance_id,
            completion_notes=payload.completion_notes,
        )
    except InvalidMaintenanceStatusTransitionError as error:
        raise _invalid_status_transition() from error
    _log_lifecycle_event("maintenance.completed", record, actor)
    return MaintenanceResponse.from_model(record)


@router.post(
    "/maintenance-records/{maintenance_id}/cancel",
    tags=["maintenance"],
    response_model=MaintenanceResponse,
    summary="Cancel one maintenance intervention",
    responses={
        **COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def cancel_maintenance_record_endpoint(
    maintenance_id: UUID,
    payload: MaintenanceCancelRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_maintenance)],
) -> MaintenanceResponse:
    """Cancel an OPEN or IN_PROGRESS record with an explicit reason."""
    try:
        record = cancel_maintenance_record(
            session,
            actor,
            maintenance_id,
            cancellation_reason=payload.cancellation_reason,
        )
    except InvalidMaintenanceStatusTransitionError as error:
        raise _invalid_status_transition() from error
    _log_lifecycle_event("maintenance.cancelled", record, actor)
    return MaintenanceResponse.from_model(record)


def _transition_without_payload(
    transition: Callable[[Session, CurrentIdentity, UUID], MaintenanceRecord],
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
) -> MaintenanceRecord:
    try:
        return transition(session, actor, maintenance_id)
    except InvalidMaintenanceStatusTransitionError as error:
        raise _invalid_status_transition() from error


def _responsible_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=RESPONSIBLE_CONFLICT_PROBLEM)


def _invalid_status_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=INVALID_STATUS_TRANSITION_PROBLEM,
    )


def _record_locked() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=RECORD_LOCKED_PROBLEM)


def _context_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=CONTEXT_CONFLICT_PROBLEM)


def _log_lifecycle_event(
    event: str,
    record: MaintenanceRecord,
    actor: CurrentIdentity,
) -> None:
    logger.info(
        "maintenance lifecycle changed",
        extra={
            "event": event,
            "maintenance_id": str(record.maintenance_id),
            "maintenance_status": record.status.value,
            "team_id": str(actor.team_id),
        },
    )
