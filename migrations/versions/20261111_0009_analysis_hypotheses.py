"""Create evidence-backed analyses and uncertain hypotheses.

Revision ID: 20261111_0009_analysis
Revises: 20261111_0008_observations
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261111_0009_analysis"
down_revision: str | None = "20261111_0008_observations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visibility_level = postgresql.ENUM(
    "TEAM",
    "ROLE_RESTRICTED",
    "ENGINEERING_CONFIDENTIAL",
    name="visibility_level",
    create_type=False,
)
analysis_evidence_type = postgresql.ENUM(
    "DRIVER_FEEDBACK",
    "LAP",
    "SECTOR",
    "CONDITION",
    "OBSERVATION",
    name="analysis_evidence_type",
    create_type=False,
)
cause_classification = postgresql.ENUM(
    "DRIVER_TECHNIQUE",
    "VEHICLE_SETUP",
    "MECHANICAL",
    "TIRES",
    "TRACK_ENVIRONMENT",
    "UNKNOWN",
    name="cause_classification",
    create_type=False,
)
confidence_level = postgresql.ENUM(
    "LOW",
    "MEDIUM",
    "HIGH",
    name="confidence_level",
    create_type=False,
)
hypothesis_status = postgresql.ENUM(
    "PROPOSED",
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "REJECTED",
    "INCONCLUSIVE",
    name="hypothesis_status",
    create_type=False,
)


def upgrade() -> None:
    """Create analysis records, evidence references, and hypotheses."""
    bind = op.get_bind()
    analysis_evidence_type.create(bind, checkfirst=True)
    cause_classification.create(bind, checkfirst=True)
    confidence_level.create(bind, checkfirst=True)
    hypothesis_status.create(bind, checkfirst=True)

    op.create_table(
        "session_analyses",
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("authorized_summary", sa.String(2000), nullable=True),
        sa.Column("technical_detail", sa.String(5000), nullable=False),
        sa.Column(
            "visibility_level",
            visibility_level,
            server_default="ENGINEERING_CONFIDENTIAL",
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
            "technical_detail = btrim(technical_detail) "
            "AND char_length(technical_detail) BETWEEN 1 AND 5000",
            name=op.f("ck_session_analyses_technical_detail_normalized"),
        ),
        sa.CheckConstraint(
            "authorized_summary IS NULL OR "
            "(authorized_summary = btrim(authorized_summary) "
            "AND char_length(authorized_summary) BETWEEN 1 AND 2000)",
            name=op.f("ck_session_analyses_authorized_summary_normalized"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ENGINEERING_CONFIDENTIAL'",
            name=op.f("ck_session_analyses_engineering_confidential"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_session_analyses_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_session_analyses_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["users.user_id"],
            name=op.f("fk_session_analyses_author_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("analysis_id", name=op.f("pk_session_analyses")),
        sa.UniqueConstraint(
            "analysis_id", "team_id", name="uq_session_analyses_analysis_team"
        ),
    )
    op.create_index(
        "ix_session_analyses_team_session",
        "session_analyses",
        ["team_id", "session_id"],
        unique=False,
    )

    op.create_table(
        "analysis_evidence_references",
        sa.Column("evidence_reference_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_type", analysis_evidence_type, nullable=False),
        sa.Column("reference_id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["analysis_id", "team_id"],
            ["session_analyses.analysis_id", "session_analyses.team_id"],
            name="fk_analysis_evidence_analysis_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "evidence_reference_id",
            name=op.f("pk_analysis_evidence_references"),
        ),
        sa.UniqueConstraint(
            "analysis_id",
            "evidence_type",
            "reference_id",
            name="uq_analysis_evidence_reference",
        ),
    )
    op.create_index(
        "ix_analysis_evidence_team_analysis",
        "analysis_evidence_references",
        ["team_id", "analysis_id"],
        unique=False,
    )

    op.create_table(
        "hypotheses",
        sa.Column("hypothesis_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("cause_classification", cause_classification, nullable=False),
        sa.Column("confidence", confidence_level, nullable=False),
        sa.Column(
            "status",
            hypothesis_status,
            server_default="PROPOSED",
            nullable=False,
        ),
        sa.Column(
            "visibility_level",
            visibility_level,
            server_default="ENGINEERING_CONFIDENTIAL",
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
            name=op.f("ck_hypotheses_description_normalized"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ENGINEERING_CONFIDENTIAL'",
            name=op.f("ck_hypotheses_engineering_confidential"),
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id", "team_id"],
            ["session_analyses.analysis_id", "session_analyses.team_id"],
            name="fk_hypotheses_analysis_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("hypothesis_id", name=op.f("pk_hypotheses")),
        sa.UniqueConstraint(
            "hypothesis_id", "team_id", name="uq_hypotheses_hypothesis_team"
        ),
    )
    op.create_index(
        "ix_hypotheses_team_analysis",
        "hypotheses",
        ["team_id", "analysis_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Block 8.9 records and their dedicated enum types."""
    op.drop_index("ix_hypotheses_team_analysis", table_name="hypotheses")
    op.drop_table("hypotheses")
    op.drop_index(
        "ix_analysis_evidence_team_analysis",
        table_name="analysis_evidence_references",
    )
    op.drop_table("analysis_evidence_references")
    op.drop_index("ix_session_analyses_team_session", table_name="session_analyses")
    op.drop_table("session_analyses")

    bind = op.get_bind()
    hypothesis_status.drop(bind, checkfirst=True)
    confidence_level.drop(bind, checkfirst=True)
    cause_classification.drop(bind, checkfirst=True)
    analysis_evidence_type.drop(bind, checkfirst=True)
