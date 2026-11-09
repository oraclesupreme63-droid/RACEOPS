"""SQLAlchemy persistence models for the operational base."""

from datetime import date
from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from raceops.db.base import Base, TimestampMixin
from raceops.operations.enums import DriverStatus, EventStatus, VehicleStatus

DRIVER_STATUS_ENUM_NAME: Final = "driver_status"
VEHICLE_STATUS_ENUM_NAME: Final = "vehicle_status"
EVENT_STATUS_ENUM_NAME: Final = "event_status"


class Driver(TimestampMixin, Base):
    """Team-owned sporting profile, optionally linked to an active identity."""

    __tablename__ = "drivers"
    __table_args__ = (
        CheckConstraint(
            "display_name = btrim(display_name) "
            "AND char_length(display_name) BETWEEN 1 AND 120",
            name="display_name_normalized",
        ),
        UniqueConstraint(
            "team_id",
            "user_id",
            name="uq_drivers_team_user",
        ),
        UniqueConstraint(
            "driver_id",
            "team_id",
            name="uq_drivers_driver_team",
        ),
        ForeignKeyConstraint(
            ["user_id", "team_id"],
            ["team_memberships.user_id", "team_memberships.team_id"],
            name="fk_drivers_user_team_membership",
            ondelete="RESTRICT",
        ),
    )

    driver_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(nullable=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, name=DRIVER_STATUS_ENUM_NAME),
        nullable=False,
        default=DriverStatus.ACTIVE,
        server_default=DriverStatus.ACTIVE.value,
    )


class Vehicle(TimestampMixin, Base):
    """Team-owned competition vehicle with explicit availability."""

    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "identifier = btrim(identifier) "
            "AND char_length(identifier) BETWEEN 1 AND 80",
            name="identifier_normalized",
        ),
        UniqueConstraint(
            "team_id",
            "identifier",
            name="uq_vehicles_team_identifier",
        ),
        UniqueConstraint(
            "vehicle_id",
            "team_id",
            name="uq_vehicles_vehicle_team",
        ),
    )

    vehicle_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    identifier: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus, name=VEHICLE_STATUS_ENUM_NAME),
        nullable=False,
        default=VehicleStatus.READY,
        server_default=VehicleStatus.READY.value,
    )


class Track(TimestampMixin, Base):
    """Minimal team-owned track reference without telemetry metadata."""

    __tablename__ = "tracks"
    __table_args__ = (
        CheckConstraint(
            "name = btrim(name) AND char_length(name) BETWEEN 1 AND 160",
            name="name_normalized",
        ),
        CheckConstraint(
            "location IS NULL OR "
            "(location = btrim(location) "
            "AND char_length(location) BETWEEN 1 AND 200)",
            name="location_normalized",
        ),
        UniqueConstraint(
            "track_id",
            "team_id",
            name="uq_tracks_track_team",
        ),
    )

    track_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)


class Event(TimestampMixin, Base):
    """Team event hosted by a Track from the same ownership boundary."""

    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "name = btrim(name) AND char_length(name) BETWEEN 1 AND 160",
            name="name_normalized",
        ),
        CheckConstraint(
            "ends_on IS NULL OR ends_on >= starts_on",
            name="date_range_valid",
        ),
        CheckConstraint(
            "description IS NULL OR "
            "(description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 1000)",
            name="description_normalized",
        ),
        ForeignKeyConstraint(
            ["track_id", "team_id"],
            ["tracks.track_id", "tracks.team_id"],
            name="fk_events_track_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "event_id",
            "team_id",
            name="uq_events_event_team",
        ),
        Index("ix_events_team_starts_on", "team_id", "starts_on"),
    )

    event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
    )
    track_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name=EVENT_STATUS_ENUM_NAME),
        nullable=False,
        default=EventStatus.PLANNED,
        server_default=EventStatus.PLANNED.value,
    )
