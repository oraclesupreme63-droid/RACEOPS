"""Create the Driver, Vehicle, Track, and Event operational base.

Revision ID: 20261108_0003_operations
Revises: 20261108_0002_identity
Create Date: 2026-11-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261108_0003_operations"
down_revision: str | None = "20261108_0002_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

driver_status = postgresql.ENUM(
    "ACTIVE",
    "INACTIVE",
    name="driver_status",
    create_type=False,
)
vehicle_status = postgresql.ENUM(
    "READY",
    "MAINTENANCE",
    "UNAVAILABLE",
    "RETIRED",
    name="vehicle_status",
    create_type=False,
)
event_status = postgresql.ENUM(
    "PLANNED",
    "ACTIVE",
    "COMPLETED",
    "CANCELLED",
    name="event_status",
    create_type=False,
)


def upgrade() -> None:
    """Create team-owned operational resources and constraints."""
    bind = op.get_bind()
    driver_status.create(bind, checkfirst=True)
    vehicle_status.create(bind, checkfirst=True)
    event_status.create(bind, checkfirst=True)

    op.create_table(
        "drivers",
        sa.Column("driver_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            driver_status,
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
            "display_name = btrim(display_name) "
            "AND char_length(display_name) BETWEEN 1 AND 120",
            name=op.f("ck_drivers_display_name_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_drivers_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_drivers_user_team_membership",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("driver_id", name=op.f("pk_drivers")),
        sa.UniqueConstraint(
            "team_id",
            "user_id",
            name="uq_drivers_team_user",
        ),
    )
    op.create_index(
        op.f("ix_drivers_team_id"),
        "drivers",
        ["team_id"],
        unique=False,
    )

    op.create_table(
        "vehicles",
        sa.Column("vehicle_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("identifier", sa.String(length=80), nullable=False),
        sa.Column(
            "status",
            vehicle_status,
            server_default=sa.text("'READY'"),
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
            "identifier = btrim(identifier) "
            "AND char_length(identifier) BETWEEN 1 AND 80",
            name=op.f("ck_vehicles_identifier_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_vehicles_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("vehicle_id", name=op.f("pk_vehicles")),
        sa.UniqueConstraint(
            "team_id",
            "identifier",
            name="uq_vehicles_team_identifier",
        ),
    )
    op.create_index(
        op.f("ix_vehicles_team_id"),
        "vehicles",
        ["team_id"],
        unique=False,
    )

    op.create_table(
        "tracks",
        sa.Column("track_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
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
            "location IS NULL OR "
            "(location = btrim(location) "
            "AND char_length(location) BETWEEN 1 AND 200)",
            name=op.f("ck_tracks_location_normalized"),
        ),
        sa.CheckConstraint(
            "name = btrim(name) AND char_length(name) BETWEEN 1 AND 160",
            name=op.f("ck_tracks_name_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_tracks_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("track_id", name=op.f("pk_tracks")),
        sa.UniqueConstraint(
            "track_id",
            "team_id",
            name="uq_tracks_track_team",
        ),
    )
    op.create_index(
        op.f("ix_tracks_team_id"),
        "tracks",
        ["team_id"],
        unique=False,
    )

    op.create_table(
        "events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("track_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "status",
            event_status,
            server_default=sa.text("'PLANNED'"),
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
            "ends_on IS NULL OR ends_on >= starts_on",
            name=op.f("ck_events_date_range_valid"),
        ),
        sa.CheckConstraint(
            "description IS NULL OR "
            "(description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 1000)",
            name=op.f("ck_events_description_normalized"),
        ),
        sa.CheckConstraint(
            "name = btrim(name) AND char_length(name) BETWEEN 1 AND 160",
            name=op.f("ck_events_name_normalized"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.team_id"],
            name=op.f("fk_events_team_id_teams"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["track_id", "team_id"],
            ["tracks.track_id", "tracks.team_id"],
            name="fk_events_track_team",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_events")),
    )
    op.create_index(
        "ix_events_team_starts_on",
        "events",
        ["team_id", "starts_on"],
        unique=False,
    )


def downgrade() -> None:
    """Remove operational tables and their PostgreSQL enum types."""
    op.drop_index("ix_events_team_starts_on", table_name="events")
    op.drop_table("events")
    op.drop_index(op.f("ix_tracks_team_id"), table_name="tracks")
    op.drop_table("tracks")
    op.drop_index(op.f("ix_vehicles_team_id"), table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index(op.f("ix_drivers_team_id"), table_name="drivers")
    op.drop_table("drivers")

    bind = op.get_bind()
    event_status.drop(bind, checkfirst=True)
    vehicle_status.drop(bind, checkfirst=True)
    driver_status.drop(bind, checkfirst=True)
