"""PostgreSQL integration contracts for IAM persistence."""

import os
from collections.abc import Iterator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    """Return a migrated PostgreSQL engine for an integration test."""
    settings = Settings()
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    engine = create_engine(
        settings.database_url.get_secret_value(),
        connect_args={
            "connect_timeout": settings.database_connect_timeout_seconds,
        },
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.mark.integration
@pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
def test_user_can_hold_one_membership_in_each_team(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session:
        user = User(
            email=_unique_email("multi-team-user"),
            password_hash="$argon2id$integration-test-placeholder",
        )
        first_team = Team(name="First Racing Team")
        second_team = Team(name="Second Racing Team")
        first_membership = TeamMembership(
            user=user,
            team=first_team,
            role=Role.ENGINEER,
        )
        second_membership = TeamMembership(
            user=user,
            team=second_team,
            role=Role.DRIVER,
        )
        session.add_all([first_membership, second_membership])
        session.commit()

        membership_ids = {
            first_membership.membership_id,
            second_membership.membership_id,
        }
        loaded_memberships = session.scalars(
            select(TeamMembership).where(
                TeamMembership.membership_id.in_(membership_ids)
            )
        ).all()

        assert {membership.role for membership in loaded_memberships} == {
            Role.ENGINEER,
            Role.DRIVER,
        }
        assert all(
            membership.created_at.tzinfo is not None
            for membership in loaded_memberships
        )
        assert all(
            membership.updated_at.tzinfo is not None
            for membership in loaded_memberships
        )


@pytest.mark.integration
@pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
def test_database_rejects_non_normalized_or_duplicate_email(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session:
        session.add(
            User(
                email="Not-Normalized@Example.com",
                password_hash="$argon2id$integration-test-placeholder",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        duplicate_email = _unique_email("duplicate")
        session.add_all(
            [
                User(
                    email=duplicate_email,
                    password_hash="$argon2id$first-placeholder",
                ),
                User(
                    email=duplicate_email,
                    password_hash="$argon2id$second-placeholder",
                ),
            ]
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
def test_database_rejects_duplicate_membership(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session:
        user = User(
            email=_unique_email("single-membership"),
            password_hash="$argon2id$integration-test-placeholder",
        )
        team = Team(name="Single Membership Team")
        session.add_all(
            [
                TeamMembership(user=user, team=team, role=Role.ENGINEER),
                TeamMembership(user=user, team=team, role=Role.MECHANIC),
            ]
        )

        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
def test_database_restricts_deleting_referenced_user_or_team(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session:
        user = User(
            email=_unique_email("preserved-user"),
            password_hash="$argon2id$integration-test-placeholder",
        )
        team = Team(name="Preserved Racing Team")
        session.add(TeamMembership(user=user, team=team, role=Role.ADMINISTRATOR))
        session.commit()
        user_id = user.user_id
        team_id = team.team_id

    with Session(database_engine) as session:
        referenced_user = session.get_one(User, user_id)
        session.delete(referenced_user)
        with pytest.raises(IntegrityError):
            session.commit()

    with Session(database_engine) as session:
        referenced_team = session.get_one(Team, team_id)
        session.delete(referenced_team)
        with pytest.raises(IntegrityError):
            session.commit()


def _unique_email(prefix: str) -> str:
    """Return a normalized email unique to one integration test execution."""
    return f"{prefix}-{uuid4()}@example.com"
