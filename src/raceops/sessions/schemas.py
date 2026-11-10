"""Validated HTTP representations for Session planning."""

from datetime import UTC, datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.models import RaceSession


class SessionCreateRequest(BaseModel):
    """Client-controlled fields accepted for a new planned Session."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    driver_id: UUID
    vehicle_id: UUID
    session_type: str = Field(min_length=1, max_length=80)
    scheduled_at: datetime

    @field_validator("session_type")
    @classmethod
    def normalize_session_type(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("session_type must not be blank")
        return normalized

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_at must include a timezone")
        return value.astimezone(UTC)


class SessionUpdateRequest(BaseModel):
    """Permitted changes while a Session remains PLANNED."""

    model_config = ConfigDict(extra="forbid")

    driver_id: UUID | None = None
    vehicle_id: UUID | None = None
    session_type: str | None = Field(default=None, min_length=1, max_length=80)
    scheduled_at: datetime | None = None

    @field_validator("session_type")
    @classmethod
    def normalize_session_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("session_type must not be blank")
        return normalized

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_at must include a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("session fields cannot be null")
        return self


class SessionResponse(BaseModel):
    """Authorized Session representation without ownership internals."""

    session_id: UUID
    event_id: UUID
    driver_id: UUID
    vehicle_id: UUID
    session_type: str
    scheduled_at: datetime
    status: SessionStatus
    results_status: ResultsStatus
    started_at: datetime | None
    ended_at: datetime | None
    results_locked_by_user_id: UUID | None
    results_locked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, race_session: RaceSession) -> Self:
        return cls(
            session_id=race_session.session_id,
            event_id=race_session.event_id,
            driver_id=race_session.driver_id,
            vehicle_id=race_session.vehicle_id,
            session_type=race_session.session_type,
            scheduled_at=race_session.scheduled_at,
            status=race_session.status,
            results_status=race_session.results_status,
            started_at=race_session.started_at,
            ended_at=race_session.ended_at,
            results_locked_by_user_id=race_session.results_locked_by_user_id,
            results_locked_at=race_session.results_locked_at,
            created_at=race_session.created_at,
            updated_at=race_session.updated_at,
        )


class SessionPageResponse(BaseModel):
    """Stable page after Team, relationship, and query filtering."""

    items: list[SessionResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
