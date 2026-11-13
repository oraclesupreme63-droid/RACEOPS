"""Typed loader for the frozen, synthetic Phase 9 scenario."""

import json
from datetime import date, datetime
from decimal import Decimal
from importlib.resources import files
from typing import cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

from raceops.iam.authorization import Visibility
from raceops.sessions.enums import LapClassification, LapSource, SectorStatus


class SectorSeed(BaseModel):
    """One optional timing segment, including incomplete data quality."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    sector_order: int = Field(gt=0)
    duration_us: int = Field(gt=0)
    status: SectorStatus = SectorStatus.VALID


class LapSeed(BaseModel):
    """One canonical lap and the sectors that were actually available."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lap_number: int = Field(gt=0)
    duration_us: int = Field(gt=0)
    source: LapSource = LapSource.MANUAL
    classification: LapClassification = LapClassification.VALID
    sectors: list[SectorSeed] = Field(default_factory=list)


class ConditionSeed(BaseModel):
    """Known conditions; omitted fields remain honestly unknown."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ambient_temperature: Decimal | None = None
    ambient_temperature_unit: str | None = None
    track_temperature: Decimal | None = None
    track_temperature_unit: str | None = None
    weather: str | None = None
    track_condition: str | None = None
    source: str | None = None

    @model_validator(mode="after")
    def require_known_value(self) -> "ConditionSeed":
        values = (
            self.ambient_temperature,
            self.track_temperature,
            self.weather,
            self.track_condition,
        )
        if all(value is None for value in values):
            raise ValueError("at least one condition must be known")
        return self


class SessionSeed(BaseModel):
    """A historical Session prepared for replay during validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_type: str = Field(min_length=1, max_length=80)
    scheduled_at: datetime
    started_at: datetime
    ended_at: datetime
    conditions: ConditionSeed
    laps: list[LapSeed] = Field(min_length=1)


class ObservationSeed(BaseModel):
    """A non-causal note intentionally exposing missing information."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    description: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=80)
    visibility_level: Visibility = Visibility.ROLE_RESTRICTED


class ValidationScenarioDefinition(BaseModel):
    """Frozen scenario definition and non-secret rehearsal copy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str
    title: str
    team_name: str
    track_name: str
    track_location: str
    event_name: str
    event_date: date
    event_description: str
    driver_name: str
    vehicle_identifier: str
    source_session: SessionSeed
    evaluation_session: SessionSeed
    seed_observation: ObservationSeed
    rehearsal: dict[str, object]


def load_validation_scenario() -> ValidationScenarioDefinition:
    """Load and validate the packaged scenario before touching PostgreSQL."""
    resource = files("raceops.validation").joinpath("scenario_v1.json")
    payload = cast(object, json.loads(resource.read_text(encoding="utf-8")))
    return ValidationScenarioDefinition.model_validate(payload)
