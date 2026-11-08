"""Public request and response schemas for the identity API."""

import re
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from raceops.iam.credentials import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.identity import CurrentIdentity

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LoginRequest(BaseModel):
    """Credentials and optional team context accepted by the login endpoint."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
    )
    team_id: UUID | None = None

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if _EMAIL_PATTERN.fullmatch(normalized) is None:
            raise ValueError("email must be valid")
        return normalized


class AccessTokenResponse(BaseModel):
    """Short-lived bearer token response."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(gt=0)


class TeamChoice(BaseModel):
    """Minimal authorized team reference disclosed after valid credentials."""

    team_id: UUID
    name: str


class TeamContextProblemDetails(BaseModel):
    """Documented RFC 9457 extension returned when team selection is required."""

    type: str
    title: str
    status: Literal[409]
    detail: str
    instance: str
    code: Literal["team_context_required"]
    trace_id: str
    teams: list[TeamChoice]


class UserIdentityResponse(BaseModel):
    user_id: UUID
    email: str
    status: IdentityStatus


class TeamIdentityResponse(BaseModel):
    team_id: UUID
    name: str
    status: IdentityStatus


class MembershipIdentityResponse(BaseModel):
    membership_id: UUID
    role: Role
    status: IdentityStatus


class CurrentIdentityResponse(BaseModel):
    """Current database-backed identity exposed without credential material."""

    user: UserIdentityResponse
    team: TeamIdentityResponse
    membership: MembershipIdentityResponse

    @classmethod
    def from_current_identity(cls, identity: CurrentIdentity) -> Self:
        return cls(
            user=UserIdentityResponse(
                user_id=identity.user_id,
                email=identity.email,
                status=IdentityStatus.ACTIVE,
            ),
            team=TeamIdentityResponse(
                team_id=identity.team_id,
                name=identity.team_name,
                status=IdentityStatus.ACTIVE,
            ),
            membership=MembershipIdentityResponse(
                membership_id=identity.membership_id,
                role=identity.role,
                status=IdentityStatus.ACTIVE,
            ),
        )
