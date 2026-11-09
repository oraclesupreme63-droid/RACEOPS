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
from raceops.operations.enums import DriverStatus, VehicleStatus
from raceops.operations.errors import (
    DriverUserConflictError,
    InvalidVehicleStatusTransitionError,
    VehicleIdentifierConflictError,
)
from raceops.operations.schemas import (
    DriverCreateRequest,
    DriverPageResponse,
    DriverResponse,
    DriverUpdateRequest,
    VehicleCreateRequest,
    VehiclePageResponse,
    VehicleResponse,
    VehicleUpdateRequest,
)
from raceops.operations.vehicles import (
    create_vehicle,
    get_vehicle,
    list_vehicles,
    transition_vehicle_status,
    update_vehicle,
)

driver_logger = logging.getLogger("raceops.operations.drivers")
vehicle_logger = logging.getLogger("raceops.operations.vehicles")
router = APIRouter()

read_drivers = require_permission(Permission.READ_DRIVERS)
manage_drivers = require_permission(Permission.MANAGE_DRIVERS)
read_vehicles = require_permission(Permission.READ_VEHICLES)
manage_vehicles = require_permission(Permission.MANAGE_VEHICLES)

DRIVER_USER_CONFLICT_PROBLEM = ProblemDefinition(
    "driver-user-conflict",
    "Driver user conflict",
    "driver_user_conflict",
    "The requested user cannot be linked to this driver.",
)
VEHICLE_IDENTIFIER_CONFLICT_PROBLEM = ProblemDefinition(
    "vehicle-identifier-conflict",
    "Vehicle identifier conflict",
    "vehicle_identifier_conflict",
    "The requested vehicle identifier is already in use by this team.",
)
INVALID_VEHICLE_STATUS_TRANSITION_PROBLEM = ProblemDefinition(
    "invalid-vehicle-status-transition",
    "Invalid vehicle status transition",
    "invalid_vehicle_status_transition",
    "The requested vehicle status transition is not allowed.",
)

