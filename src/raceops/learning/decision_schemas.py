"""Validated representations for actionable priorities and assigned work."""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.learning.enums import ActionStatus, ActionType, TargetIntent
from raceops.learning.models import Action, Priority

RECIPIENT_ROLES = frozenset({Role.DRIVER, Role.ENGINEER, Role.MECHANIC})


class DecisionTargetRequest(BaseModel):
    """A real target Session or an honest unresolved NEXT_SESSION intent."""

    model_config = ConfigDict(extra="forbid")

    target_intent: TargetIntent = TargetIntent.NEXT_SESSION
    target_session_id: UUID | None = None

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if self.target_intent is TargetIntent.NEXT_SESSION:
            if self.target_session_id is not None:
                raise ValueError("NEXT_SESSION cannot include target_session_id")
        elif self.target_session_id is None:
            raise ValueError("SPECIFIC_SESSION requires target_session_id")
        return self


class PriorityCreateRequest(DecisionTargetRequest):
    """One concrete focus, optionally highlighted among the main three."""

    hypothesis_id: UUID | None = None
    recipient_role: Role
    recipient_user_id: UUID | None = None
    description: str = Field(min_length=1, max_length=2000)
    is_main: bool = True
    rank: int | None = Field(default=None, ge=1, le=3)

    @field_validator("recipient_role")
    @classmethod
    def validate_recipient_role(cls, value: Role) -> Role:
        if value not in RECIPIENT_ROLES:
            raise ValueError("recipient_role must be DRIVER, ENGINEER, or MECHANIC")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_rank(self) -> Self:
        if not self.is_main and self.rank is not None:
            raise ValueError("a non-main priority cannot have rank")
        return self


class PriorityUpdateRequest(BaseModel):
    """Update wording or main placement without changing its audience."""

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(default=None, min_length=1, max_length=2000)
    is_main: bool | None = None
    rank: int | None = Field(default=None, ge=1, le=3)

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
        if "description" in self.model_fields_set and self.description is None:
            raise ValueError("description cannot be null")
        if self.is_main is False and self.rank is not None:
            raise ValueError("a non-main priority cannot have rank")
        if "rank" in self.model_fields_set and self.is_main is not True:
            raise ValueError("rank updates must explicitly keep is_main true")
        return self


class PriorityResponse(BaseModel):
    """Priority projection with confidential motivation removed by audience."""

    priority_id: UUID
    source_session_id: UUID
    target_session_id: UUID | None
    target_intent: TargetIntent
    hypothesis_id: UUID | None = None
    recipient_role: Role
    recipient_user_id: UUID | None
    description: str
    is_main: bool
    rank: int | None
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, priority: Priority, actor_role: Role) -> Self:
        return cls(
            priority_id=priority.priority_id,
            source_session_id=priority.source_session_id,
            target_session_id=priority.target_session_id,
            target_intent=priority.target_intent,
            hypothesis_id=(
                priority.hypothesis_id if actor_role is Role.ENGINEER else None
            ),
            recipient_role=priority.recipient_role,
            recipient_user_id=priority.recipient_user_id,
            description=priority.description,
            is_main=priority.is_main,
            rank=priority.rank,
            visibility_level=priority.visibility_level,
            created_at=priority.created_at,
            updated_at=priority.updated_at,
        )


class PriorityPageResponse(BaseModel):
    items: list[PriorityResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class ActionCreateRequest(DecisionTargetRequest):
    """Assigned work with explicit motivation and protected technical detail."""

    hypothesis_id: UUID | None = None
    priority_id: UUID | None = None
    assignee_user_id: UUID | None = None
    assignee_role: Role
    action_type: ActionType
    public_summary: str | None = Field(default=None, min_length=1, max_length=2000)
    confidential_detail: str | None = Field(default=None, min_length=1, max_length=5000)

    @field_validator("assignee_role")
    @classmethod
    def validate_assignee_role(cls, value: Role) -> Role:
        if value not in RECIPIENT_ROLES:
            raise ValueError("assignee_role must be DRIVER, ENGINEER, or MECHANIC")
        return value

    @field_validator("public_summary", "confidential_detail")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_motivation(self) -> Self:
        if not any(
            (
                self.hypothesis_id,
                self.priority_id,
                self.public_summary,
                self.confidential_detail,
            )
        ):
            raise ValueError("an action requires a motivation")
        if self.assignee_role is not Role.ENGINEER and self.public_summary is None:
            raise ValueError("non-Engineer assignees require a public_summary")
        return self


class ActionCancellationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=1000)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("reason must not be blank")
        return normalized


class ActionResponse(BaseModel):
    """Action projection that never serializes forbidden technical fields."""

    action_id: UUID
    source_session_id: UUID
    target_session_id: UUID | None
    target_intent: TargetIntent
    hypothesis_id: UUID | None = None
    priority_id: UUID | None = None
    assignee_user_id: UUID | None
    assignee_role: Role
    action_type: ActionType
    status: ActionStatus
    public_summary: str | None
    confidential_detail: str | None = None
    cancellation_reason: str | None
    visibility_level: Visibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, action: Action, actor_role: Role) -> Self:
        engineering = actor_role is Role.ENGINEER
        return cls(
            action_id=action.action_id,
            source_session_id=action.source_session_id,
            target_session_id=action.target_session_id,
            target_intent=action.target_intent,
            hypothesis_id=action.hypothesis_id if engineering else None,
            priority_id=action.priority_id if engineering else None,
            assignee_user_id=action.assignee_user_id,
            assignee_role=action.assignee_role,
            action_type=action.action_type,
            status=action.status,
            public_summary=action.public_summary,
            confidential_detail=action.confidential_detail if engineering else None,
            cancellation_reason=action.cancellation_reason,
            visibility_level=action.visibility_level,
            created_at=action.created_at,
            updated_at=action.updated_at,
        )


class ActionPageResponse(BaseModel):
    items: list[ActionResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
