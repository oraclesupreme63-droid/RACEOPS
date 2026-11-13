"""PostgreSQL proof for the local Phase 9 validation seed."""

import os
from collections.abc import Iterator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from raceops.core.config import Settings
from raceops.iam.credentials import verify_password
from raceops.iam.enums import Role
from raceops.iam.models import TeamMembership, User
from raceops.learning.models import Observation
from raceops.operations.models import Event
from raceops.sessions.enums import LapClassification, ResultsStatus, SectorStatus
from raceops.sessions.models import ConditionSnapshot, Lap, RaceSession, Sector
from raceops.validation.scenario import load_validation_scenario
from raceops.validation.seed_scenario import (
    ValidationScenarioConflictError,
    seed_validation_scenario,
)

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)
PASSWORD = "phase-nine-local-password"


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
def test_seed_creates_role_accounts_and_imperfect_replay_data(
    database_engine: Engine,
) -> None:
    scenario_id = f"it-{uuid4().hex[:12]}"
    session_factory = sessionmaker(database_engine)
    result = seed_validation_scenario(
        session_factory=session_factory,
        environment="test",
        scenario_id=scenario_id,
        password=PASSWORD,
    )

    with Session(database_engine) as session:
        memberships = list(
            session.scalars(
                select(TeamMembership).where(TeamMembership.team_id == result.team_id)
            )
        )
        users = list(
            session.scalars(
                select(User)
                .join(TeamMembership)
                .where(TeamMembership.team_id == result.team_id)
            )
        )
        sessions = list(
            session.scalars(
                select(RaceSession)
                .where(RaceSession.team_id == result.team_id)
                .order_by(RaceSession.scheduled_at)
            )
        )
        source = sessions[0]
        conditions = session.scalar(
            select(ConditionSnapshot).where(
                ConditionSnapshot.session_id == source.session_id
            )
        )
        invalid_laps = session.scalar(
            select(func.count())
            .select_from(Lap)
            .where(
                Lap.session_id == source.session_id,
                Lap.classification == LapClassification.INVALID,
            )
        )
        incomplete_sectors = session.scalar(
            select(func.count())
            .select_from(Sector)
            .join(Lap, Lap.lap_id == Sector.lap_id)
            .where(
                Lap.session_id == source.session_id,
                Sector.status == SectorStatus.INCOMPLETE,
            )
        )
        observations = session.scalar(
            select(func.count())
            .select_from(Observation)
            .where(Observation.session_id == source.session_id)
        )

    assert result.version == "phase-9-v1"
    assert {membership.role for membership in memberships} == set(Role)
    assert len(users) == len(Role)
    assert all(verify_password(PASSWORD, user.password_hash) for user in users)
    assert len(sessions) == 2
    assert all(item.results_status is ResultsStatus.LOCKED for item in sessions)
    assert sessions[1].scheduled_at > sessions[0].scheduled_at
    assert conditions is not None
    assert conditions.track_temperature is None
    assert invalid_laps == 1
    assert incomplete_sectors == 1
    assert observations == 1

    with pytest.raises(ValidationScenarioConflictError):
        seed_validation_scenario(
            session_factory=session_factory,
            environment="test",
            scenario_id=scenario_id,
            password=PASSWORD,
        )


@pytest.mark.integration
@requires_database
def test_public_timing_dataset_is_seeded_with_provenance_preserved(
    database_engine: Engine,
) -> None:
    scenario_id = f"public-{uuid4().hex[:10]}"
    result = seed_validation_scenario(
        session_factory=sessionmaker(database_engine),
        environment="test",
        scenario_id=scenario_id,
        password=PASSWORD,
        definition=load_validation_scenario("public-kristianstad-2025"),
    )

    with Session(database_engine) as session:
        event = session.scalar(select(Event).where(Event.team_id == result.team_id))
        sessions = list(
            session.scalars(
                select(RaceSession)
                .where(RaceSession.team_id == result.team_id)
                .order_by(RaceSession.started_at)
            )
        )
        lap_counts = [
            session.scalar(
                select(func.count())
                .select_from(Lap)
                .where(Lap.session_id == race_session.session_id)
            )
            for race_session in sessions
        ]
        sector_count = session.scalar(
            select(func.count())
            .select_from(Sector)
            .join(Lap, Lap.lap_id == Sector.lap_id)
            .where(Lap.session_id.in_([item.session_id for item in sessions]))
        )

    assert result.version == "phase-9-public-v1"
    assert event is not None
    assert "https://nocache.fiakarting.com/" in (event.description or "")
    assert lap_counts == [13, 25]
    assert sector_count == 114
