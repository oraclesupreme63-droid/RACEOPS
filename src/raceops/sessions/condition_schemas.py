"""Validated HTTP representations for sparse Session conditions."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.sessions.models import ConditionSnapshot


class ConditionFields(BaseModel):
    """Known values only; absent information remains null, never zero."""

    model_config = ConfigDict(extra="forbid")

    ambient_temperature: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=3
    )
    ambient_temperature_unit: str | None = Field(
        default=None, min_length=1, max_length=24
    )
    track_temperature: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=3
    )
    track_temperature_unit: str | None = Field(
        default=None, min_length=1, max_length=24
    )
    weather: str | None = Field(default=None, min_length=1, max_length=80)
    track_condition: str | None = Field(default=None, min_length=1, max_length=120)
    source: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator(
        "ambient_temperature_unit",
        "track_temperature_unit",
        "weather",
        "track_condition",
        "source",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("condition text must not be blank")
        return normalized


class ConditionCreateRequest(ConditionFields):
    """Create the single P0 snapshot with at least one known condition."""

    @model_validator(mode="after")
    def validate_complete_snapshot(self) -> Self:
        _validate_pairs_and_content(self)
        return self


class ConditionUpdateRequest(ConditionFields):
    """Partial changes; the service validates the resulting full snapshot."""

    @model_validator(mode="after")
    def require_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        return self


class ConditionResponse(BaseModel):
    """Authorized sparse snapshot with explicit measurement units."""

    condition_id: UUID
    session_id: UUID
    ambient_temperature: Decimal | None
    ambient_temperature_unit: str | None
    track_temperature: Decimal | None
    track_temperature_unit: str | None
    weather: str | None
    track_condition: str | None
    source: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, snapshot: ConditionSnapshot) -> Self:
        return cls(
            condition_id=snapshot.condition_id,
            session_id=snapshot.session_id,
            ambient_temperature=snapshot.ambient_temperature,
            ambient_temperature_unit=snapshot.ambient_temperature_unit,
            track_temperature=snapshot.track_temperature,
            track_temperature_unit=snapshot.track_temperature_unit,
            weather=snapshot.weather,
            track_condition=snapshot.track_condition,
            source=snapshot.source,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


def _validate_pairs_and_content(snapshot: ConditionFields) -> None:
    if (snapshot.ambient_temperature is None) != (
        snapshot.ambient_temperature_unit is None
    ):
        raise ValueError("ambient_temperature requires its unit")
    if (snapshot.track_temperature is None) != (
        snapshot.track_temperature_unit is None
    ):
        raise ValueError("track_temperature requires its unit")
    if all(
        value is None
        for value in (
            snapshot.ambient_temperature,
            snapshot.track_temperature,
            snapshot.weather,
            snapshot.track_condition,
        )
    ):
        raise ValueError("at least one known condition must be supplied")
