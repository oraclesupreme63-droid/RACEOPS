"""Application services for team-scoped maintenance records."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from raceops.iam.enums import IdentityStatus
from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import TeamMembership, User
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.errors import MaintenanceResponsibleConflictError
from raceops.maintenance.models import MaintenanceRecord
from raceops.operations.models import Vehicle


def create_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    *,
    vehicle_id: UUID,
    responsible_user_id: UUID,
    maintenance_type: MaintenanceType,
    description: str,
) -> MaintenanceRecord:
    """Create one OPEN record after validating its minimal same-Team context."""
    vehicle = session.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_id == vehicle_id,
            Vehicle.team_id == actor.team_id,
        )
    )
    if vehicle is None:
        raise ResourceNotFoundError

    responsible_membership = session.scalar(
        select(TeamMembership)
        .join(User, TeamMembership.user_id == User.user_id)
        .where(
            TeamMembership.user_id == responsible_user_id,
            TeamMembership.team_id == actor.team_id,
            TeamMembership.status == IdentityStatus.ACTIVE,
            User.status == IdentityStatus.ACTIVE,
        )
        .with_for_update()
    )
    if responsible_membership is None:
        raise MaintenanceResponsibleConflictError

    record = MaintenanceRecord(
        team_id=actor.team_id,
        vehicle_id=vehicle.vehicle_id,
        responsible_user_id=responsible_membership.user_id,
        created_by_user_id=actor.user_id,
        maintenance_type=maintenance_type,
        description=description,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_maintenance_records(
    session: Session,
    actor: CurrentIdentity,
    *,
    vehicle_id: UUID | None,
    maintenance_type: MaintenanceType | None,
    status: MaintenanceStatus | None,
    limit: int,
    offset: int,
) -> tuple[list[MaintenanceRecord], int]:
    """List one stable page after applying Team and optional filters."""
    filters = [MaintenanceRecord.team_id == actor.team_id]
    if vehicle_id is not None:
        filters.append(MaintenanceRecord.vehicle_id == vehicle_id)
    if maintenance_type is not None:
        filters.append(MaintenanceRecord.maintenance_type == maintenance_type)
    if status is not None:
        filters.append(MaintenanceRecord.status == status)

    total = session.scalar(
        select(func.count()).select_from(MaintenanceRecord).where(*filters)
    )
    statement = (
        select(MaintenanceRecord)
        .where(*filters)
        .order_by(
            MaintenanceRecord.created_at.desc(),
            MaintenanceRecord.maintenance_id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
) -> MaintenanceRecord:
    """Read one record from the actor's selected Team without leakage."""
    record = session.scalar(
        select(MaintenanceRecord).where(
            MaintenanceRecord.maintenance_id == maintenance_id,
            MaintenanceRecord.team_id == actor.team_id,
        )
    )
    if record is None:
        raise ResourceNotFoundError
    return record
