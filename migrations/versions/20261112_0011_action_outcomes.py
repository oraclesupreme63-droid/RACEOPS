"""Create evidence-based Action Outcomes.

Revision ID: 20261112_0011_outcomes
Revises: 20261111_0010_decisions
Create Date: 2026-11-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261112_0011_outcomes"
down_revision: str | None = "20261111_0010_decisions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visibility_level = postgresql.ENUM(
    "TEAM",
    "ROLE_RESTRICTED",
    "ENGINEERING_CONFIDENTIAL",
    name="visibility_level",
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
action_outcome_classification = postgresql.ENUM(
    "IMPROVED",
    "WORSENED",
    "NO_MEASURABLE_EFFECT",
    "INCONCLUSIVE",
    name="action_outcome_classification",
    create_type=False,
)


def upgrade() -> None:
    """Add one explicit P0 evaluation per completed Action."""
    bind = op.get_bind()
    action_outcome_classification.create(bind, checkfirst=True)

    op.create_table(
        "action_outcomes",
        sa.Column("outcome_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("action_id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_session_id", sa.Uuid(), nullable=False),
        sa.Column("classification", action_outcome_classification, nullable=False),
        sa.Column("public_conclusion", sa.String(2000), nullable=True),
        sa.Column("confidential_conclusion", sa.String(5000), nullable=True),
        sa.Column("concluded_hypothesis_status", hypothesis_status, nullable=True),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
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
            "public_conclusion IS NOT NULL OR confidential_conclusion IS NOT NULL",
            name=op.f("ck_action_outcomes_has_conclusion"),
        ),
        sa.CheckConstraint(
            "public_conclusion IS NULL OR "
            "(public_conclusion = btrim(public_conclusion) "
            "AND char_length(public_conclusion) BETWEEN 1 AND 2000)",
            name=op.f("ck_action_outcomes_public_conclusion_normalized"),
        ),
        sa.CheckConstraint(
            "confidential_conclusion IS NULL OR "
            "(confidential_conclusion = btrim(confidential_conclusion) "
            "AND char_length(confidential_conclusion) BETWEEN 1 AND 5000)",
            name=op.f("ck_action_outcomes_confidential_conclusion_normalized"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name=op.f("ck_action_outcomes_role_restricted"),
        ),
        sa.ForeignKeyConstraint(
            ["action_id", "team_id"],
            ["actions.action_id", "actions.team_id"],
            name="fk_action_outcomes_action_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["evaluation_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_action_outcomes_evaluation_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["users.user_id"],
            name=op.f("fk_action_outcomes_author_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("outcome_id", name=op.f("pk_action_outcomes")),
        sa.UniqueConstraint("action_id", name="uq_action_outcomes_action"),
        sa.UniqueConstraint(
            "outcome_id", "team_id", name="uq_action_outcomes_outcome_team"
        ),
    )
    op.create_index(
        "ix_action_outcomes_team_session",
        "action_outcomes",
        ["team_id", "evaluation_session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Outcomes while preserving Action execution records."""
    op.drop_index("ix_action_outcomes_team_session", table_name="action_outcomes")
    op.drop_table("action_outcomes")
    action_outcome_classification.drop(op.get_bind(), checkfirst=True)
