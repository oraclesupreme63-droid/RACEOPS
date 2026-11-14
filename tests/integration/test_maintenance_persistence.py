"""PostgreSQL contracts for team-scoped maintenance persistence."""

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import Team, TeamMembership, User
from raceops.learning.enums import ActionType, TargetIntent
from raceops.learning.models import Action, Observation
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.errors import InvalidMaintenanceStatusTransitionError
from raceops.maintenance.models import MaintenanceRecord
from raceops.maintenance.services import (
    cancel_maintenance_record,
    complete_maintenance_record,
)
from raceops.operations.enums import VehicleStatus
from raceops.operations.models import Driver, Event, Track, Vehicle
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
def test_maintenance_record_round_trip_preserves_context_and_vehicle_status(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Maintenance Team"))
        mechanic = _user("maintenance-mechanic")
        session.add(TeamMembership(user=mechanic, team=team, role=Role.MECHANIC))
        session.flush()

        driver = Driver(team_id=team.team_id, display_name="Test Driver")
        vehicle = Vehicle(team_id=team.team_id, identifier=_unique("Kart"))
        track = Track(team_id=team.team_id, name=_unique("Test Track"))
        session.add_all([driver, vehicle, track])
        session.flush()

        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=_unique("Maintenance Event"),
            starts_on=date(2026, 11, 13),
        )
        session.add(event)
        session.flush()

        race_session = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 13, 12, tzinfo=UTC),
        )
        session.add(race_session)
        session.flush()

        observation = Observation(
            team_id=team.team_id,
            session_id=race_session.session_id,
            vehicle_id=vehicle.vehicle_id,
            author_user_id=mechanic.user_id,
            description="Vibration under braking.",
        )
        action = Action(
            team_id=team.team_id,
            source_session_id=race_session.session_id,
            target_scope_id=race_session.session_id,
            assignee_user_id=mechanic.user_id,
            assignee_role=Role.MECHANIC,
            target_intent=TargetIntent.NEXT_SESSION,
            action_type=ActionType.MECHANICAL,
            public_summary="Inspect brake assembly.",
        )
        session.add_all([observation, action])
        session.flush()

        record = MaintenanceRecord(
            team_id=team.team_id,
            vehicle_id=vehicle.vehicle_id,
            responsible_user_id=mechanic.user_id,
            created_by_user_id=mechanic.user_id,
            session_id=race_session.session_id,
            observation_id=observation.observation_id,
            action_id=action.action_id,
            maintenance_type=MaintenanceType.INSPECTION,
            description="Inspect left-front brake and wheel assembly.",
        )
        session.add(record)
        session.flush()

        assert record.status is MaintenanceStatus.OPEN
        assert record.visibility_level is Visibility.ROLE_RESTRICTED
        assert record.created_at.tzinfo is not None
        assert vehicle.status is VehicleStatus.READY


