"""Public request and response contracts for maintenance records."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.enums import Role
from raceops.learning.decision_schemas import ActionResponse
from raceops.learning.models import Action, Observation
from raceops.learning.schemas import ObservationResponse
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.models import MaintenanceRecord
from raceops.sessions.models import RaceSession
from raceops.sessions.schemas import SessionResponse


class MaintenanceCreateRequest(BaseModel):
    """Minimal fields accepted when creating one intervention record."""

    model_config = ConfigDict(extra="forbid")

    vehicle_id: UUID
    responsible_user_id: UUID
    session_id: UUID | None = None
    observation_id: UUID | None = None
    action_id: UUID | None = None
    maintenance_type: MaintenanceType
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized


class MaintenanceUpdateRequest(BaseModel):
    """Editable OPEN-record fields; lifecycle and ownership stay server-owned."""

    model_config = ConfigDict(extra="forbid")

    responsible_user_id: UUID | None = None
    maintenance_type: MaintenanceType | None = None
    description: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class MaintenanceCompleteRequest(BaseModel):
    """Required conclusion for a completed intervention."""

    model_config = ConfigDict(extra="forbid")

    completion_notes: str = Field(min_length=1, max_length=2000)

    @field_validator("completion_notes")
    @classmethod
    def normalize_completion_notes(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("completion_notes must not be blank")
        return normalized


class MaintenanceCancelRequest(BaseModel):
    """Required reason for ending an intervention without completion."""

    model_config = ConfigDict(extra="forbid")

    cancellation_reason: str = Field(min_length=1, max_length=1000)

    @field_validator("cancellation_reason")
    @classmethod
    def normalize_cancellation_reason(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("cancellation_reason must not be blank")
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


class MaintenanceCausalChainResponse(BaseModel):
    """Authorized context from one Session symptom to its intervention."""

    session: SessionResponse | None
    observation: ObservationResponse | None
    action: ActionResponse | None
    maintenance: MaintenanceResponse

    @classmethod
    def from_models(
        cls,
        record: MaintenanceRecord,
        race_session: RaceSession | None,
        observation: Observation | None,
        action: Action | None,
        actor_role: Role,
    ) -> Self:
        return cls(
            session=(
                SessionResponse.from_model(race_session)
                if race_session is not None
                else None
            ),
            observation=(
                ObservationResponse.from_model(observation)
                if observation is not None
                else None
            ),
            action=(
                ActionResponse.from_model(action, actor_role)
                if action is not None
                else None
            ),
            maintenance=MaintenanceResponse.from_model(record),
        )
