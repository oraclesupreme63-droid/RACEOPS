"""Create team-scoped Maintenance Records.

Revision ID: 20261113_0012_maintenance
Revises: 20261112_0011_outcomes
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261113_0012_maintenance"
down_revision: str | None = "20261112_0011_outcomes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visibility_level = postgresql.ENUM(
    "TEAM",
    "ROLE_RESTRICTED",
    "ENGINEERING_CONFIDENTIAL",
    name="visibility_level",
    create_type=False,
)
maintenance_type = postgresql.ENUM(
    "INSPECTION",
    "PREVENTIVE_SERVICE",
    "REPAIR",
    "REPLACEMENT",
    name="maintenance_type",
    create_type=False,
)
maintenance_status = postgresql.ENUM(
    "OPEN",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    name="maintenance_status",
    create_type=False,
)


def upgrade() -> None:
    """Add immutable-context intervention records without an API."""
    bind = op.get_bind()
    maintenance_type.create(bind, checkfirst=True)
    maintenance_status.create(bind, checkfirst=True)

    op.create_table(
        "maintenance_records",
        sa.Column("maintenance_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("vehicle_id", sa.Uuid(), nullable=False),
        sa.Column("responsible_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("observation_id", sa.Uuid(), nullable=True),
        sa.Column("action_id", sa.Uuid(), nullable=True),
        sa.Column("maintenance_type", maintenance_type, nullable=False),
        sa.Column("status", maintenance_status, server_default="OPEN", nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("completion_notes", sa.String(2000), nullable=True),
        sa.Column("cancellation_reason", sa.String(1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "visibility_level",
            visibility_level,
            server_default="ROLE_RESTRICTED",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name=op.f("ck_maintenance_records_description_normalized"),
        ),
        sa.CheckConstraint(
            "completion_notes IS NULL OR "
            "(completion_notes = btrim(completion_notes) "
            "AND char_length(completion_notes) BETWEEN 1 AND 2000)",
            name=op.f("ck_maintenance_records_completion_notes_normalized"),
        ),
        sa.CheckConstraint(
            "cancellation_reason IS NULL OR "
            "(cancellation_reason = btrim(cancellation_reason) "
            "AND char_length(cancellation_reason) BETWEEN 1 AND 1000)",
            name=op.f("ck_maintenance_records_cancellation_reason_normalized"),
        ),
        sa.CheckConstraint(
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
            name=op.f("ck_maintenance_records_lifecycle_consistent"),
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR completed_at IS NULL OR completed_at >= started_at",
            name=op.f("ck_maintenance_records_completion_time_order_valid"),
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR cancelled_at IS NULL OR cancelled_at >= started_at",
            name=op.f("ck_maintenance_records_cancellation_time_order_valid"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name=op.f("ck_maintenance_records_role_restricted"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_maintenance_records_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_maintenance_records_vehicle_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["responsible_user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_maintenance_records_responsible_membership",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_maintenance_records_creator_membership",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_maintenance_records_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["observation_id", "team_id"],
            ["observations.observation_id", "observations.team_id"],
            name="fk_maintenance_records_observation_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["action_id", "team_id"],
            ["actions.action_id", "actions.team_id"],
            name="fk_maintenance_records_action_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("maintenance_id", name=op.f("pk_maintenance_records")),
        sa.UniqueConstraint(
            "maintenance_id",
            "team_id",
            name="uq_maintenance_records_maintenance_team",
        ),
    )
    op.create_index(
        "ix_maintenance_records_team_vehicle_created",
        "maintenance_records",
        ["team_id", "vehicle_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_records_team_status",
        "maintenance_records",
        ["team_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_records_team_session",
        "maintenance_records",
        ["team_id", "session_id"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_records_team_observation",
        "maintenance_records",
        ["team_id", "observation_id"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_records_team_action",
        "maintenance_records",
        ["team_id", "action_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove intervention records and their private enum types."""
    op.drop_index(
        "ix_maintenance_records_team_action", table_name="maintenance_records"
    )
    op.drop_index(
        "ix_maintenance_records_team_observation", table_name="maintenance_records"
    )
    op.drop_index(
        "ix_maintenance_records_team_session", table_name="maintenance_records"
    )
    op.drop_index(
        "ix_maintenance_records_team_status", table_name="maintenance_records"
    )
    op.drop_index(
        "ix_maintenance_records_team_vehicle_created",
        table_name="maintenance_records",
    )
    op.drop_table("maintenance_records")

    bind = op.get_bind()
    maintenance_status.drop(bind, checkfirst=True)
    maintenance_type.drop(bind, checkfirst=True)
