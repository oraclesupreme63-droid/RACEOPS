"""HTTP contracts for evidence-backed analysis and confidential hypotheses."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.learning.models import Observation
from raceops.main import create_app
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.models import (
    ConditionSnapshot,
    DriverFeedback,
    Lap,
    RaceSession,
    Sector,
)

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "analysis-api-test-secret-never-used-in-production"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)


@dataclass(frozen=True, slots=True)
class SeededIdentity:
    user_id: UUID
    membership_id: UUID
    team_id: UUID


@dataclass(frozen=True, slots=True)
class SeededContext:
    driver_identity: SeededIdentity
    driver_id: UUID
    vehicle_id: UUID
    session_id: UUID


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


@pytest.fixture
def application(database_engine: Engine) -> Iterator[FastAPI]:
    del database_engine
    base_settings = Settings()
    app = create_app(
        Settings(
            env="test",
            database_url=base_settings.database_url,
            jwt_secret=SecretStr(JWT_SECRET),
            access_token_ttl_minutes=15,
        )
    )
    try:
        yield app
    finally:
        app.state.db_engine.dispose()


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_analysis_hypothesis_confidentiality_and_authorized_summary(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    foreign_context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.ENGINEER
    )
    manager = _seed_identity(
        database_engine,
        team_id=context.driver_identity.team_id,
        role=Role.TEAM_MANAGER,
    )
    mechanic = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.MECHANIC
    )
    evidence = _seed_session_evidence(database_engine, context, engineer)
    foreign_observation_id = _seed_observation(
        database_engine,
        foreign_context,
        foreign_context.driver_identity,
    )
    transport = ASGITransport(app=application)

    analysis_payload = {
        "technical_detail": " Rear instability follows abrupt brake release. ",
        "authorized_summary": " Engineering is working on rear stability. ",
        "evidence": evidence,
    }
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{context.session_id}/analyses",
            headers=_headers(engineer),
            json=analysis_payload,
        )
        analysis_id = created.json()["analysis_id"]
        hypothesis = await client.post(
            f"/api/v1/analyses/{analysis_id}/hypotheses",
            headers=_headers(engineer),
            json={
                "description": "Abrupt brake release may amplify instability.",
                "cause_classification": "DRIVER_TECHNIQUE",
                "confidence": "MEDIUM",
            },
        )
        hypothesis_id = hypothesis.json()["hypothesis_id"]
        updated_hypothesis = await client.patch(
            f"/api/v1/hypotheses/{hypothesis_id}",
            headers=_headers(engineer),
            json={"confidence": "HIGH"},
        )
        premature_conclusion = await client.patch(
            f"/api/v1/hypotheses/{hypothesis_id}",
            headers=_headers(engineer),
            json={"status": "SUPPORTED"},
        )
        manager_full_read = await client.get(
            f"/api/v1/analyses/{analysis_id}", headers=_headers(manager)
        )
        driver_summaries = await client.get(
            f"/api/v1/sessions/{context.session_id}/analysis-summaries",
            headers=_headers(context.driver_identity),
        )
        mechanic_summaries = await client.get(
            f"/api/v1/sessions/{context.session_id}/analysis-summaries",
            headers=_headers(mechanic),
        )
        hidden_analysis = await client.post(
            f"/api/v1/sessions/{context.session_id}/analyses",
            headers=_headers(engineer),
            json={
                "technical_detail": "Confidential setup direction only.",
                "evidence": analysis_payload["evidence"],
            },
        )
        summaries_after_hidden = await client.get(
            f"/api/v1/sessions/{context.session_id}/analysis-summaries",
            headers=_headers(context.driver_identity),
        )
        foreign_evidence = await client.post(
            f"/api/v1/sessions/{context.session_id}/analyses",
            headers=_headers(engineer),
            json={
                "technical_detail": "Must reject foreign evidence.",
                "evidence": [
                    {
                        "evidence_type": "OBSERVATION",
                        "reference_id": str(foreign_observation_id),
                    }
                ],
            },
        )
        unrelated_driver_read = await client.get(
            f"/api/v1/sessions/{context.session_id}/analysis-summaries",
            headers=_headers(foreign_context.driver_identity),
        )
        no_evidence = await client.post(
            f"/api/v1/sessions/{context.session_id}/analyses",
            headers=_headers(engineer),
            json={"technical_detail": "Unsupported analysis.", "evidence": []},
        )
        engineering_list = await client.get(
            f"/api/v1/sessions/{context.session_id}/analyses",
            headers=_headers(engineer),
        )

    assert created.status_code == 201
    created_body = created.json()
    assert created_body["technical_detail"] == (
        "Rear instability follows abrupt brake release."
    )
    assert created_body["authorized_summary"] == (
        "Engineering is working on rear stability."
    )
    assert created_body["visibility_level"] == "ENGINEERING_CONFIDENTIAL"
    assert created_body["evidence"] == evidence
    assert hypothesis.status_code == 201
    assert hypothesis.json()["status"] == "PROPOSED"
    assert hypothesis.json()["visibility_level"] == "ENGINEERING_CONFIDENTIAL"
    assert updated_hypothesis.status_code == 200
    assert updated_hypothesis.json()["confidence"] == "HIGH"
    assert premature_conclusion.status_code == 422
    assert manager_full_read.status_code == 403
    assert driver_summaries.status_code == 200
    assert driver_summaries.json() == mechanic_summaries.json()
    assert len(driver_summaries.json()) == 1
    assert set(driver_summaries.json()[0]) == {"authorized_summary", "updated_at"}
    assert hidden_analysis.status_code == 201
    assert summaries_after_hidden.json() == driver_summaries.json()
    assert foreign_evidence.status_code == 404
    assert unrelated_driver_read.status_code == 404
    assert no_evidence.status_code == 422
    assert engineering_list.status_code == 200
    assert len(engineering_list.json()) == 2


def test_openapi_separates_full_analysis_from_authorized_summaries() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/sessions/{session_id}/analyses"]) == {"get", "post"}
    assert set(paths["/api/v1/sessions/{session_id}/analysis-summaries"]) == {"get"}
    assert set(paths["/api/v1/analyses/{analysis_id}"]) == {"get", "patch"}
    assert set(paths["/api/v1/analyses/{analysis_id}/hypotheses"]) == {
        "get",
        "post",
    }
    assert set(paths["/api/v1/hypotheses/{hypothesis_id}"]) == {"get", "patch"}


def _seed_context(engine: Engine) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"analysis-driver-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Analysis Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=Role.DRIVER)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Analysis Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id,
            display_name="Analysis Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Analysis Event {uuid4()}",
            starts_on=date(2026, 11, 18),
        )
        session.add(event)
        session.flush()
        race_session = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 18, 15, tzinfo=UTC),
        )
        session.add(race_session)
        session.flush()
        return SeededContext(
            driver_identity=SeededIdentity(
                user.user_id, membership.membership_id, team.team_id
            ),
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_id=race_session.session_id,
        )


def _seed_identity(engine: Engine, *, team_id: UUID, role: Role) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"analysis-{role.value.lower()}-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(user.user_id, membership.membership_id, team_id)


def _seed_observation(
    engine: Engine,
    context: SeededContext,
    author: SeededIdentity,
) -> UUID:
    with Session(engine) as session, session.begin():
        observation = Observation(
            team_id=context.driver_identity.team_id,
            session_id=context.session_id,
            vehicle_id=context.vehicle_id,
            author_user_id=author.user_id,
            description="Rear instability observed under braking.",
            category="Handling",
            visibility_level=Visibility.ENGINEERING_CONFIDENTIAL,
        )
        session.add(observation)
        session.flush()
        return observation.observation_id


def _seed_session_evidence(
    engine: Engine,
    context: SeededContext,
    author: SeededIdentity,
) -> list[dict[str, str]]:
    with Session(engine) as session, session.begin():
        feedback = DriverFeedback(
            team_id=context.driver_identity.team_id,
            session_id=context.session_id,
            driver_id=context.driver_id,
            author_user_id=context.driver_identity.user_id,
            description="Rear instability under braking.",
            visibility_level=Visibility.ROLE_RESTRICTED,
        )
        lap = Lap(
            team_id=context.driver_identity.team_id,
            session_id=context.session_id,
            lap_number=1,
            duration_us=61_000_000,
        )
        condition = ConditionSnapshot(
            team_id=context.driver_identity.team_id,
            session_id=context.session_id,
            weather="Dry",
        )
        session.add_all([feedback, lap, condition])
        session.flush()
        sector = Sector(
            team_id=context.driver_identity.team_id,
            lap_id=lap.lap_id,
            sector_order=1,
            duration_us=20_000_000,
        )
        observation = Observation(
            team_id=context.driver_identity.team_id,
            session_id=context.session_id,
            vehicle_id=context.vehicle_id,
            author_user_id=author.user_id,
            description="Rear instability observed under braking.",
            category="Handling",
            visibility_level=Visibility.ENGINEERING_CONFIDENTIAL,
        )
        session.add_all([sector, observation])
        session.flush()
        return [
            {
                "evidence_type": "DRIVER_FEEDBACK",
                "reference_id": str(feedback.feedback_id),
            },
            {"evidence_type": "LAP", "reference_id": str(lap.lap_id)},
            {"evidence_type": "SECTOR", "reference_id": str(sector.sector_id)},
            {
                "evidence_type": "CONDITION",
                "reference_id": str(condition.condition_id),
            },
            {
                "evidence_type": "OBSERVATION",
                "reference_id": str(observation.observation_id),
            },
        ]


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
