"""Public request and response contracts for operational resources."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.operations.enums import DriverStatus, EventStatus, VehicleStatus
from raceops.operations.models import Driver, Event, Track, Vehicle


class DriverCreateRequest(BaseModel):
    """Fields accepted when an authorized actor creates a Driver."""

    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=120)
    user_id: UUID | None = None

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("display_name must not be blank")
        return normalized


class DriverUpdateRequest(BaseModel):
    """Partial Driver changes; explicit null unlinks the optional User."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    user_id: UUID | None = None

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("display_name must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_at_least_one_change(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if "display_name" in self.model_fields_set and self.display_name is None:
            raise ValueError("display_name cannot be null")
        return self


class DriverResponse(BaseModel):
    """Authorized Driver representation without a client-controlled Team."""

    driver_id: UUID
    user_id: UUID | None
    display_name: str
    status: DriverStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, driver: Driver) -> Self:
        return cls(
            driver_id=driver.driver_id,
            user_id=driver.user_id,
            display_name=driver.display_name,
            status=driver.status,
            created_at=driver.created_at,
            updated_at=driver.updated_at,
        )


class DriverPageResponse(BaseModel):
    """Stable offset page calculated after authorization filtering."""

    items: list[DriverResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class VehicleCreateRequest(BaseModel):
    """Fields accepted when an authorized actor creates a Vehicle."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=1, max_length=80)

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("identifier must not be blank")
        return normalized


class VehicleUpdateRequest(BaseModel):
    """Allowed Vehicle identity change; status has dedicated commands."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=1, max_length=80)

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("identifier must not be blank")
        return normalized


class VehicleResponse(BaseModel):
    """Authorized Vehicle representation without ownership internals."""

    vehicle_id: UUID
    identifier: str
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, vehicle: Vehicle) -> Self:
        return cls(
            vehicle_id=vehicle.vehicle_id,
            identifier=vehicle.identifier,
            status=vehicle.status,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
        )


class VehiclePageResponse(BaseModel):
    """Stable offset page calculated after Team authorization filtering."""

    items: list[VehicleResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class TrackCreateRequest(BaseModel):
    """Minimal Track fields accepted from an authorized Team actor."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("name", "location")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized


class TrackUpdateRequest(BaseModel):
    """Partial Track changes; explicit null clears the optional location."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("name", "location")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_at_least_one_change(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self


class TrackResponse(BaseModel):
    """Authorized Track representation without ownership internals."""

    track_id: UUID
    name: str
    location: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, track: Track) -> Self:
        return cls(
            track_id=track.track_id,
            name=track.name,
            location=track.location,
            created_at=track.created_at,
            updated_at=track.updated_at,
        )


class TrackPageResponse(BaseModel):
    """Stable offset page calculated after Team filtering."""

    items: list[TrackResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class EventCreateRequest(BaseModel):
    """Fields accepted when an authorized actor creates an Event."""

    model_config = ConfigDict(extra="forbid")

    track_id: UUID
    name: str = Field(min_length=1, max_length=160)
    starts_on: date
    ends_on: date | None = None
    description: str | None = Field(default=None, min_length=1, max_length=1000)

    @field_validator("name", "description")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.ends_on is not None and self.ends_on < self.starts_on:
            raise ValueError("ends_on cannot precede starts_on")
        return self


class EventUpdateRequest(BaseModel):
    """Partial Event metadata changes; status uses explicit commands."""

    model_config = ConfigDict(extra="forbid")

    track_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    starts_on: date | None = None
    ends_on: date | None = None
    description: str | None = Field(default=None, min_length=1, max_length=1000)

    @field_validator("name", "description")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        required_fields = {"track_id", "name", "starts_on"}
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in required_fields
        ):
            raise ValueError("required event fields cannot be null")
        if (
            self.starts_on is not None
            and self.ends_on is not None
            and self.ends_on < self.starts_on
        ):
            raise ValueError("ends_on cannot precede starts_on")
        return self


class EventResponse(BaseModel):
    """Authorized Event representation with its same-Team Track reference."""

    event_id: UUID
    track_id: UUID
    name: str
    starts_on: date
    ends_on: date | None
    description: str | None
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, event: Event) -> Self:
        return cls(
            event_id=event.event_id,
            track_id=event.track_id,
            name=event.name,
            starts_on=event.starts_on,
            ends_on=event.ends_on,
            description=event.description,
            status=event.status,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )


class EventPageResponse(BaseModel):
    """Stable Event page after Team and optional filters."""

    items: list[EventResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
