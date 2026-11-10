"""Validated HTTP representations for Lap and Sector results."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from raceops.sessions.enums import LapClassification, LapSource, SectorStatus
from raceops.sessions.models import Lap, Sector


class SectorCreateRequest(BaseModel):
    """One optional ordered segment supplied with or after a Lap."""

    model_config = ConfigDict(extra="forbid")

    sector_order: int = Field(ge=1)
    duration_us: int = Field(ge=1)
    status: SectorStatus = SectorStatus.VALID


class SectorUpdateRequest(BaseModel):
    """Mutable Sector timing fields while Session results remain open."""

    model_config = ConfigDict(extra="forbid")

    sector_order: int | None = Field(default=None, ge=1)
    duration_us: int | None = Field(default=None, ge=1)
    status: SectorStatus | None = None

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        _require_non_null_changes(self)
        return self


class LapCreateRequest(BaseModel):
    """Canonical timing result with optional atomic Sector creation."""

    model_config = ConfigDict(extra="forbid")

    lap_number: int = Field(ge=1)
    duration_us: int = Field(ge=1)
    source: LapSource = LapSource.MANUAL
    classification: LapClassification = LapClassification.VALID
    sectors: list[SectorCreateRequest] = Field(default_factory=list, max_length=50)

    @model_validator(mode="after")
    def require_unique_sector_orders(self) -> Self:
        orders = [sector.sector_order for sector in self.sectors]
        if len(orders) != len(set(orders)):
            raise ValueError("sector_order must be unique inside a Lap")
        return self


class LapUpdateRequest(BaseModel):
    """Mutable Lap fields while Session results remain open."""

    model_config = ConfigDict(extra="forbid")

    lap_number: int | None = Field(default=None, ge=1)
    duration_us: int | None = Field(default=None, ge=1)
    source: LapSource | None = None
    classification: LapClassification | None = None

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        _require_non_null_changes(self)
        return self


class LapResponse(BaseModel):
    """Authorized canonical Lap representation."""

    lap_id: UUID
    session_id: UUID
    lap_number: int
    duration_us: int
    source: LapSource
    classification: LapClassification
    is_eligible: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, lap: Lap) -> Self:
        return cls(
            lap_id=lap.lap_id,
            session_id=lap.session_id,
            lap_number=lap.lap_number,
            duration_us=lap.duration_us,
            source=lap.source,
            classification=lap.classification,
            is_eligible=lap.is_eligible,
            created_at=lap.created_at,
            updated_at=lap.updated_at,
        )


class LapPageResponse(BaseModel):
    """Stable Lap page ordered by number and identifier."""

    items: list[LapResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class SectorResponse(BaseModel):
    """Authorized Sector representation."""

    sector_id: UUID
    lap_id: UUID
    sector_order: int
    duration_us: int
    status: SectorStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, sector: Sector) -> Self:
        return cls(
            sector_id=sector.sector_id,
            lap_id=sector.lap_id,
            sector_order=sector.sector_order,
            duration_us=sector.duration_us,
            status=sector.status,
            created_at=sector.created_at,
            updated_at=sector.updated_at,
        )


class SectorPageResponse(BaseModel):
    """All optional Sectors for one Lap in deterministic order."""

    items: list[SectorResponse]
    total: int = Field(ge=0)


class ResultsSummaryResponse(BaseModel):
    """Simple integer timing metrics without false precision or certainty."""

    session_id: UUID
    total_laps: int = Field(ge=0)
    eligible_laps: int = Field(ge=0)
    excluded_laps: int = Field(ge=0)
    best_lap_id: UUID | None
    best_lap_us: int | None
    average_lap_us: int | None
    consistency_us: int | None


def _require_non_null_changes(model: BaseModel) -> None:
    if not model.model_fields_set:
        raise ValueError("at least one field must be supplied")
    if any(getattr(model, field) is None for field in model.model_fields_set):
        raise ValueError("result fields cannot be null")
