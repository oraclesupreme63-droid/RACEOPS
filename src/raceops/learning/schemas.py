"""Validated HTTP representations for honest technical Observations."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.authorization import Visibility
from raceops.learning.enums import (
    AnalysisEvidenceType,
    CauseClassification,
    ConfidenceLevel,
    HypothesisStatus,
)
from raceops.learning.models import Hypothesis, Observation, SessionAnalysis


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


class AnalysisEvidenceRequest(BaseModel):
    """One typed pointer whose Session relationship is checked server-side."""

    model_config = ConfigDict(extra="forbid")

    evidence_type: AnalysisEvidenceType
    reference_id: UUID


class AnalysisEvidenceResponse(BaseModel):
    """Evidence identifier exposed only through Engineering endpoints."""

    evidence_type: AnalysisEvidenceType
    reference_id: UUID


class SessionAnalysisCreateRequest(BaseModel):
    """Engineering analysis grounded in at least one available source."""

    model_config = ConfigDict(extra="forbid")

    technical_detail: str = Field(min_length=1, max_length=5000)
    authorized_summary: str | None = Field(default=None, min_length=1, max_length=2000)
    evidence: list[AnalysisEvidenceRequest] = Field(min_length=1, max_length=100)

    @field_validator("technical_detail", "authorized_summary")
    @classmethod
    def normalize_analysis_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized

    @field_validator("evidence")
    @classmethod
    def reject_duplicate_evidence(
        cls, value: list[AnalysisEvidenceRequest]
    ) -> list[AnalysisEvidenceRequest]:
        keys = {(item.evidence_type, item.reference_id) for item in value}
        if len(keys) != len(value):
            raise ValueError("evidence references must be unique")
        return value


class SessionAnalysisUpdateRequest(BaseModel):
    """Editable reasoning; evidence and confidentiality remain immutable."""

    model_config = ConfigDict(extra="forbid")

    technical_detail: str | None = Field(default=None, min_length=1, max_length=5000)
    authorized_summary: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("technical_detail", "authorized_summary")
    @classmethod
    def normalize_analysis_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_analysis_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if (
            "technical_detail" in self.model_fields_set
            and self.technical_detail is None
        ):
            raise ValueError("technical_detail cannot be null")
        return self


class SessionAnalysisResponse(BaseModel):
    """Complete analysis representation reserved for Engineering."""

    analysis_id: UUID
    session_id: UUID
    author_user_id: UUID
    authorized_summary: str | None
    technical_detail: str
    visibility_level: Visibility
    evidence: list[AnalysisEvidenceResponse]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, analysis: SessionAnalysis) -> Self:
        return cls(
            analysis_id=analysis.analysis_id,
            session_id=analysis.session_id,
            author_user_id=analysis.author_user_id,
            authorized_summary=analysis.authorized_summary,
            technical_detail=analysis.technical_detail,
            visibility_level=analysis.visibility_level,
            evidence=[
                AnalysisEvidenceResponse(
                    evidence_type=item.evidence_type,
                    reference_id=item.reference_id,
                )
                for item in analysis.evidence_refs
            ],
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        )


class AuthorizedAnalysisSummaryResponse(BaseModel):
    """Deliberately non-identifying projection for an authorized audience."""

    authorized_summary: str
    updated_at: datetime


class HypothesisCreateRequest(BaseModel):
    """One uncertain explanation; its initial status is server-controlled."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1, max_length=2000)
    cause_classification: CauseClassification
    confidence: ConfidenceLevel

    @field_validator("description")
    @classmethod
    def normalize_hypothesis_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized


class HypothesisUpdateRequest(BaseModel):
    """Revise a proposed hypothesis without concluding it prematurely."""

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(default=None, min_length=1, max_length=2000)
    cause_classification: CauseClassification | None = None
    confidence: ConfidenceLevel | None = None

    @field_validator("description")
    @classmethod
    def normalize_hypothesis_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_hypothesis_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("hypothesis fields cannot be null")
        return self


class HypothesisResponse(BaseModel):
    """Engineering-only representation with explicit uncertainty and state."""

    hypothesis_id: UUID
    analysis_id: UUID
    description: str
    cause_classification: CauseClassification
    confidence: ConfidenceLevel
    status: HypothesisStatus
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, hypothesis: Hypothesis) -> Self:
        return cls(
            hypothesis_id=hypothesis.hypothesis_id,
            analysis_id=hypothesis.analysis_id,
            description=hypothesis.description,
            cause_classification=hypothesis.cause_classification,
            confidence=hypothesis.confidence,
            status=hypothesis.status,
            visibility_level=hypothesis.visibility_level,
            created_at=hypothesis.created_at,
            updated_at=hypothesis.updated_at,
        )
