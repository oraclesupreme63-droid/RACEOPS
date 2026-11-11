"""Validated HTTP representations for honest technical Observations."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.authorization import Visibility
from raceops.learning.models import Observation


class ObservationCreateRequest(BaseModel):
    """Evidence associated with at least one same-Team Session or Vehicle."""

    model_config = ConfigDict(extra="forbid")

    session_id: UUID | None = None
    vehicle_id: UUID | None = None
    description: str = Field(min_length=1, max_length=2000)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    visibility_level: Visibility = Visibility.ROLE_RESTRICTED

    @field_validator("description", "category")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_context(self) -> Self:
        if self.session_id is None and self.vehicle_id is None:
            raise ValueError("session_id or vehicle_id is required")
        return self


class ObservationUpdateRequest(BaseModel):
    """Editable evidence text; context and visibility remain immutable in P0."""

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(default=None, min_length=1, max_length=2000)
    category: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("description", "category")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if "description" in self.model_fields_set and self.description is None:
            raise ValueError("description cannot be null")
        return self


class ObservationResponse(BaseModel):
    """Authorized evidence without any implied causal or confirmation field."""

    observation_id: UUID
    session_id: UUID | None
    vehicle_id: UUID | None
    author_user_id: UUID
    description: str
    category: str | None
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, observation: Observation) -> Self:
        return cls(
            observation_id=observation.observation_id,
            session_id=observation.session_id,
            vehicle_id=observation.vehicle_id,
            author_user_id=observation.author_user_id,
            description=observation.description,
            category=observation.category,
            visibility_level=observation.visibility_level,
            created_at=observation.created_at,
            updated_at=observation.updated_at,
        )


class ObservationPageResponse(BaseModel):
    """Stable page after Team, relationship, and visibility filtering."""

    items: list[ObservationResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
