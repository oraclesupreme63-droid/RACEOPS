"""Secure local bootstrap for RaceOps' first team administrator."""

import argparse
import getpass
import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from raceops.core.config import get_settings
from raceops.core.logging import configure_logging
from raceops.db.session import build_engine, build_session_factory
from raceops.iam.credentials import hash_password
from raceops.iam.enums import Role
from raceops.iam.errors import (
    BootstrapConflictError,
    BootstrapValidationError,
    PasswordPolicyError,
)
from raceops.iam.models import Team, TeamMembership, User

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
logger = logging.getLogger("raceops.iam.bootstrap")


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    """Non-secret identifiers created by a successful bootstrap."""

    user_id: UUID
    team_id: UUID
    membership_id: UUID


def bootstrap_administrator(
    session_factory: sessionmaker[Session],
    *,
    email: str,
    team_name: str,
    password: str,
) -> BootstrapResult:
    """Create Team, User, and Administrator membership atomically."""
    normalized_email = _normalize_email(email)
    normalized_team_name = _normalize_team_name(team_name)
    try:
        password_hash = hash_password(password)
    except PasswordPolicyError as error:
        raise BootstrapValidationError(str(error)) from error

    try:
        with session_factory() as session, session.begin():
            user = User(email=normalized_email, password_hash=password_hash)
            team = Team(name=normalized_team_name)
            membership = TeamMembership(
                user=user,
                team=team,
                role=Role.ADMINISTRATOR,
            )
            session.add(membership)
            session.flush()
            result = BootstrapResult(
                user_id=user.user_id,
                team_id=team.team_id,
                membership_id=membership.membership_id,
            )
    except IntegrityError as error:
        raise BootstrapConflictError(
            "bootstrap conflicts with existing identity data"
        ) from error

    return result


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the local operator command without accepting password arguments."""
    parser = _build_parser()
    options = parser.parse_args(arguments)
    settings = get_settings()
    configure_logging(level=settings.log_level, environment=settings.env)

    try:
        password = _read_confirmed_password()
        engine = build_engine(settings)
        try:
            result = bootstrap_administrator(
                build_session_factory(engine),
                email=options.email,
                team_name=options.team_name,
                password=password,
            )
        finally:
            engine.dispose()
    except (BootstrapValidationError, BootstrapConflictError) as error:
        logger.error(str(error), extra={"event": "identity.bootstrap_rejected"})
        return 1
    except SQLAlchemyError:
        logger.exception(
            "bootstrap database operation failed",
            extra={"event": "identity.bootstrap_failed"},
        )
        return 1

    logger.info(
        "administrator bootstrap completed",
        extra={
            "event": "identity.bootstrap_completed",
            "user_id": str(result.user_id),
            "team_id": str(result.team_id),
            "membership_id": str(result.membership_id),
        },
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create the first RaceOps team administrator atomically."
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--team-name", required=True)
    return parser


def _read_confirmed_password() -> str:
    password = getpass.getpass("Administrator password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise BootstrapValidationError("password confirmation does not match")
    return password


def _normalize_email(email: str) -> str:
    normalized_email = email.strip().lower()
    if (
        len(normalized_email) < 3
        or len(normalized_email) > 254
        or _EMAIL_PATTERN.fullmatch(normalized_email) is None
    ):
        raise BootstrapValidationError("email is invalid")
    return normalized_email


def _normalize_team_name(team_name: str) -> str:
    normalized_team_name = team_name.strip()
    if not normalized_team_name or len(normalized_team_name) > 120:
        raise BootstrapValidationError(
            "team name must contain between 1 and 120 characters"
        )
    return normalized_team_name


if __name__ == "__main__":
    raise SystemExit(main())
