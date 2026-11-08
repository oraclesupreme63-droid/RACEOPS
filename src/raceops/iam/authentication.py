"""Credential authentication and active team-context selection."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from raceops.iam.credentials import hash_password, verify_password
from raceops.iam.enums import IdentityStatus
from raceops.iam.errors import InvalidCredentialsError, TeamContextRequiredError
from raceops.iam.models import Team, TeamMembership, User

_DUMMY_PASSWORD_HASH = hash_password("timing-defense-not-a-real-password")


@dataclass(frozen=True, slots=True)
class AuthenticatedMembership:
    """Validated User and Membership identifiers selected for a new token."""

    user_id: UUID
    membership_id: UUID
    team_id: UUID


def authenticate_credentials(
    session: Session,
    *,
    email: str,
    password: str,
    team_id: UUID | None,
) -> AuthenticatedMembership:
    """Authenticate credentials and select exactly one active team membership."""
    normalized_email = email.strip().lower()
    user = session.scalar(select(User).where(User.email == normalized_email))
    if user is None:
        verify_password(password, _DUMMY_PASSWORD_HASH)
        raise InvalidCredentialsError("unknown_email")

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("wrong_password")
    if user.status is not IdentityStatus.ACTIVE:
        raise InvalidCredentialsError("inactive_user")

    active_memberships = session.execute(
        select(TeamMembership, Team)
        .join(Team, TeamMembership.team_id == Team.team_id)
        .where(
            TeamMembership.user_id == user.user_id,
            TeamMembership.status == IdentityStatus.ACTIVE,
            Team.status == IdentityStatus.ACTIVE,
        )
        .order_by(Team.name, Team.team_id)
    ).all()

    if team_id is not None:
        selected = next(
            (
                (membership, team)
                for membership, team in active_memberships
                if team.team_id == team_id
            ),
            None,
        )
        if selected is None:
            raise InvalidCredentialsError("invalid_team_context")
        membership, team = selected
        return AuthenticatedMembership(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team.team_id,
        )

    if not active_memberships:
        raise InvalidCredentialsError("no_active_membership")
    if len(active_memberships) > 1:
        raise TeamContextRequiredError(
            tuple((team.team_id, team.name) for _, team in active_memberships)
        )

    membership, team = active_memberships[0]
    return AuthenticatedMembership(
        user_id=user.user_id,
        membership_id=membership.membership_id,
        team_id=team.team_id,
    )
