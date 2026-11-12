"""HTTP representations for evidence-based Action evaluation."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.learning.decision_schemas import ActionResponse, PriorityResponse
from raceops.learning.enums import (
    ActionEvaluationStatus,
    ActionOutcomeClassification,
    HypothesisStatus,
)
from raceops.learning.models import Action, ActionOutcome
from raceops.learning.schemas import HypothesisResponse, SessionAnalysisResponse


class ActionOutcomeCreateRequest(BaseModel):
    """A later Session, observed effect, and an honest conclusion."""

    model_config = ConfigDict(extra="forbid")

    evaluation_session_id: UUID
    classification: ActionOutcomeClassification
    public_conclusion: str | None = Field(default=None, min_length=1, max_length=2000)
    confidential_conclusion: str | None = Field(
        default=None, min_length=1, max_length=5000
    )
    concluded_hypothesis_status: HypothesisStatus | None = None

    @field_validator("public_conclusion", "confidential_conclusion")
    @classmethod
    def normalize_conclusion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("conclusions must not be blank")
        return normalized

    @field_validator("concluded_hypothesis_status")
    @classmethod
    def reject_proposed_conclusion(
        cls, value: HypothesisStatus | None
    ) -> HypothesisStatus | None:
        if value is HypothesisStatus.PROPOSED:
            raise ValueError("a concluded hypothesis cannot remain PROPOSED")
        return value

    @model_validator(mode="after")
    def require_conclusion(self) -> Self:
        if self.public_conclusion is None and self.confidential_conclusion is None:
            raise ValueError("an outcome requires a conclusion")
        return self


class ActionOutcomeResponse(BaseModel):
    """Outcome projection that protects Engineering-only conclusions."""

    outcome_id: UUID
    action_id: UUID
    evaluation_session_id: UUID
    classification: ActionOutcomeClassification
    public_conclusion: str | None
    confidential_conclusion: str | None = None
    concluded_hypothesis_status: HypothesisStatus | None = None
    author_user_id: UUID
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, outcome: ActionOutcome, actor_role: Role) -> Self:
        engineering = actor_role is Role.ENGINEER
        return cls(
            outcome_id=outcome.outcome_id,
            action_id=outcome.action_id,
            evaluation_session_id=outcome.evaluation_session_id,
            classification=outcome.classification,
            public_conclusion=outcome.public_conclusion,
            confidential_conclusion=(
                outcome.confidential_conclusion if engineering else None
            ),
            concluded_hypothesis_status=(
                outcome.concluded_hypothesis_status if engineering else None
            ),
            author_user_id=outcome.author_user_id,
            visibility_level=outcome.visibility_level,
            created_at=outcome.created_at,
            updated_at=outcome.updated_at,
        )


class ActionEvaluationResponse(BaseModel):
    """Explicitly distinguish no evaluation from a stored Outcome."""

    action_id: UUID
    evaluation_status: ActionEvaluationStatus
    outcome: ActionOutcomeResponse | None

    @classmethod
    def from_action(cls, action: Action, actor_role: Role) -> Self:
        if action.outcome is None:
            return cls(
                action_id=action.action_id,
                evaluation_status=ActionEvaluationStatus.NOT_EVALUATED,
                outcome=None,
            )
        return cls(
            action_id=action.action_id,
            evaluation_status=ActionEvaluationStatus(
                action.outcome.classification.value
            ),
            outcome=ActionOutcomeResponse.from_model(action.outcome, actor_role),
        )


class LearningChainResponse(BaseModel):
    """Authorized traversal from reasoning to work and observed result."""

    action: ActionResponse
    priority: PriorityResponse | None = None
    hypothesis: HypothesisResponse | None = None
    analysis: SessionAnalysisResponse | None = None
    evaluation: ActionEvaluationResponse
