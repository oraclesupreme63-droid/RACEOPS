"""HTTP boundary for RaceOps operational resources."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.operations.drivers import (
    create_driver,
    get_driver,
    list_drivers,
    set_driver_status,
    update_driver,
)
from raceops.operations.enums import DriverStatus
from raceops.operations.errors import DriverUserConflictError
from raceops.operations.schemas import (
    DriverCreateRequest,
    DriverPageResponse,
    DriverResponse,
    DriverUpdateRequest,
)

logger = logging.getLogger("raceops.operations.drivers")
router = APIRouter(tags=["drivers"])

read_drivers = require_permission(Permission.READ_DRIVERS)
manage_drivers = require_permission(Permission.MANAGE_DRIVERS)

DRIVER_USER_CONFLICT_PROBLEM = ProblemDefinition(
    "driver-user-conflict",
    "Driver user conflict",
    "driver_user_conflict",
    "The requested user cannot be linked to this driver.",
)

COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Driver not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/drivers",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Driver in the active Team",
    responses={
        **COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "User link conflict."},
    },
)
def create_driver_endpoint(
    payload: DriverCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_drivers)],
) -> DriverResponse:
    """Create a Driver without accepting client-controlled ownership."""
    try:
        driver = create_driver(
            session,
            actor,
            display_name=payload.display_name,
            user_id=payload.user_id,
        )
    except DriverUserConflictError as error:
        raise _driver_user_conflict() from error
    logger.info(
        "driver created",
        extra={
            "event": "driver.created",
            "driver_id": str(driver.driver_id),
            "team_id": str(actor.team_id),
        },
    )
    return DriverResponse.from_model(driver)


@router.get(
    "/drivers",
    response_model=DriverPageResponse,
    summary="List authorized Drivers in the active Team",
    responses=COMMON_RESPONSES,
)
def list_drivers_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_drivers)],
    driver_status: Annotated[DriverStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DriverPageResponse:
    """Return a stable page after Team and relationship filtering."""
    drivers, total = list_drivers(
        session,
        actor,
        status=driver_status,
        limit=limit,
        offset=offset,
    )
    return DriverPageResponse(
        items=[DriverResponse.from_model(driver) for driver in drivers],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/drivers/{driver_id}",
    response_model=DriverResponse,
    summary="Read one authorized Driver",
    responses=COMMON_RESPONSES,
)
def get_driver_endpoint(
    driver_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_drivers)],
) -> DriverResponse:
    """Return one same-Team Driver or the Driver actor's own profile."""
    return DriverResponse.from_model(get_driver(session, actor, driver_id))


@router.patch(
    "/drivers/{driver_id}",
    response_model=DriverResponse,
    summary="Update permitted Driver fields",
    responses={
        **COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "User link conflict."},
    },
)
def update_driver_endpoint(
    driver_id: UUID,
    payload: DriverUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_drivers)],
) -> DriverResponse:
    """Update name or optional User link while preserving ownership."""
    try:
        driver = update_driver(
            session,
            actor,
            driver_id,
            change_display_name="display_name" in payload.model_fields_set,
            display_name=payload.display_name,
            change_user_id="user_id" in payload.model_fields_set,
            user_id=payload.user_id,
        )
    except DriverUserConflictError as error:
        raise _driver_user_conflict() from error
    logger.info(
        "driver updated",
        extra={
            "event": "driver.updated",
            "driver_id": str(driver.driver_id),
            "team_id": str(actor.team_id),
        },
    )
    return DriverResponse.from_model(driver)


@router.post(
    "/drivers/{driver_id}/activate",
    response_model=DriverResponse,
    summary="Activate a Driver",
    responses=COMMON_RESPONSES,
)
def activate_driver_endpoint(
    driver_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_drivers)],
) -> DriverResponse:
    """Mark a preserved Driver as available for future assignment."""
    return _change_driver_status(
        session,
        actor,
        driver_id,
        DriverStatus.ACTIVE,
    )


@router.post(
    "/drivers/{driver_id}/deactivate",
    response_model=DriverResponse,
    summary="Deactivate a Driver",
    responses=COMMON_RESPONSES,
)
def deactivate_driver_endpoint(
    driver_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_drivers)],
) -> DriverResponse:
    """Deactivate a Driver without deleting history or identity links."""
    return _change_driver_status(
        session,
        actor,
        driver_id,
        DriverStatus.INACTIVE,
    )


def _change_driver_status(
    session: Session,
    actor: CurrentIdentity,
    driver_id: UUID,
    driver_status: DriverStatus,
) -> DriverResponse:
    driver = set_driver_status(session, actor, driver_id, driver_status)
    logger.info(
        "driver status changed",
        extra={
            "event": "driver.status_changed",
            "driver_id": str(driver.driver_id),
            "team_id": str(actor.team_id),
            "driver_status": driver.status.value,
        },
    )
    return DriverResponse.from_model(driver)


def _driver_user_conflict() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=DRIVER_USER_CONFLICT_PROBLEM,
    )
