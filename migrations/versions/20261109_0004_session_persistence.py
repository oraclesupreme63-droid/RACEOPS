"""Create Session persistence and Team-safe operational references.

Revision ID: 20261109_0004_sessions
Revises: 20261108_0003_operations
Create Date: 2026-11-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261109_0004_sessions"
down_revision: str | None = "20261108_0003_operations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

session_status = postgresql.ENUM(
    "PLANNED",
    "ACTIVE",
    "PAUSED",
    "COMPLETED",
    "CANCELLED",
    name="session_status",
    create_type=False,
)
results_status = postgresql.ENUM(
    "OPEN",
    "LOCKED",
    name="results_status",
    create_type=False,
)


def upgrade() -> None:
    """Create Team-owned Session records with independent result locking."""
    bind = op.get_bind()
    session_status.create(bind, checkfirst=True)
    results_status.create(bind, checkfirst=True)

    op.create_unique_constraint(
        "uq_drivers_driver_team",
        "drivers",
        ["driver_id", "team_id"],
    )
    op.create_unique_constraint(
        "uq_vehicles_vehicle_team",
        "vehicles",
        ["vehicle_id", "team_id"],
    )
    op.create_unique_constraint(
        "uq_events_event_team",
        "events",
        ["event_id", "team_id"],
    )

    op.create_table(
        "sessions",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("driver_id", sa.Uuid(), nullable=False),
        sa.Column("vehicle_id", sa.Uuid(), nullable=False),
        sa.Column("session_type", sa.String(length=80), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            session_status,
            server_default=sa.text("'PLANNED'"),
            nullable=False,
        ),
        sa.Column(
            "results_status",
            results_status,
            server_default=sa.text("'OPEN'"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("results_locked_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("results_locked_at", sa.DateTime(timezone=True), nullable=True),
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
            "session_type = btrim(session_type) "
            "AND char_length(session_type) BETWEEN 1 AND 80",
            name=op.f("ck_sessions_session_type_normalized"),
        ),
        sa.CheckConstraint(
            "(status = 'PLANNED' AND started_at IS NULL AND ended_at IS NULL) "
            "OR (status IN ('ACTIVE', 'PAUSED') "
            "AND started_at IS NOT NULL AND ended_at IS NULL) "
            "OR (status = 'COMPLETED' "
            "AND started_at IS NOT NULL AND ended_at IS NOT NULL) "
            "OR (status = 'CANCELLED' AND ended_at IS NOT NULL)",
            name=op.f("ck_sessions_activity_timestamps_consistent"),
        ),
        sa.CheckConstraint(
            "started_at IS NULL OR ended_at IS NULL OR ended_at >= started_at",
            name=op.f("ck_sessions_activity_time_order_valid"),
        ),
        sa.CheckConstraint(
            "(results_status = 'OPEN' "
            "AND results_locked_by_user_id IS NULL "
            "AND results_locked_at IS NULL) "
            "OR (results_status = 'LOCKED' "
            "AND results_locked_by_user_id IS NOT NULL "
            "AND results_locked_at IS NOT NULL)",
            name=op.f("ck_sessions_results_lock_consistent"),
        ),
        sa.CheckConstraint(
            "results_status = 'OPEN' OR status IN ('COMPLETED', 'CANCELLED')",
            name=op.f("ck_sessions_results_lock_requires_terminal_activity"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_sessions_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["event_id", "team_id"],
            ["events.event_id", "events.team_id"],
            name="fk_sessions_event_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["driver_id", "team_id"],
            ["drivers.driver_id", "drivers.team_id"],
            name="fk_sessions_driver_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_sessions_vehicle_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["results_locked_by_user_id"],
            ["users.user_id"],
            name=op.f("fk_sessions_results_locked_by_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("session_id", name=op.f("pk_sessions")),
    )
    op.create_index(
        "ix_sessions_team_scheduled_at",
        "sessions",
        ["team_id", "scheduled_at"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_team_event",
        "sessions",
        ["team_id", "event_id"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_team_driver",
        "sessions",
        ["team_id", "driver_id"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_team_vehicle",
        "sessions",
        ["team_id", "vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Session persistence and its supporting constraints."""
    op.drop_index("ix_sessions_team_vehicle", table_name="sessions")
    op.drop_index("ix_sessions_team_driver", table_name="sessions")
    op.drop_index("ix_sessions_team_event", table_name="sessions")
    op.drop_index("ix_sessions_team_scheduled_at", table_name="sessions")
    op.drop_table("sessions")

    op.drop_constraint("uq_events_event_team", "events", type_="unique")
    op.drop_constraint("uq_vehicles_vehicle_team", "vehicles", type_="unique")
    op.drop_constraint("uq_drivers_driver_team", "drivers", type_="unique")

    bind = op.get_bind()
    results_status.drop(bind, checkfirst=True)
    session_status.drop(bind, checkfirst=True)