DRIVER_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Driver not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}
VEHICLE_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Vehicle not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/drivers",
    tags=["drivers"],
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Driver in the active Team",
    responses={
        **DRIVER_COMMON_RESPONSES,
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
    driver_logger.info(
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
    tags=["drivers"],
    response_model=DriverPageResponse,
    summary="List authorized Drivers in the active Team",
    responses=DRIVER_COMMON_RESPONSES,
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
    tags=["drivers"],
    response_model=DriverResponse,
    summary="Read one authorized Driver",
    responses=DRIVER_COMMON_RESPONSES,
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
    tags=["drivers"],
    response_model=DriverResponse,
    summary="Update permitted Driver fields",
    responses={
        **DRIVER_COMMON_RESPONSES,
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
    driver_logger.info(
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
    tags=["drivers"],
    response_model=DriverResponse,
    summary="Activate a Driver",
    responses=DRIVER_COMMON_RESPONSES,
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
    tags=["drivers"],
    response_model=DriverResponse,
    summary="Deactivate a Driver",
    responses=DRIVER_COMMON_RESPONSES,
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
    driver_logger.info(
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


@router.post(
    "/vehicles",
    tags=["vehicles"],
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Vehicle in the active Team",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Identifier conflict."},
    },
)
def create_vehicle_endpoint(
    payload: VehicleCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Create a READY Vehicle without client-controlled ownership or status."""
    try:
        vehicle = create_vehicle(session, actor, identifier=payload.identifier)
    except VehicleIdentifierConflictError as error:
        raise _vehicle_identifier_conflict() from error
    vehicle_logger.info(
        "vehicle created",
        extra={
            "event": "vehicle.created",
            "vehicle_id": str(vehicle.vehicle_id),
            "team_id": str(actor.team_id),
        },
    )
    return VehicleResponse.from_model(vehicle)


@router.get(
    "/vehicles",
    tags=["vehicles"],
    response_model=VehiclePageResponse,
    summary="List Vehicles in the active Team",
    responses=VEHICLE_COMMON_RESPONSES,
)
def list_vehicles_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_vehicles)],
    vehicle_status: Annotated[VehicleStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> VehiclePageResponse:
    """Return a stable page after Team and optional status filtering."""
    vehicles, total = list_vehicles(
        session,
        actor,
        status=vehicle_status,
        limit=limit,
        offset=offset,
    )
    return VehiclePageResponse(
        items=[VehicleResponse.from_model(vehicle) for vehicle in vehicles],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/vehicles/{vehicle_id}",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Read one same-Team Vehicle",
    responses=VEHICLE_COMMON_RESPONSES,
)
def get_vehicle_endpoint(
    vehicle_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_vehicles)],
) -> VehicleResponse:
    """Return one Vehicle only inside the actor's active Team."""
    return VehicleResponse.from_model(get_vehicle(session, actor, vehicle_id))


@router.patch(
    "/vehicles/{vehicle_id}",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Update a Vehicle identifier",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Identifier conflict."},
    },
)
def update_vehicle_endpoint(
    vehicle_id: UUID,
    payload: VehicleUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Rename a Vehicle; lifecycle changes use explicit command endpoints."""
    try:
        vehicle = update_vehicle(
            session,
            actor,
            vehicle_id,
            identifier=payload.identifier,
        )
    except VehicleIdentifierConflictError as error:
        raise _vehicle_identifier_conflict() from error
    vehicle_logger.info(
        "vehicle updated",
        extra={
            "event": "vehicle.updated",
            "vehicle_id": str(vehicle.vehicle_id),
            "team_id": str(actor.team_id),
        },
    )
    return VehicleResponse.from_model(vehicle)


@router.post(
    "/vehicles/{vehicle_id}/mark-ready",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Mark a Vehicle ready",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def mark_vehicle_ready_endpoint(
    vehicle_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Explicitly return a non-retired Vehicle to READY."""
    return _change_vehicle_status(session, actor, vehicle_id, VehicleStatus.READY)


@router.post(
    "/vehicles/{vehicle_id}/mark-maintenance",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Mark a Vehicle in maintenance",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def mark_vehicle_maintenance_endpoint(
    vehicle_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Explicitly mark a non-retired Vehicle as in maintenance."""
    return _change_vehicle_status(
        session,
        actor,
        vehicle_id,
        VehicleStatus.MAINTENANCE,
    )


@router.post(
    "/vehicles/{vehicle_id}/mark-unavailable",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Mark a Vehicle unavailable",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def mark_vehicle_unavailable_endpoint(
    vehicle_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Explicitly remove a non-retired Vehicle from availability."""
    return _change_vehicle_status(
        session,
        actor,
        vehicle_id,
        VehicleStatus.UNAVAILABLE,
    )


@router.post(
    "/vehicles/{vehicle_id}/retire",
    tags=["vehicles"],
    response_model=VehicleResponse,
    summary="Retire a Vehicle permanently",
    responses={
        **VEHICLE_COMMON_RESPONSES,
        409: {"model": ProblemDetails, "description": "Invalid transition."},
    },
)
def retire_vehicle_endpoint(
    vehicle_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(manage_vehicles)],
) -> VehicleResponse:
    """Move a Vehicle to its terminal RETIRED state."""
    return _change_vehicle_status(session, actor, vehicle_id, VehicleStatus.RETIRED)


def _change_vehicle_status(
    session: Session,
    actor: CurrentIdentity,
    vehicle_id: UUID,
    target_status: VehicleStatus,
) -> VehicleResponse:
    try:
        vehicle = transition_vehicle_status(
            session,
            actor,
            vehicle_id,
            target_status,
        )
    except InvalidVehicleStatusTransitionError as error:
        raise _invalid_vehicle_status_transition() from error
    vehicle_logger.info(
        "vehicle status changed",
        extra={
            "event": "vehicle.status_changed",
            "vehicle_id": str(vehicle.vehicle_id),
            "team_id": str(actor.team_id),
            "vehicle_status": vehicle.status.value,
        },
    )
    return VehicleResponse.from_model(vehicle)


def _vehicle_identifier_conflict() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=VEHICLE_IDENTIFIER_CONFLICT_PROBLEM,
    )


def _invalid_vehicle_status_transition() -> ApiProblemError:
    return ApiProblemError(
        status_code=409,
        definition=INVALID_VEHICLE_STATUS_TRANSITION_PROBLEM,
    )
