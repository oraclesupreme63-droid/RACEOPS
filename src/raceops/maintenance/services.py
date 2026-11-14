"""Application services for team-scoped maintenance records."""

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from raceops.iam.enums import IdentityStatus
from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import TeamMembership, User
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.errors import (
    InvalidMaintenanceStatusTransitionError,
    MaintenanceRecordLockedError,
    MaintenanceResponsibleConflictError,
)
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

    responsible_membership = _require_active_responsible(
        session, actor.team_id, responsible_user_id
    )

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


def update_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
    *,
    changes: Mapping[str, object],
) -> MaintenanceRecord:
    """Edit allowed fields only while the intervention remains OPEN."""
    record = _get_maintenance_for_update(session, actor.team_id, maintenance_id)
    if record.status is not MaintenanceStatus.OPEN:
        session.rollback()
        raise MaintenanceRecordLockedError

    responsible_user_id = changes.get("responsible_user_id")
    if isinstance(responsible_user_id, UUID):
        membership = _require_active_responsible(
            session, actor.team_id, responsible_user_id
        )
        record.responsible_user_id = membership.user_id
    if "maintenance_type" in changes:
        record.maintenance_type = cast(MaintenanceType, changes["maintenance_type"])
    if "description" in changes:
        record.description = cast(str, changes["description"])

    _commit_record(session, record)
    return record


def start_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
) -> MaintenanceRecord:
    """Move one OPEN intervention to IN_PROGRESS with server time."""
    record = _get_maintenance_for_update(session, actor.team_id, maintenance_id)
    if record.status is not MaintenanceStatus.OPEN:
        _reject_transition(session)
    record.status = MaintenanceStatus.IN_PROGRESS
    record.started_at = datetime.now(UTC)
    _commit_record(session, record)
    return record


def complete_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
    *,
    completion_notes: str,
) -> MaintenanceRecord:
    """Complete an OPEN or IN_PROGRESS intervention without releasing Vehicle."""
    record = _get_maintenance_for_update(session, actor.team_id, maintenance_id)
    if record.status not in {MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS}:
        _reject_transition(session)
    record.status = MaintenanceStatus.COMPLETED
    record.completion_notes = completion_notes
    record.completed_at = datetime.now(UTC)
    _commit_record(session, record)
    return record


def cancel_maintenance_record(
    session: Session,
    actor: CurrentIdentity,
    maintenance_id: UUID,
    *,
    cancellation_reason: str,
) -> MaintenanceRecord:
    """Cancel an OPEN or IN_PROGRESS intervention with an explicit reason."""
    record = _get_maintenance_for_update(session, actor.team_id, maintenance_id)
    if record.status not in {MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS}:
        _reject_transition(session)
    record.status = MaintenanceStatus.CANCELLED
    record.cancellation_reason = cancellation_reason
    record.cancelled_at = datetime.now(UTC)
    _commit_record(session, record)
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


def _get_maintenance_for_update(
    session: Session,
    team_id: UUID,
    maintenance_id: UUID,
) -> MaintenanceRecord:
    record = session.scalar(
        select(MaintenanceRecord)
        .where(
            MaintenanceRecord.maintenance_id == maintenance_id,
            MaintenanceRecord.team_id == team_id,
        )
        .with_for_update()
    )
    if record is None:
        raise ResourceNotFoundError
    return record


def _require_active_responsible(
    session: Session,
    team_id: UUID,
    responsible_user_id: UUID,
) -> TeamMembership:
    membership = session.scalar(
        select(TeamMembership)
        .join(User, TeamMembership.user_id == User.user_id)
        .where(
            TeamMembership.user_id == responsible_user_id,
            TeamMembership.team_id == team_id,
            TeamMembership.status == IdentityStatus.ACTIVE,
            User.status == IdentityStatus.ACTIVE,
        )
        .with_for_update()
    )
    if membership is None:
        session.rollback()
        raise MaintenanceResponsibleConflictError
    return membership


def _commit_record(session: Session, record: MaintenanceRecord) -> None:
    session.commit()
    session.refresh(record)


def _reject_transition(session: Session) -> None:
    session.rollback()
    raise InvalidMaintenanceStatusTransitionError
