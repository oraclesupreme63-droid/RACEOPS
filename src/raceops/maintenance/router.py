"""HTTP boundary for team-scoped maintenance records."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.errors import MaintenanceResponsibleConflictError
from raceops.maintenance.schemas import (
    MaintenanceCreateRequest,
    MaintenancePageResponse,
    MaintenanceResponse,
)
from raceops.maintenance.services import (
    create_maintenance_record,
    get_maintenance_record,
    list_maintenance_records,
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
        409: {"model": ProblemDetails, "description": "Responsible conflict."},
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
            maintenance_type=payload.maintenance_type,
            description=payload.description,
        )
    except MaintenanceResponsibleConflictError as error:
        raise ApiProblemError(
            status_code=409,
            definition=RESPONSIBLE_CONFLICT_PROBLEM,
        ) from error
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
