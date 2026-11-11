"""Create recipient priorities and assigned Actions.

Revision ID: 20261111_0010_decisions
Revises: 20261111_0009_analysis
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261111_0010_decisions"
down_revision: str | None = "20261111_0009_analysis"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visibility_level = postgresql.ENUM(
    "TEAM",
    "ROLE_RESTRICTED",
    "ENGINEERING_CONFIDENTIAL",
    name="visibility_level",
    create_type=False,
)
team_role = postgresql.ENUM(
    "ADMINISTRATOR",
    "TEAM_MANAGER",
    "ENGINEER",
    "MECHANIC",
    "DRIVER",
    name="team_role",
    create_type=False,
)
target_intent = postgresql.ENUM(
    "NEXT_SESSION",
    "SPECIFIC_SESSION",
    name="target_intent",
    create_type=False,
)
action_type = postgresql.ENUM(
    "DRIVING",
    "ENGINEERING",
    "MECHANICAL",
    name="action_type",
    create_type=False,
)
action_status = postgresql.ENUM(
    "PROPOSED",
    "PLANNED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    name="action_status",
    create_type=False,
)


def upgrade() -> None:
    """Add priorities and work execution without creating Outcomes."""
    bind = op.get_bind()
    target_intent.create(bind, checkfirst=True)
    action_type.create(bind, checkfirst=True)
    action_status.create(bind, checkfirst=True)

    op.create_table(
        "priorities",
        sa.Column("priority_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("source_session_id", sa.Uuid(), nullable=False),
        sa.Column("target_session_id", sa.Uuid(), nullable=True),
        sa.Column("target_scope_id", sa.Uuid(), nullable=False),
        sa.Column("hypothesis_id", sa.Uuid(), nullable=True),
        sa.Column("target_intent", target_intent, nullable=False),
        sa.Column("recipient_role", team_role, nullable=False),
        sa.Column("recipient_user_id", sa.Uuid(), nullable=True),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("is_main", sa.Boolean(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
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
            name=op.f("ck_priorities_description_normalized"),
        ),
        sa.CheckConstraint(
            "recipient_role IN ('DRIVER', 'ENGINEER', 'MECHANIC')",
            name=op.f("ck_priorities_recipient_role_allowed"),
        ),
        sa.CheckConstraint(
            "(is_main AND rank BETWEEN 1 AND 3) OR (NOT is_main AND rank IS NULL)",
            name=op.f("ck_priorities_main_rank_consistent"),
        ),
        sa.CheckConstraint(
            "(target_intent = 'NEXT_SESSION' "
            "AND target_session_id IS NULL "
            "AND target_scope_id = source_session_id) "
            "OR (target_intent = 'SPECIFIC_SESSION' "
            "AND target_session_id IS NOT NULL "
            "AND target_scope_id = target_session_id)",
            name=op.f("ck_priorities_target_consistent"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name=op.f("ck_priorities_role_restricted"),
        ),
        sa.ForeignKeyConstraint(
            ["source_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_priorities_source_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["target_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_priorities_target_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hypothesis_id", "team_id"],
            ["hypotheses.hypothesis_id", "hypotheses.team_id"],
            name="fk_priorities_hypothesis_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["recipient_user_id"],
            ["users.user_id"],
            name=op.f("fk_priorities_recipient_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("priority_id", name=op.f("pk_priorities")),
        sa.UniqueConstraint(
            "priority_id", "team_id", name="uq_priorities_priority_team"
        ),
    )
    op.create_index(
        "ix_priorities_team_source",
        "priorities",
        ["team_id", "source_session_id"],
        unique=False,
    )
    op.create_index(
        "ix_priorities_team_target",
        "priorities",
        ["team_id", "target_scope_id"],
        unique=False,
    )
    op.create_index(
        "uq_priorities_main_rank_scope",
        "priorities",
        [
            "team_id",
            "target_scope_id",
            "recipient_role",
            "recipient_user_id",
            "rank",
        ],
        unique=True,
        postgresql_where=sa.text("is_main"),
        postgresql_nulls_not_distinct=True,
    )

    op.create_table(
        "actions",
        sa.Column("action_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("source_session_id", sa.Uuid(), nullable=False),
        sa.Column("target_session_id", sa.Uuid(), nullable=True),
        sa.Column("target_scope_id", sa.Uuid(), nullable=False),
        sa.Column("hypothesis_id", sa.Uuid(), nullable=True),
        sa.Column("priority_id", sa.Uuid(), nullable=True),
        sa.Column("assignee_user_id", sa.Uuid(), nullable=True),
        sa.Column("assignee_role", team_role, nullable=False),
        sa.Column("target_intent", target_intent, nullable=False),
        sa.Column("action_type", action_type, nullable=False),
        sa.Column("status", action_status, server_default="PROPOSED", nullable=False),
        sa.Column("public_summary", sa.String(2000), nullable=True),
        sa.Column("confidential_detail", sa.String(5000), nullable=True),
        sa.Column("cancellation_reason", sa.String(1000), nullable=True),
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
            "assignee_role IN ('DRIVER', 'ENGINEER', 'MECHANIC')",
            name=op.f("ck_actions_assignee_role_allowed"),
        ),
        sa.CheckConstraint(
            "(target_intent = 'NEXT_SESSION' "
            "AND target_session_id IS NULL "
            "AND target_scope_id = source_session_id) "
            "OR (target_intent = 'SPECIFIC_SESSION' "
            "AND target_session_id IS NOT NULL "
            "AND target_scope_id = target_session_id)",
            name=op.f("ck_actions_target_consistent"),
        ),
        sa.CheckConstraint(
            "hypothesis_id IS NOT NULL OR priority_id IS NOT NULL "
            "OR public_summary IS NOT NULL OR confidential_detail IS NOT NULL",
            name=op.f("ck_actions_has_motivation"),
        ),
        sa.CheckConstraint(
            "public_summary IS NULL OR (public_summary = btrim(public_summary) "
            "AND char_length(public_summary) BETWEEN 1 AND 2000)",
            name=op.f("ck_actions_public_summary_normalized"),
        ),
        sa.CheckConstraint(
            "confidential_detail IS NULL OR "
            "(confidential_detail = btrim(confidential_detail) "
            "AND char_length(confidential_detail) BETWEEN 1 AND 5000)",
            name=op.f("ck_actions_confidential_detail_normalized"),
        ),
        sa.CheckConstraint(
            "(status = 'CANCELLED' AND cancellation_reason IS NOT NULL) "
            "OR (status <> 'CANCELLED' AND cancellation_reason IS NULL)",
            name=op.f("ck_actions_cancellation_consistent"),
        ),
        sa.CheckConstraint(
            "cancellation_reason IS NULL OR "
            "(cancellation_reason = btrim(cancellation_reason) "
            "AND char_length(cancellation_reason) BETWEEN 1 AND 1000)",
            name=op.f("ck_actions_cancellation_reason_normalized"),
        ),
        sa.CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name=op.f("ck_actions_role_restricted"),
        ),
        sa.ForeignKeyConstraint(
            ["source_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_actions_source_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["target_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_actions_target_session_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hypothesis_id", "team_id"],
            ["hypotheses.hypothesis_id", "hypotheses.team_id"],
            name="fk_actions_hypothesis_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["priority_id", "team_id"],
            ["priorities.priority_id", "priorities.team_id"],
            name="fk_actions_priority_team",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assignee_user_id"],
            ["users.user_id"],
            name=op.f("fk_actions_assignee_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("action_id", name=op.f("pk_actions")),
        sa.UniqueConstraint("action_id", "team_id", name="uq_actions_action_team"),
    )
    op.create_index(
        "ix_actions_team_source",
        "actions",
        ["team_id", "source_session_id"],
        unique=False,
    )
    op.create_index(
        "ix_actions_team_target",
        "actions",
        ["team_id", "target_scope_id"],
        unique=False,
    )
    op.create_index(
        "ix_actions_team_assignee",
        "actions",
        ["team_id", "assignee_user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove decisions while retaining earlier learning records."""
    op.drop_index("ix_actions_team_assignee", table_name="actions")
    op.drop_index("ix_actions_team_target", table_name="actions")
    op.drop_index("ix_actions_team_source", table_name="actions")
    op.drop_table("actions")
    op.drop_index("uq_priorities_main_rank_scope", table_name="priorities")
    op.drop_index("ix_priorities_team_target", table_name="priorities")
    op.drop_index("ix_priorities_team_source", table_name="priorities")
    op.drop_table("priorities")

    bind = op.get_bind()
    action_status.drop(bind, checkfirst=True)
    action_type.drop(bind, checkfirst=True)
    target_intent.drop(bind, checkfirst=True)
