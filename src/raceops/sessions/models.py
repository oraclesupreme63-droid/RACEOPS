"""SQLAlchemy persistence model for a motorsport Session."""

from datetime import datetime
from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from raceops.db.base import Base, TimestampMixin
from raceops.sessions.enums import (
    LapClassification,
    LapSource,
    ResultsStatus,
    SectorStatus,
    SessionStatus,
)

SESSION_STATUS_ENUM_NAME: Final = "session_status"
RESULTS_STATUS_ENUM_NAME: Final = "results_status"
LAP_SOURCE_ENUM_NAME: Final = "lap_source"
LAP_CLASSIFICATION_ENUM_NAME: Final = "lap_classification"
SECTOR_STATUS_ENUM_NAME: Final = "sector_status"


class RaceSession(TimestampMixin, Base):
    """One on-track activity with an atomic Driver and Vehicle assignment."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "session_type = btrim(session_type) "
            "AND char_length(session_type) BETWEEN 1 AND 80",
            name="session_type_normalized",
        ),
        CheckConstraint(
            "(status = 'PLANNED' AND started_at IS NULL AND ended_at IS NULL) "
            "OR (status IN ('ACTIVE', 'PAUSED') "
            "AND started_at IS NOT NULL AND ended_at IS NULL) "
            "OR (status = 'COMPLETED' "
            "AND started_at IS NOT NULL AND ended_at IS NOT NULL) "
            "OR (status = 'CANCELLED' AND ended_at IS NOT NULL)",
            name="activity_timestamps_consistent",
        ),
        CheckConstraint(
            "started_at IS NULL OR ended_at IS NULL OR ended_at >= started_at",
            name="activity_time_order_valid",
        ),
        CheckConstraint(
            "(results_status = 'OPEN' "
            "AND results_locked_by_user_id IS NULL "
            "AND results_locked_at IS NULL) "
            "OR (results_status = 'LOCKED' "
            "AND results_locked_by_user_id IS NOT NULL "
            "AND results_locked_at IS NOT NULL)",
            name="results_lock_consistent",
        ),
        CheckConstraint(
            "results_status = 'OPEN' OR status IN ('COMPLETED', 'CANCELLED')",
            name="results_lock_requires_terminal_activity",
        ),
        ForeignKeyConstraint(
            ["event_id", "team_id"],
            ["events.event_id", "events.team_id"],
            name="fk_sessions_event_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["driver_id", "team_id"],
            ["drivers.driver_id", "drivers.team_id"],
            name="fk_sessions_driver_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_sessions_vehicle_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "session_id",
            "team_id",
            name="uq_sessions_session_team",
        ),
        Index("ix_sessions_team_scheduled_at", "team_id", "scheduled_at"),
        Index("ix_sessions_team_event", "team_id", "event_id"),
        Index("ix_sessions_team_driver", "team_id", "driver_id"),
        Index("ix_sessions_team_vehicle", "team_id", "vehicle_id"),
    )

    session_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_id: Mapped[UUID] = mapped_column(nullable=False)
    driver_id: Mapped[UUID] = mapped_column(nullable=False)
    vehicle_id: Mapped[UUID] = mapped_column(nullable=False)
    session_type: Mapped[str] = mapped_column(String(80), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name=SESSION_STATUS_ENUM_NAME),
        nullable=False,
        default=SessionStatus.PLANNED,
        server_default=SessionStatus.PLANNED.value,
    )
    results_status: Mapped[ResultsStatus] = mapped_column(
        Enum(ResultsStatus, name=RESULTS_STATUS_ENUM_NAME),
        nullable=False,
        default=ResultsStatus.OPEN,
        server_default=ResultsStatus.OPEN.value,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    results_locked_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=True,
    )
    results_locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Lap(TimestampMixin, Base):
    """Canonical lap result and aggregate root for optional Sectors."""

    __tablename__ = "laps"
    __table_args__ = (
        CheckConstraint("lap_number > 0", name="lap_number_positive"),
        CheckConstraint("duration_us > 0", name="duration_us_positive"),
        ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_laps_session_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "session_id",
            "lap_number",
            name="uq_laps_session_lap_number",
        ),
        UniqueConstraint("lap_id", "team_id", name="uq_laps_lap_team"),
        Index("ix_laps_team_session", "team_id", "session_id"),
    )

    lap_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    session_id: Mapped[UUID] = mapped_column(nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_us: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source: Mapped[LapSource] = mapped_column(
        Enum(LapSource, name=LAP_SOURCE_ENUM_NAME),
        nullable=False,
        default=LapSource.MANUAL,
        server_default=LapSource.MANUAL.value,
    )
    classification: Mapped[LapClassification] = mapped_column(
        Enum(LapClassification, name=LAP_CLASSIFICATION_ENUM_NAME),
        nullable=False,
        default=LapClassification.VALID,
        server_default=LapClassification.VALID.value,
    )

    @property
    def is_eligible(self) -> bool:
        """Return whether this Lap participates in primary metrics."""
        return self.classification == LapClassification.VALID


class Sector(TimestampMixin, Base):
    """Optional ordered timing segment contained by one Lap aggregate."""

    __tablename__ = "sectors"
    __table_args__ = (
        CheckConstraint("sector_order > 0", name="sector_order_positive"),
        CheckConstraint("duration_us > 0", name="duration_us_positive"),
        ForeignKeyConstraint(
            ["lap_id", "team_id"],
            ["laps.lap_id", "laps.team_id"],
            name="fk_sectors_lap_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "lap_id",
            "sector_order",
            name="uq_sectors_lap_sector_order",
        ),
        Index("ix_sectors_team_lap", "team_id", "lap_id"),
    )

    sector_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    lap_id: Mapped[UUID] = mapped_column(nullable=False)
    sector_order: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_us: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[SectorStatus] = mapped_column(
        Enum(SectorStatus, name=SECTOR_STATUS_ENUM_NAME),
        nullable=False,
        default=SectorStatus.VALID,
        server_default=SectorStatus.VALID.value,
    )
