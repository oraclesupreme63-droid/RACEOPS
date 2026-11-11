"""Create relationship-scoped Driver Feedback.

Revision ID: 20261111_0007_feedback
Revises: 20261110_0006_conditions
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261111_0007_feedback"
down_revision: str | None = "20261110_0006_conditions"
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
    """Preserve experiencer, recorder, Session, visibility, and brief context."""
    visibility_level.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "driver_feedback",
        sa.Column("feedback_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("driver_id", sa.Uuid(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("corner_or_zone", sa.String(80), nullable=True),
        sa.Column("driving_phase", sa.String(80), nullable=True),
        sa.Column("severity", sa.String(40), nullable=True),
        sa.Column("confidence", sa.String(40), nullable=True),
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
            name=op.f("ck_driver_feedback_description_normalized"),
        ),
        sa.CheckConstraint(
            "corner_or_zone IS NULL OR (corner_or_zone = btrim(corner_or_zone) "
            "AND char_length(corner_or_zone) BETWEEN 1 AND 80)",
            name=op.f("ck_driver_feedback_corner_or_zone_normalized"),
        ),
        sa.CheckConstraint(
            "driving_phase IS NULL OR (driving_phase = btrim(driving_phase) "
            "AND char_length(driving_phase) BETWEEN 1 AND 80)",
            name=op.f("ck_driver_feedback_driving_phase_normalized"),
        ),
        sa.CheckConstraint(
            "severity IS NULL OR (severity = btrim(severity) "
            "AND char_length(severity) BETWEEN 1 AND 40)",
            name=op.f("ck_driver_feedback_severity_normalized"),
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence = btrim(confidence) "
            "AND char_length(confidence) BETWEEN 1 AND 40)",
            name=op.f("ck_driver_feedback_confidence_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_driver_feedback_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["driver_id", "team_id"],
            ["drivers.driver_id", "drivers.team_id"],
            name="fk_driver_feedback_driver_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["users.user_id"],
            name=op.f("fk_driver_feedback_author_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("feedback_id", name=op.f("pk_driver_feedback")),
        sa.UniqueConstraint(
            "feedback_id", "team_id", name="uq_driver_feedback_feedback_team"
        ),
    )
    op.create_index(
        "ix_driver_feedback_team_session",
        "driver_feedback",
        ["team_id", "session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Driver Feedback and its first shared visibility type."""
    op.drop_index("ix_driver_feedback_team_session", table_name="driver_feedback")
    op.drop_table("driver_feedback")
    visibility_level.drop(op.get_bind(), checkfirst=True)
