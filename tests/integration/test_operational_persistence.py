"""PostgreSQL contracts for Driver, Vehicle, Track, and Event persistence."""

import os
from collections.abc import Iterator
from datetime import date
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.operations.enums import DriverStatus, EventStatus, VehicleStatus
from raceops.operations.models import Driver, Event, Track, Vehicle

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    """Return a migrated PostgreSQL engine for an integration test."""
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
def test_operational_resources_round_trip_with_defaults(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Operations Team"))
        user = User(
            email=f"operations-{uuid4()}@example.com",
            password_hash="$argon2id$operations-placeholder",
        )
        membership = TeamMembership(user=user, team=team, role=Role.DRIVER)
        session.add(membership)
        session.flush()

        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id,
            display_name="Alex Rivera",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier="Kart 27")
        track = Track(
            team_id=team.team_id,
            name="Autódromo Local",
            location="Ciudad de México",
        )
        session.add_all([driver, vehicle, track])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name="Prueba de noviembre",
            starts_on=date(2026, 11, 8),
        )
        session.add(event)
        session.flush()

        assert driver.status is DriverStatus.ACTIVE
        assert vehicle.status is VehicleStatus.READY
        assert event.status is EventStatus.PLANNED
        assert all(
            resource.created_at.tzinfo is not None
            for resource in (driver, vehicle, track, event)
        )


@pytest.mark.integration
@requires_database
def test_driver_user_link_requires_membership_in_same_team(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        first_team = Team(name=_unique("Driver Home Team"))
        second_team = Team(name=_unique("Other Team"))
        user = User(
            email=f"linked-driver-{uuid4()}@example.com",
            password_hash="$argon2id$driver-placeholder",
        )
        session.add(TeamMembership(user=user, team=first_team, role=Role.DRIVER))
        session.add(second_team)
        session.flush()
        user_id = user.user_id
        second_team_id = second_team.team_id

    with Session(database_engine) as session:
        session.add(
            Driver(
                team_id=second_team_id,
                user_id=user_id,
                display_name="Cross Team Driver",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@requires_database
def test_user_can_link_one_driver_per_team(database_engine: Engine) -> None:
    with Session(database_engine) as session, session.begin():
        first_team = Team(name=_unique("First Driver Team"))
        second_team = Team(name=_unique("Second Driver Team"))
        user = User(
            email=f"multi-driver-{uuid4()}@example.com",
            password_hash="$argon2id$multi-driver-placeholder",
        )
        session.add_all(
            [
                TeamMembership(user=user, team=first_team, role=Role.DRIVER),
                TeamMembership(user=user, team=second_team, role=Role.DRIVER),
            ]
        )
        session.flush()
        session.add_all(
            [
                Driver(
                    team_id=first_team.team_id,
                    user_id=user.user_id,
                    display_name="First Profile",
                ),
                Driver(
                    team_id=second_team.team_id,
                    user_id=user.user_id,
                    display_name="Second Profile",
                ),
            ]
        )
        user_id = user.user_id
        first_team_id = first_team.team_id

    with Session(database_engine) as session:
        session.add(
            Driver(
                team_id=first_team_id,
                user_id=user_id,
                display_name="Duplicate Profile",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@requires_database
def test_vehicle_identifier_is_unique_only_inside_team(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        first_team = Team(name=_unique("First Vehicle Team"))
        second_team = Team(name=_unique("Second Vehicle Team"))
        session.add_all([first_team, second_team])
        session.flush()
        session.add_all(
            [
                Vehicle(team_id=first_team.team_id, identifier="Kart 7"),
                Vehicle(team_id=second_team.team_id, identifier="Kart 7"),
            ]
        )
        first_team_id = first_team.team_id

    with Session(database_engine) as session:
        session.add(Vehicle(team_id=first_team_id, identifier="Kart 7"))
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@requires_database
def test_event_rejects_cross_team_track_and_invalid_dates(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        first_team = Team(name=_unique("Event Team"))
        second_team = Team(name=_unique("Track Team"))
        session.add_all([first_team, second_team])
        session.flush()
        track = Track(team_id=second_team.team_id, name="Foreign Track")
        session.add(track)
        session.flush()
        first_team_id = first_team.team_id
        track_id = track.track_id

    with Session(database_engine) as session:
        session.add(
            Event(
                team_id=first_team_id,
                track_id=track_id,
                name="Cross Team Event",
                starts_on=date(2026, 11, 8),
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()

    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Date Team"))
        session.add(team)
        session.flush()
        track = Track(team_id=team.team_id, name="Date Track")
        session.add(track)
        session.flush()
        session.add(
            Event(
                team_id=team.team_id,
                track_id=track.track_id,
                name="Invalid Date Event",
                starts_on=date(2026, 11, 9),
                ends_on=date(2026, 11, 8),
            )
        )
        with pytest.raises(IntegrityError):
            session.flush()


@pytest.mark.integration
@requires_database
def test_database_preserves_referenced_track_and_team(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Preserved Operations Team"))
        session.add(team)
        session.flush()
        track = Track(team_id=team.team_id, name="Preserved Track")
        session.add(track)
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name="Preserved Event",
            starts_on=date(2026, 11, 8),
        )
        session.add(event)
        session.flush()
        team_id = team.team_id
        track_id = track.track_id

    with Session(database_engine) as session:
        session.delete(session.get_one(Track, track_id))
        with pytest.raises(IntegrityError):
            session.commit()

    with Session(database_engine) as session:
        session.delete(session.get_one(Team, team_id))
        with pytest.raises(IntegrityError):
            session.commit()


def _unique(prefix: str) -> str:
    return f"{prefix} {uuid4()}"
