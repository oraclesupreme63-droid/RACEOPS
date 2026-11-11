"""Persistence models for evidence in the Session learning loop."""

from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from raceops.db.base import Base, TimestampMixin
from raceops.iam.authorization import Visibility

VISIBILITY_LEVEL_ENUM_NAME: Final = "visibility_level"


class Observation(TimestampMixin, Base):
    """A recorded fact, symptom, or behavior; never a confirmed cause."""

    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint(
            "session_id IS NOT NULL OR vehicle_id IS NOT NULL",
            name="has_session_or_vehicle",
        ),
        CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name="description_normalized",
        ),
        CheckConstraint(
            "category IS NULL OR (category = btrim(category) "
            "AND char_length(category) BETWEEN 1 AND 80)",
            name="category_normalized",
        ),
        ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_observations_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_observations_vehicle_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "observation_id", "team_id", name="uq_observations_observation_team"
        ),
        Index("ix_observations_team_session", "team_id", "session_id"),
        Index("ix_observations_team_vehicle", "team_id", "vehicle_id"),
    )

    observation_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[UUID | None] = mapped_column(nullable=True)
    vehicle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    author_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ROLE_RESTRICTED,
        server_default=Visibility.ROLE_RESTRICTED.value,
    )
