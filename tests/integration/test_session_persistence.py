"""PostgreSQL contracts for motorsport Session persistence."""

import os
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from raceops.core.config import Settings
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.models import RaceSession

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
def test_session_round_trip_starts_planned_with_open_results(
    database_engine: Engine,
) -> None:
    with DbSession(database_engine) as db, db.begin():
        resources = _create_operational_context(db, "Session Defaults")
        race_session = RaceSession(
            team_id=resources.team_id,
            event_id=resources.event_id,
            driver_id=resources.driver_id,
            vehicle_id=resources.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 9, 15, 0, tzinfo=UTC),
        )
        db.add(race_session)
        db.flush()

        assert race_session.status is SessionStatus.PLANNED
        assert race_session.results_status is ResultsStatus.OPEN
        assert race_session.started_at is None
        assert race_session.ended_at is None
        assert race_session.results_locked_by_user_id is None
        assert race_session.results_locked_at is None
        assert race_session.scheduled_at.tzinfo is not None
        assert race_session.created_at.tzinfo is not None


@pytest.mark.integration
@requires_database
def test_session_rejects_each_cross_team_assignment(database_engine: Engine) -> None:
    with DbSession(database_engine) as db, db.begin():
        home = _create_operational_context(db, "Session Home")
        foreign = _create_operational_context(db, "Session Foreign")

    invalid_assignments = [
        (foreign.event_id, home.driver_id, home.vehicle_id),
        (home.event_id, foreign.driver_id, home.vehicle_id),
        (home.event_id, home.driver_id, foreign.vehicle_id),
    ]
    for event_id, driver_id, vehicle_id in invalid_assignments:
        with DbSession(database_engine) as db:
            db.add(
                RaceSession(
                    team_id=home.team_id,
                    event_id=event_id,
                    driver_id=driver_id,
                    vehicle_id=vehicle_id,
                    session_type="Practice",
                    scheduled_at=datetime(2026, 11, 9, 15, 0, tzinfo=UTC),
                )
            )
            with pytest.raises(IntegrityError):
                db.commit()


@pytest.mark.integration
@requires_database
def test_session_rejects_incoherent_activity_and_result_states(
    database_engine: Engine,
) -> None:
    with DbSession(database_engine) as db, db.begin():
        resources = _create_operational_context(db, "Session Constraints")

    started_at = datetime(2026, 11, 9, 15, 0, tzinfo=UTC)
    invalid_sessions = [
        RaceSession(
            team_id=resources.team_id,
            event_id=resources.event_id,
            driver_id=resources.driver_id,
            vehicle_id=resources.vehicle_id,
            session_type="Practice",
            scheduled_at=started_at,
            status=SessionStatus.ACTIVE,
        ),
        RaceSession(
            team_id=resources.team_id,
            event_id=resources.event_id,
            driver_id=resources.driver_id,
            vehicle_id=resources.vehicle_id,
            session_type="Practice",
            scheduled_at=started_at,
            status=SessionStatus.COMPLETED,
            started_at=started_at,
            ended_at=started_at - timedelta(minutes=1),
        ),
        RaceSession(
            team_id=resources.team_id,
            event_id=resources.event_id,
            driver_id=resources.driver_id,
            vehicle_id=resources.vehicle_id,
            session_type="Practice",
            scheduled_at=started_at,
            results_status=ResultsStatus.LOCKED,
        ),
    ]

    for invalid in invalid_sessions:
        with DbSession(database_engine) as db:
            db.add(invalid)
            with pytest.raises(IntegrityError):
                db.commit()


@pytest.mark.integration
@requires_database
def test_session_accepts_locked_results_only_for_terminal_activity(
    database_engine: Engine,
) -> None:
    with DbSession(database_engine) as db, db.begin():
        resources = _create_operational_context(db, "Session Locked")
        started_at = datetime(2026, 11, 9, 15, 0, tzinfo=UTC)
        race_session = RaceSession(
            team_id=resources.team_id,
            event_id=resources.event_id,
            driver_id=resources.driver_id,
            vehicle_id=resources.vehicle_id,
            session_type="Qualifying",
            scheduled_at=started_at,
            status=SessionStatus.COMPLETED,
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=15),
            results_status=ResultsStatus.LOCKED,
            results_locked_by_user_id=resources.user_id,
            results_locked_at=started_at + timedelta(minutes=20),
        )
        db.add(race_session)
        db.flush()

        assert race_session.results_status is ResultsStatus.LOCKED
        assert race_session.results_locked_by_user_id == resources.user_id


class _OperationalContext:
    def __init__(
        self,
        *,
        team_id: UUID,
        user_id: UUID,
        event_id: UUID,
        driver_id: UUID,
        vehicle_id: UUID,
    ) -> None:
        self.team_id = team_id
        self.user_id = user_id
        self.event_id = event_id
        self.driver_id = driver_id
        self.vehicle_id = vehicle_id


def _create_operational_context(
    db: DbSession,
    prefix: str,
) -> _OperationalContext:
    team = Team(name=f"{prefix} Team {uuid4()}")
    user = User(
        email=f"session-{uuid4()}@example.com",
        password_hash="$argon2id$session-placeholder",
    )
    db.add(TeamMembership(user=user, team=team, role=Role.ENGINEER))
    db.flush()
    driver = Driver(
        team_id=team.team_id,
        display_name=f"{prefix} Driver",
    )
    vehicle = Vehicle(
        team_id=team.team_id,
        identifier=f"{prefix} Vehicle",
    )
    track = Track(team_id=team.team_id, name=f"{prefix} Track")
    db.add_all([driver, vehicle, track])
    db.flush()
    event = Event(
        team_id=team.team_id,
        track_id=track.track_id,
        name=f"{prefix} Event",
        starts_on=date(2026, 11, 9),
    )
    db.add(event)
    db.flush()
    return _OperationalContext(
        team_id=team.team_id,
        user_id=user.user_id,
        event_id=event.event_id,
        driver_id=driver.driver_id,
        vehicle_id=vehicle.vehicle_id,
    )
