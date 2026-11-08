"""PostgreSQL integration tests for current identity and secure bootstrap."""

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from raceops.core.config import Settings
from raceops.db.session import build_session_factory
from raceops.iam.bootstrap_admin import bootstrap_administrator
from raceops.iam.credentials import verify_password
from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.errors import BootstrapConflictError, InvalidAccessTokenError
from raceops.iam.identity import resolve_current_identity
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import AccessTokenClaims

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    settings = Settings()
    command.upgrade(Config("alembic.ini"), "head")
    engine = create_engine(
        settings.database_url.get_secret_value(),
        connect_args={"connect_timeout": settings.database_connect_timeout_seconds},
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.mark.integration
@requires_database
def test_bootstrap_creates_normalized_administrator_atomically(
    database_engine: Engine,
) -> None:
    factory = build_session_factory(database_engine)
    unique = uuid4()
    password = "a secure bootstrap password"

    result = bootstrap_administrator(
        factory,
        email=f" Admin-{unique}@Example.COM ",
        team_name="  Apex Student Racing  ",
        password=password,
    )

    with factory() as session:
        user = session.get_one(User, result.user_id)
        team = session.get_one(Team, result.team_id)
        membership = session.get_one(TeamMembership, result.membership_id)

        assert user.email == f"admin-{unique}@example.com"
        assert password not in user.password_hash
        assert verify_password(password, user.password_hash) is True
        assert team.name == "Apex Student Racing"
        assert membership.role is Role.ADMINISTRATOR
        assert membership.user_id == user.user_id
        assert membership.team_id == team.team_id


@pytest.mark.integration
@requires_database
def test_bootstrap_conflict_rolls_back_team_and_membership(
    database_engine: Engine,
) -> None:
    factory = build_session_factory(database_engine)
    email = f"bootstrap-conflict-{uuid4()}@example.com"
    bootstrap_administrator(
        factory,
        email=email,
        team_name="Original Team",
        password="original secure password",
    )

    with pytest.raises(BootstrapConflictError):
        bootstrap_administrator(
            factory,
            email=email,
            team_name="Must Roll Back Team",
            password="another secure password",
        )

    with factory() as session:
        rolled_back_teams = session.scalar(
            select(func.count())
            .select_from(Team)
            .where(Team.name == "Must Roll Back Team")
        )
        assert rolled_back_teams == 0


@pytest.mark.integration
@requires_database
def test_current_identity_is_resolved_and_role_change_is_immediate(
    database_engine: Engine,
) -> None:
    factory, claims = _persist_identity(database_engine)

    with factory() as session:
        identity = resolve_current_identity(session, claims)
        assert identity.role is Role.ENGINEER

        membership = session.get_one(TeamMembership, claims.membership_id)
        membership.role = Role.TEAM_MANAGER
        session.commit()

    with factory() as session:
        identity = resolve_current_identity(session, claims)
        assert identity.role is Role.TEAM_MANAGER


@pytest.mark.integration
@requires_database
@pytest.mark.parametrize("inactive_entity", ["user", "membership", "team"])
def test_current_identity_rejects_each_inactive_boundary(
    database_engine: Engine,
    inactive_entity: str,
) -> None:
    factory, claims = _persist_identity(database_engine)

    with factory() as session:
        membership = session.get_one(TeamMembership, claims.membership_id)
        if inactive_entity == "user":
            session.get_one(User, claims.user_id).status = IdentityStatus.INACTIVE
        elif inactive_entity == "membership":
            membership.status = IdentityStatus.INACTIVE
        else:
            session.get_one(Team, membership.team_id).status = IdentityStatus.INACTIVE
        session.commit()

    with factory() as session, pytest.raises(InvalidAccessTokenError):
        resolve_current_identity(session, claims)


@pytest.mark.integration
@requires_database
def test_current_identity_rejects_mismatched_or_missing_references(
    database_engine: Engine,
) -> None:
    factory, claims = _persist_identity(database_engine)
    mismatched = AccessTokenClaims(
        user_id=uuid4(),
        membership_id=claims.membership_id,
        token_id=uuid4(),
        issued_at=claims.issued_at,
        expires_at=claims.expires_at,
    )

    with factory() as session, pytest.raises(InvalidAccessTokenError):
        resolve_current_identity(session, mismatched)


def _persist_identity(
    database_engine: Engine,
) -> tuple[sessionmaker[Session], AccessTokenClaims]:
    factory = build_session_factory(database_engine)
    with factory() as session, session.begin():
        user = User(
            email=f"identity-{uuid4()}@example.com",
            password_hash="$argon2id$integration-placeholder",
        )
        team = Team(name=f"Identity Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=Role.ENGINEER)
        session.add(membership)
        session.flush()
        now = datetime.now(UTC)
        claims = AccessTokenClaims(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            token_id=uuid4(),
            issued_at=now,
            expires_at=now + timedelta(minutes=15),
        )
    return factory, claims
