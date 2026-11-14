"""Public request and response contracts for maintenance records."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.models import MaintenanceRecord


class MaintenanceCreateRequest(BaseModel):
    """Minimal fields accepted when creating one intervention record."""

    model_config = ConfigDict(extra="forbid")

    vehicle_id: UUID
    responsible_user_id: UUID
    maintenance_type: MaintenanceType
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized


class MaintenanceResponse(BaseModel):
    """Authorized record without Team ownership or visibility internals."""

    maintenance_id: UUID
    vehicle_id: UUID
    responsible_user_id: UUID
    created_by_user_id: UUID
    session_id: UUID | None
    observation_id: UUID | None
    action_id: UUID | None
    maintenance_type: MaintenanceType
    status: MaintenanceStatus
    description: str
    completion_notes: str | None
    cancellation_reason: str | None
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, record: MaintenanceRecord) -> Self:
        return cls(
            maintenance_id=record.maintenance_id,
            vehicle_id=record.vehicle_id,
            responsible_user_id=record.responsible_user_id,
            created_by_user_id=record.created_by_user_id,
            session_id=record.session_id,
            observation_id=record.observation_id,
            action_id=record.action_id,
            maintenance_type=record.maintenance_type,
            status=record.status,
            description=record.description,
            completion_notes=record.completion_notes,
            cancellation_reason=record.cancellation_reason,
            started_at=record.started_at,
            completed_at=record.completed_at,
            cancelled_at=record.cancelled_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class MaintenancePageResponse(BaseModel):
    """Stable page calculated after Team and optional filters."""

    items: list[MaintenanceResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
