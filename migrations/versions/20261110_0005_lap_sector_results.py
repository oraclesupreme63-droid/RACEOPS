"""Create canonical Lap and optional Sector results.

Revision ID: 20261110_0005_results
Revises: 20261109_0004_sessions
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261110_0005_results"
down_revision: str | None = "20261109_0004_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

lap_source = postgresql.ENUM(
    "MANUAL", "IMPORTED", "OTHER", name="lap_source", create_type=False
)
lap_classification = postgresql.ENUM(
    "VALID",
    "INVALID",
    "OUT_LAP",
    "IN_LAP",
    "INCOMPLETE",
    name="lap_classification",
    create_type=False,
)
sector_status = postgresql.ENUM(
    "VALID", "INVALID", "INCOMPLETE", name="sector_status", create_type=False
)


def upgrade() -> None:
    """Create Team-safe timing results and their integrity constraints."""
    bind = op.get_bind()
    lap_source.create(bind, checkfirst=True)
    lap_classification.create(bind, checkfirst=True)
    sector_status.create(bind, checkfirst=True)

    op.create_unique_constraint(
        "uq_sessions_session_team",
        "sessions",
        ["session_id", "team_id"],
    )
    op.create_table(
        "laps",
        sa.Column("lap_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("lap_number", sa.Integer(), nullable=False),
        sa.Column("duration_us", sa.BigInteger(), nullable=False),
        sa.Column(
            "source",
            lap_source,
            server_default=sa.text("'MANUAL'"),
            nullable=False,
        ),
        sa.Column(
            "classification",
            lap_classification,
            server_default=sa.text("'VALID'"),
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
        sa.CheckConstraint("lap_number > 0", name=op.f("ck_laps_lap_number_positive")),
        sa.CheckConstraint(
            "duration_us > 0", name=op.f("ck_laps_duration_us_positive")
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_laps_session_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("lap_id", name=op.f("pk_laps")),
        sa.UniqueConstraint(
            "session_id", "lap_number", name="uq_laps_session_lap_number"
        ),
        sa.UniqueConstraint("lap_id", "team_id", name="uq_laps_lap_team"),
    )
    op.create_index(
        "ix_laps_team_session", "laps", ["team_id", "session_id"], unique=False
    )

    op.create_table(
        "sectors",
        sa.Column("sector_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("lap_id", sa.Uuid(), nullable=False),
        sa.Column("sector_order", sa.Integer(), nullable=False),
        sa.Column("duration_us", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sector_status,
            server_default=sa.text("'VALID'"),
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
            "sector_order > 0", name=op.f("ck_sectors_sector_order_positive")
        ),
        sa.CheckConstraint(
            "duration_us > 0", name=op.f("ck_sectors_duration_us_positive")
        ),
        sa.ForeignKeyConstraint(
            ["lap_id", "team_id"],
            ["laps.lap_id", "laps.team_id"],
            name="fk_sectors_lap_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("sector_id", name=op.f("pk_sectors")),
        sa.UniqueConstraint(
            "lap_id", "sector_order", name="uq_sectors_lap_sector_order"
        ),
    )
    op.create_index(
        "ix_sectors_team_lap", "sectors", ["team_id", "lap_id"], unique=False
    )


def downgrade() -> None:
    """Remove timing results and supporting PostgreSQL enum types."""
    op.drop_index("ix_sectors_team_lap", table_name="sectors")
    op.drop_table("sectors")
    op.drop_index("ix_laps_team_session", table_name="laps")
    op.drop_table("laps")
    op.drop_constraint("uq_sessions_session_team", "sessions", type_="unique")

    bind = op.get_bind()
    sector_status.drop(bind, checkfirst=True)
    lap_classification.drop(bind, checkfirst=True)
    lap_source.drop(bind, checkfirst=True)
