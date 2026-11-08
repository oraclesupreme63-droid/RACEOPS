"""Resolve the current authorization identity from PostgreSQL."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.errors import InvalidAccessTokenError
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import AccessTokenClaims


@dataclass(frozen=True, slots=True)
class CurrentIdentity:
    """Fresh server-side view of a user in one team context."""

    user_id: UUID
    email: str
    membership_id: UUID
    team_id: UUID
    team_name: str
    role: Role


def resolve_current_identity(
    session: Session,
    claims: AccessTokenClaims,
) -> CurrentIdentity:
    """Resolve token references and require active User, Membership, and Team."""
    statement = (
        select(TeamMembership, User, Team)
        .join(User, TeamMembership.user_id == User.user_id)
        .join(Team, TeamMembership.team_id == Team.team_id)
        .where(
            TeamMembership.membership_id == claims.membership_id,
            TeamMembership.user_id == claims.user_id,
        )
    )
    row = session.execute(statement).one_or_none()
    if row is None:
        raise InvalidAccessTokenError("access token is invalid")

    membership, user, team = row
    if (
        user.status is not IdentityStatus.ACTIVE
        or membership.status is not IdentityStatus.ACTIVE
        or team.status is not IdentityStatus.ACTIVE
    ):
        raise InvalidAccessTokenError("access token is invalid")

    return CurrentIdentity(
        user_id=user.user_id,
        email=user.email,
        membership_id=membership.membership_id,
        team_id=team.team_id,
        team_name=team.name,
        role=membership.role,
    )