@pytest.mark.integration
@requires_database
def test_maintenance_record_rejects_cross_team_vehicle_and_responsible_user(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        first_team = Team(name=_unique("First Maintenance Team"))
        second_team = Team(name=_unique("Second Maintenance Team"))
        first_user = _user("first-maintenance-user")
        second_user = _user("second-maintenance-user")
        session.add_all(
            [
                TeamMembership(user=first_user, team=first_team, role=Role.MECHANIC),
                TeamMembership(user=second_user, team=second_team, role=Role.MECHANIC),
            ]
        )
        session.flush()
        first_vehicle = Vehicle(
            team_id=first_team.team_id, identifier=_unique("First Kart")
        )
        second_vehicle = Vehicle(
            team_id=second_team.team_id, identifier=_unique("Second Kart")
        )
        session.add_all([first_vehicle, second_vehicle])
        session.flush()
        first_team_id = first_team.team_id
        first_user_id = first_user.user_id
        second_user_id = second_user.user_id
        first_vehicle_id = first_vehicle.vehicle_id
        second_vehicle_id = second_vehicle.vehicle_id

    with Session(database_engine) as session:
        session.add(
            MaintenanceRecord(
                team_id=first_team_id,
                vehicle_id=second_vehicle_id,
                responsible_user_id=first_user_id,
                created_by_user_id=first_user_id,
                maintenance_type=MaintenanceType.REPAIR,
                description="Cross-team vehicle must fail.",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()

    with Session(database_engine) as session:
        session.add(
            MaintenanceRecord(
                team_id=first_team_id,
                vehicle_id=first_vehicle_id,
                responsible_user_id=second_user_id,
                created_by_user_id=first_user_id,
                maintenance_type=MaintenanceType.REPAIR,
                description="Cross-team responsible user must fail.",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@requires_database
def test_maintenance_lifecycle_fields_are_database_enforced(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Lifecycle Maintenance Team"))
        mechanic = _user("lifecycle-mechanic")
        session.add(TeamMembership(user=mechanic, team=team, role=Role.MECHANIC))
        session.flush()
        vehicle = Vehicle(team_id=team.team_id, identifier=_unique("Lifecycle Kart"))
        session.add(vehicle)
        session.flush()
        team_id = team.team_id
        user_id = mechanic.user_id
        vehicle_id = vehicle.vehicle_id

    with Session(database_engine) as session:
        session.add(
            MaintenanceRecord(
                team_id=team_id,
                vehicle_id=vehicle_id,
                responsible_user_id=user_id,
                created_by_user_id=user_id,
                maintenance_type=MaintenanceType.REPAIR,
                status=MaintenanceStatus.COMPLETED,
                description="Invalid completion without evidence.",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.integration
@requires_database
def test_concurrent_terminal_commands_allow_exactly_one_winner(
    database_engine: Engine,
) -> None:
    with Session(database_engine) as session, session.begin():
        team = Team(name=_unique("Concurrent Maintenance Team"))
        mechanic = _user("concurrent-mechanic")
        membership = TeamMembership(user=mechanic, team=team, role=Role.MECHANIC)
        session.add(membership)
        session.flush()
        vehicle = Vehicle(team_id=team.team_id, identifier=_unique("Concurrent Kart"))
        session.add(vehicle)
        session.flush()
        record = MaintenanceRecord(
            team_id=team.team_id,
            vehicle_id=vehicle.vehicle_id,
            responsible_user_id=mechanic.user_id,
            created_by_user_id=mechanic.user_id,
            maintenance_type=MaintenanceType.REPAIR,
            description="Resolve concurrent lifecycle command safely.",
        )
        session.add(record)
        session.flush()
        maintenance_id = record.maintenance_id
        vehicle_id = vehicle.vehicle_id
        actor = CurrentIdentity(
            user_id=mechanic.user_id,
            email=mechanic.email,
            membership_id=membership.membership_id,
            team_id=team.team_id,
            team_name=team.name,
            role=membership.role,
        )

    barrier = Barrier(2)

    def complete() -> str:
        with Session(database_engine) as session:
            barrier.wait()
            try:
                complete_maintenance_record(
                    session,
                    actor,
                    maintenance_id,
                    completion_notes="Concurrent completion won.",
                )
            except InvalidMaintenanceStatusTransitionError:
                return "rejected"
            return "completed"

    def cancel() -> str:
        with Session(database_engine) as session:
            barrier.wait()
            try:
                cancel_maintenance_record(
                    session,
                    actor,
                    maintenance_id,
                    cancellation_reason="Concurrent cancellation won.",
                )
            except InvalidMaintenanceStatusTransitionError:
                return "rejected"
            return "cancelled"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [executor.submit(complete), executor.submit(cancel)]
        outcomes = [future.result(timeout=10) for future in results]

    assert outcomes.count("rejected") == 1
    assert len({*outcomes, "rejected"}) == 2
    with Session(database_engine) as session:
        persisted = session.get_one(MaintenanceRecord, maintenance_id)
        vehicle = session.get_one(Vehicle, vehicle_id)
        assert persisted.status in {
            MaintenanceStatus.COMPLETED,
            MaintenanceStatus.CANCELLED,
        }
        assert (persisted.completion_notes is None) != (
            persisted.cancellation_reason is None
        )
        assert vehicle.status is VehicleStatus.READY


def _user(prefix: str) -> User:
    return User(
        email=f"{prefix}-{uuid4()}@example.com",
        password_hash="$argon2id$maintenance-placeholder",
    )


def _unique(prefix: str) -> str:
    return f"{prefix} {uuid4()}"
