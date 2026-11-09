"""Application services for team-scoped Vehicle management."""

from collections.abc import Mapping, Set
from types import MappingProxyType
from typing import Final
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.operations.enums import VehicleStatus
from raceops.operations.errors import (
    InvalidVehicleStatusTransitionError,
    VehicleIdentifierConflictError,
)
from raceops.operations.models import Vehicle

VEHICLE_STATUS_TRANSITIONS: Final[Mapping[VehicleStatus, Set[VehicleStatus]]] = (
    MappingProxyType(
        {
            VehicleStatus.READY: frozenset(
                {
                    VehicleStatus.MAINTENANCE,
                    VehicleStatus.UNAVAILABLE,
                    VehicleStatus.RETIRED,
                }
            ),
            VehicleStatus.MAINTENANCE: frozenset(
                {
                    VehicleStatus.READY,
                    VehicleStatus.UNAVAILABLE,
                    VehicleStatus.RETIRED,
                }
            ),
            VehicleStatus.UNAVAILABLE: frozenset(
                {
                    VehicleStatus.READY,
                    VehicleStatus.MAINTENANCE,
                    VehicleStatus.RETIRED,
                }
            ),
            VehicleStatus.RETIRED: frozenset(),
        }
    )
)


def create_vehicle(
    session: Session,
    actor: CurrentIdentity,
    *,
    identifier: str,
) -> Vehicle:
    """Create one READY Vehicle owned by the actor's selected Team."""
    vehicle = Vehicle(team_id=actor.team_id, identifier=identifier)
    session.add(vehicle)
    _commit_vehicle(session, vehicle)
    return vehicle


def list_vehicles(
    session: Session,
    actor: CurrentIdentity,
    *,
    status: VehicleStatus | None,
    limit: int,
    offset: int,
) -> tuple[list[Vehicle], int]:
    """List Vehicles inside the actor's selected Team."""
    filters = [Vehicle.team_id == actor.team_id]
    if status is not None:
        filters.append(Vehicle.status == status)

    total = session.scalar(select(func.count()).select_from(Vehicle).where(*filters))
    statement = (
        select(Vehicle)
        .where(*filters)
        .order_by(Vehicle.created_at, Vehicle.vehicle_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_vehicle(
    session: Session,
    actor: CurrentIdentity,
    vehicle_id: UUID,
) -> Vehicle:
    """Read one same-Team Vehicle without revealing foreign resources."""
    vehicle = session.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_id == vehicle_id,
            Vehicle.team_id == actor.team_id,
        )
    )
    if vehicle is None:
        raise ResourceNotFoundError
    return vehicle


def update_vehicle(
    session: Session,
    actor: CurrentIdentity,
    vehicle_id: UUID,
    *,
    identifier: str,
) -> Vehicle:
    """Update the Vehicle identifier while preserving Team ownership."""
    vehicle = _get_vehicle_for_update(session, actor.team_id, vehicle_id)
    vehicle.identifier = identifier
    _commit_vehicle(session, vehicle)
    return vehicle


def transition_vehicle_status(
    session: Session,
    actor: CurrentIdentity,
    vehicle_id: UUID,
    target_status: VehicleStatus,
) -> Vehicle:
    """Apply one explicit valid transition without changing invalid records."""
    vehicle = _get_vehicle_for_update(session, actor.team_id, vehicle_id)
    if target_status not in VEHICLE_STATUS_TRANSITIONS[vehicle.status]:
        session.rollback()
        raise InvalidVehicleStatusTransitionError

    vehicle.status = target_status
    session.commit()
    session.refresh(vehicle)
    return vehicle


def is_vehicle_assignable(status: VehicleStatus) -> bool:
    """Return the Phase 8 assignment predicate without mutating state."""
    return status is VehicleStatus.READY


def _get_vehicle_for_update(
    session: Session,
    team_id: UUID,
    vehicle_id: UUID,
) -> Vehicle:
    vehicle = session.scalar(
        select(Vehicle)
        .where(
            Vehicle.vehicle_id == vehicle_id,
            Vehicle.team_id == team_id,
        )
        .with_for_update()
    )
    if vehicle is None:
        raise ResourceNotFoundError
    return vehicle


def _commit_vehicle(session: Session, vehicle: Vehicle) -> None:
    try:
        session.commit()
        session.refresh(vehicle)
    except IntegrityError as error:
        session.rollback()
        raise VehicleIdentifierConflictError from error
