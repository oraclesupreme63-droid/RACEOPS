"""Create optional per-Session Condition Snapshots.

Revision ID: 20261110_0006_conditions
Revises: 20261110_0005_results
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261110_0006_conditions"
down_revision: str | None = "20261110_0005_results"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create one sparse, Team-safe contextual snapshot per Session."""
    op.create_table(
        "condition_snapshots",
        sa.Column("condition_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("ambient_temperature", sa.Numeric(10, 3), nullable=True),
        sa.Column("ambient_temperature_unit", sa.String(24), nullable=True),
        sa.Column("track_temperature", sa.Numeric(10, 3), nullable=True),
        sa.Column("track_temperature_unit", sa.String(24), nullable=True),
        sa.Column("weather", sa.String(80), nullable=True),
        sa.Column("track_condition", sa.String(120), nullable=True),
        sa.Column("source", sa.String(80), nullable=True),
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
            "(ambient_temperature IS NULL AND ambient_temperature_unit IS NULL) "
            "OR (ambient_temperature IS NOT NULL "
            "AND ambient_temperature_unit IS NOT NULL)",
            name=op.f("ck_condition_snapshots_ambient_temperature_value_unit_pair"),
        ),
        sa.CheckConstraint(
            "(track_temperature IS NULL AND track_temperature_unit IS NULL) "
            "OR (track_temperature IS NOT NULL "
            "AND track_temperature_unit IS NOT NULL)",
            name=op.f("ck_condition_snapshots_track_temperature_value_unit_pair"),
        ),
        sa.CheckConstraint(
            "ambient_temperature IS NOT NULL OR track_temperature IS NOT NULL "
            "OR weather IS NOT NULL OR track_condition IS NOT NULL",
            name=op.f("ck_condition_snapshots_at_least_one_known_condition"),
        ),
        sa.CheckConstraint(
            "ambient_temperature_unit IS NULL "
            "OR (ambient_temperature_unit = btrim(ambient_temperature_unit) "
            "AND char_length(ambient_temperature_unit) BETWEEN 1 AND 24)",
            name=op.f("ck_condition_snapshots_ambient_temperature_unit_normalized"),
        ),
        sa.CheckConstraint(
            "track_temperature_unit IS NULL "
            "OR (track_temperature_unit = btrim(track_temperature_unit) "
            "AND char_length(track_temperature_unit) BETWEEN 1 AND 24)",
            name=op.f("ck_condition_snapshots_track_temperature_unit_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_condition_snapshots_session_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("condition_id", name=op.f("pk_condition_snapshots")),
        sa.UniqueConstraint("session_id", name="uq_condition_snapshots_session"),
    )
    op.create_index(
        "ix_condition_snapshots_team_session",
        "condition_snapshots",
        ["team_id", "session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Condition Snapshots."""
    op.drop_index(
        "ix_condition_snapshots_team_session",
        table_name="condition_snapshots",
    )
    op.drop_table("condition_snapshots")
