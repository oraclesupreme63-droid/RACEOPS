"""Create honest, visibility-scoped Observations.

Revision ID: 20261111_0008_observations
Revises: 20261111_0007_feedback
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261111_0008_observations"
down_revision: str | None = "20261111_0007_feedback"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visibility_level = postgresql.ENUM(
    "TEAM",
    "ROLE_RESTRICTED",
    "ENGINEERING_CONFIDENTIAL",
    name="visibility_level",
    create_type=False,
)


def upgrade() -> None:
    """Create evidence records without introducing causal claims."""
    op.create_table(
        "observations",
        sa.Column("observation_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("vehicle_id", sa.Uuid(), nullable=True),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("category", sa.String(80), nullable=True),
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
            "session_id IS NOT NULL OR vehicle_id IS NOT NULL",
            name=op.f("ck_observations_has_session_or_vehicle"),
        ),
        sa.CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name=op.f("ck_observations_description_normalized"),
        ),
        sa.CheckConstraint(
            "category IS NULL OR (category = btrim(category) "
            "AND char_length(category) BETWEEN 1 AND 80)",
            name=op.f("ck_observations_category_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_observations_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_observations_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_observations_vehicle_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["users.user_id"],
            name=op.f("fk_observations_author_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("observation_id", name=op.f("pk_observations")),
        sa.UniqueConstraint(
            "observation_id", "team_id", name="uq_observations_observation_team"
        ),
    )
    op.create_index(
        "ix_observations_team_session",
        "observations",
        ["team_id", "session_id"],
        unique=False,
    )
    op.create_index(
        "ix_observations_team_vehicle",
        "observations",
        ["team_id", "vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Observations while retaining the shared visibility type."""
    op.drop_index("ix_observations_team_vehicle", table_name="observations")
    op.drop_index("ix_observations_team_session", table_name="observations")
    op.drop_table("observations")
