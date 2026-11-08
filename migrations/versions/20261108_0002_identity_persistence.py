"""Create identity and team membership persistence.

Revision ID: 20261108_0002_identity
Revises: 20261024_0001
Create Date: 2026-11-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261108_0002_identity"
down_revision: str | None = "20261024_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

identity_status = postgresql.ENUM(
    "ACTIVE",
    "INACTIVE",
    name="identity_status",
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


def upgrade() -> None:
    """Create Team, User, and TeamMembership storage."""
    bind = op.get_bind()
    identity_status.create(bind, checkfirst=True)
    team_role.create(bind, checkfirst=True)

    op.create_table(
        "teams",
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            identity_status,
            server_default=sa.text("'ACTIVE'"),
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
            "char_length(btrim(name)) > 0",
            name=op.f("ck_teams_name_not_blank"),
        ),
        sa.PrimaryKeyConstraint("team_id", name=op.f("pk_teams")),
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column(
            "status",
            identity_status,
            server_default=sa.text("'ACTIVE'"),
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
            "email = lower(btrim(email)) AND char_length(email) BETWEEN 3 AND 254",
            name=op.f("ck_users_email_normalized"),
        ),
        sa.CheckConstraint(
            "char_length(btrim(password_hash)) > 0",
            name=op.f("ck_users_password_hash_not_blank"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "team_memberships",
        sa.Column("membership_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("role", team_role, nullable=False),
        sa.Column(
            "status",
            identity_status,
            server_default=sa.text("'ACTIVE'"),
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
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_team_memberships_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_team_memberships_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "membership_id",
            name=op.f("pk_team_memberships"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "team_id",
            name=op.f("uq_team_memberships_user_id"),
        ),
    )
    op.create_index(
        op.f("ix_team_memberships_team_id"),
        "team_memberships",
        ["team_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove identity tables and their PostgreSQL enum types."""
    op.drop_index(
        op.f("ix_team_memberships_team_id"),
        table_name="team_memberships",
    )
    op.drop_table("team_memberships")
    op.drop_table("users")
    op.drop_table("teams")

    bind = op.get_bind()
    team_role.drop(bind, checkfirst=True)
    identity_status.drop(bind, checkfirst=True)
