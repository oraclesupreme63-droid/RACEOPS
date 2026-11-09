"""Public request and response contracts for operational resources."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.operations.enums import DriverStatus, VehicleStatus
from raceops.operations.models import Driver, Vehicle


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
