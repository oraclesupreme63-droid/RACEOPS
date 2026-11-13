"""Persistence model for team-scoped vehicle maintenance history."""

from datetime import datetime
from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from raceops.db.base import Base, TimestampMixin
from raceops.iam.authorization import Visibility
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType

MAINTENANCE_TYPE_ENUM_NAME: Final = "maintenance_type"
MAINTENANCE_STATUS_ENUM_NAME: Final = "maintenance_status"
VISIBILITY_LEVEL_ENUM_NAME: Final = "visibility_level"


class MaintenanceRecord(TimestampMixin, Base):
    """One intervention whose completion never implies Vehicle readiness."""

    __tablename__ = "maintenance_records"
    __table_args__ = (
        CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name="description_normalized",
        ),
        CheckConstraint(
            "completion_notes IS NULL OR "
            "(completion_notes = btrim(completion_notes) "
            "AND char_length(completion_notes) BETWEEN 1 AND 2000)",
            name="completion_notes_normalized",
        ),
        CheckConstraint(
            "cancellation_reason IS NULL OR "
            "(cancellation_reason = btrim(cancellation_reason) "
            "AND char_length(cancellation_reason) BETWEEN 1 AND 1000)",
            name="cancellation_reason_normalized",
        ),
        CheckConstraint(
            "(status = 'OPEN' AND started_at IS NULL "
            "AND completed_at IS NULL AND cancelled_at IS NULL "
            "AND completion_notes IS NULL AND cancellation_reason IS NULL) "
            "OR (status = 'IN_PROGRESS' AND started_at IS NOT NULL "
            "AND completed_at IS NULL AND cancelled_at IS NULL "
            "AND completion_notes IS NULL AND cancellation_reason IS NULL) "
            "OR (status = 'COMPLETED' AND completed_at IS NOT NULL "
            "AND cancelled_at IS NULL AND completion_notes IS NOT NULL "
            "AND cancellation_reason IS NULL) "
            "OR (status = 'CANCELLED' AND completed_at IS NULL "
            "AND cancelled_at IS NOT NULL AND completion_notes IS NULL "
            "AND cancellation_reason IS NOT NULL)",
            name="lifecycle_consistent",
        ),
        CheckConstraint(
            "started_at IS NULL OR completed_at IS NULL OR completed_at >= started_at",
            name="completion_time_order_valid",
        ),
        CheckConstraint(
            "started_at IS NULL OR cancelled_at IS NULL OR cancelled_at >= started_at",
            name="cancellation_time_order_valid",
        ),
        CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name="role_restricted",
        ),
        ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_maintenance_records_vehicle_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["responsible_user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_maintenance_records_responsible_membership",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["created_by_user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_maintenance_records_creator_membership",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_maintenance_records_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["observation_id", "team_id"],
            ["observations.observation_id", "observations.team_id"],
            name="fk_maintenance_records_observation_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["action_id", "team_id"],
            ["actions.action_id", "actions.team_id"],
            name="fk_maintenance_records_action_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "maintenance_id",
            "team_id",
            name="uq_maintenance_records_maintenance_team",
        ),
        Index(
            "ix_maintenance_records_team_vehicle_created",
            "team_id",
            "vehicle_id",
            "created_at",
        ),
        Index("ix_maintenance_records_team_status", "team_id", "status"),
        Index("ix_maintenance_records_team_session", "team_id", "session_id"),
        Index(
            "ix_maintenance_records_team_observation",
            "team_id",
            "observation_id",
        ),
        Index("ix_maintenance_records_team_action", "team_id", "action_id"),
    )

    maintenance_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
    )
    vehicle_id: Mapped[UUID] = mapped_column(nullable=False)
    responsible_user_id: Mapped[UUID] = mapped_column(nullable=False)
    created_by_user_id: Mapped[UUID] = mapped_column(nullable=False)
    session_id: Mapped[UUID | None] = mapped_column(nullable=True)
    observation_id: Mapped[UUID | None] = mapped_column(nullable=True)
    action_id: Mapped[UUID | None] = mapped_column(nullable=True)
    maintenance_type: Mapped[MaintenanceType] = mapped_column(
        Enum(MaintenanceType, name=MAINTENANCE_TYPE_ENUM_NAME),
        nullable=False,
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus, name=MAINTENANCE_STATUS_ENUM_NAME),
        nullable=False,
        default=MaintenanceStatus.OPEN,
        server_default=MaintenanceStatus.OPEN.value,
    )
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    completion_notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ROLE_RESTRICTED,
        server_default=Visibility.ROLE_RESTRICTED.value,
    )
