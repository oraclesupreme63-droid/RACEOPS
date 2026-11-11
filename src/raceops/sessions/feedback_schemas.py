"""Validated HTTP representations for Session Driver Feedback."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.authorization import Visibility
from raceops.sessions.models import DriverFeedback


class FeedbackCreateRequest(BaseModel):
    """Short, low-friction description plus optional driving context."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1, max_length=2000)
    corner_or_zone: str | None = Field(default=None, min_length=1, max_length=80)
    driving_phase: str | None = Field(default=None, min_length=1, max_length=80)
    severity: str | None = Field(default=None, min_length=1, max_length=40)
    confidence: str | None = Field(default=None, min_length=1, max_length=40)

    @field_validator(
        "description",
        "corner_or_zone",
        "driving_phase",
        "severity",
        "confidence",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized


class FeedbackUpdateRequest(BaseModel):
    """Editable feedback fields; optional context may explicitly be cleared."""

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(default=None, min_length=1, max_length=2000)
    corner_or_zone: str | None = Field(default=None, min_length=1, max_length=80)
    driving_phase: str | None = Field(default=None, min_length=1, max_length=80)
    severity: str | None = Field(default=None, min_length=1, max_length=40)
    confidence: str | None = Field(default=None, min_length=1, max_length=40)

    @field_validator(
        "description",
        "corner_or_zone",
        "driving_phase",
        "severity",
        "confidence",
    )
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


class FeedbackResponse(BaseModel):
    """Authorized feedback with explicit experiencer and recorder identities."""

    feedback_id: UUID
    session_id: UUID
    driver_id: UUID
    author_user_id: UUID
    description: str
    corner_or_zone: str | None
    driving_phase: str | None
    severity: str | None
    confidence: str | None
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, feedback: DriverFeedback) -> Self:
        return cls(
            feedback_id=feedback.feedback_id,
            session_id=feedback.session_id,
            driver_id=feedback.driver_id,
            author_user_id=feedback.author_user_id,
            description=feedback.description,
            corner_or_zone=feedback.corner_or_zone,
            driving_phase=feedback.driving_phase,
            severity=feedback.severity,
            confidence=feedback.confidence,
            visibility_level=feedback.visibility_level,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
        )


class FeedbackPageResponse(BaseModel):
    """Stable authorized page for one Session."""

    items: list[FeedbackResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
