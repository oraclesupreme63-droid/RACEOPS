"""Typed loaders for frozen Phase 9 validation datasets."""

import json
from datetime import date, datetime
from decimal import Decimal
from importlib.resources import files
from typing import Literal, cast

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


class PublishedSourceSeed(BaseModel):
    """Provenance and transformation boundary for a public timing source."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: Literal["PUBLIC_TIMING"]
    publisher: str = Field(min_length=1, max_length=200)
    document_title: str = Field(min_length=1, max_length=300)
    document_url: str = Field(pattern=r"^https://", max_length=1000)
    document_references: list[str] = Field(min_length=1)
    retrieved_on: date
    publication_notice: str = Field(min_length=1, max_length=500)
    identity_handling: str = Field(min_length=1, max_length=500)
    factual_fields: list[str] = Field(min_length=1)
    synthetic_fields: list[str] = Field(min_length=1)


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
    event_end_date: date | None = None
    event_description: str
    driver_name: str
    vehicle_identifier: str
    source_session: SessionSeed
    evaluation_session: SessionSeed
    seed_observation: ObservationSeed
    published_source: PublishedSourceSeed | None = None
    rehearsal: dict[str, object]

    @model_validator(mode="after")
    def validate_event_dates(self) -> "ValidationScenarioDefinition":
        if self.event_end_date is not None and self.event_end_date < self.event_date:
            raise ValueError("event_end_date cannot precede event_date")
        return self


ValidationDatasetName = Literal["synthetic", "public-kristianstad-2025"]

_DATASET_FILES: dict[ValidationDatasetName, str] = {
    "synthetic": "scenario_v1.json",
    "public-kristianstad-2025": "scenario_public_kristianstad_2025.json",
}


def load_validation_scenario(
    dataset: ValidationDatasetName = "synthetic",
) -> ValidationScenarioDefinition:
    """Load and validate one packaged dataset before touching PostgreSQL."""
    resource = files("raceops.validation").joinpath(_DATASET_FILES[dataset])
    payload = cast(object, json.loads(resource.read_text(encoding="utf-8")))
    return ValidationScenarioDefinition.model_validate(payload)
