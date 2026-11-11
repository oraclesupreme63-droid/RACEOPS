"""HTTP contracts for sparse Session Condition Snapshots."""

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
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.main import create_app
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.models import RaceSession

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "condition-api-test-secret-never-used-in-production"
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
    identity: SeededIdentity
    event_id: UUID
    driver_id: UUID
    vehicle_id: UUID


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
async def test_mechanic_creates_reads_and_updates_sparse_conditions(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.MECHANIC)
    session_id = _seed_race_session(database_engine, context)
    headers = _headers(context.identity)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=headers,
            json={
                "ambient_temperature": "24.500",
                "ambient_temperature_unit": " °C ",
                "source": "Manual pit reading",
            },
        )
        read = await client.get(
            f"/api/v1/sessions/{session_id}/conditions", headers=headers
        )
        duplicate = await client.post(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=headers,
            json={"weather": "Dry"},
        )
        invalid_pair = await client.patch(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=headers,
            json={"track_temperature": "31.250"},
        )
        updated = await client.patch(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=headers,
            json={
                "ambient_temperature": None,
                "ambient_temperature_unit": None,
                "weather": "Cloudy",
                "track_condition": "Dry",
            },
        )
        empty = await client.patch(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=headers,
            json={"weather": None, "track_condition": None},
        )

    assert created.status_code == 201
    assert created.json()["ambient_temperature"] == "24.500"
    assert created.json()["ambient_temperature_unit"] == "°C"
    assert created.json()["track_temperature"] is None
    assert read.json() == created.json()
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "condition_snapshot_exists"
    assert invalid_pair.status_code == 422
    assert invalid_pair.json()["code"] == "invalid_condition_snapshot"
    assert updated.status_code == 200
    assert updated.json()["ambient_temperature"] is None
    assert updated.json()["weather"] == "Cloudy"
    assert empty.status_code == 422
    assert empty.json()["code"] == "invalid_condition_snapshot"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_reads_only_assigned_conditions_and_cannot_write(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.DRIVER, link_actor_driver=True)
    own_session_id = _seed_race_session(database_engine, context)
    mechanic = _seed_identity(
        database_engine, team_id=context.identity.team_id, role=Role.MECHANIC
    )
    with Session(database_engine) as session, session.begin():
        other_driver = Driver(
            team_id=context.identity.team_id,
            display_name="Other Driver",
        )
        session.add(other_driver)
        session.flush()
        other_session = RaceSession(
            team_id=context.identity.team_id,
            event_id=context.event_id,
            driver_id=other_driver.driver_id,
            vehicle_id=context.vehicle_id,
            session_type="Qualifying",
            scheduled_at=datetime(2026, 11, 15, 16, tzinfo=UTC),
        )
        session.add(other_session)
        session.flush()
        other_session_id = other_session.session_id

    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for target in (own_session_id, other_session_id):
            response = await client.post(
                f"/api/v1/sessions/{target}/conditions",
                headers=_headers(mechanic),
                json={"weather": "Dry"},
            )
            assert response.status_code == 201
        own_read = await client.get(
            f"/api/v1/sessions/{own_session_id}/conditions",
            headers=_headers(context.identity),
        )
        hidden_read = await client.get(
            f"/api/v1/sessions/{other_session_id}/conditions",
            headers=_headers(context.identity),
        )
        denied_write = await client.patch(
            f"/api/v1/sessions/{own_session_id}/conditions",
            headers=_headers(context.identity),
            json={"weather": "Wet"},
        )

    assert own_read.status_code == 200
    assert hidden_read.status_code == 404
    assert denied_write.status_code == 403


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_condition_requests_reject_missing_units_and_empty_data(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ENGINEER)
    session_id = _seed_race_session(database_engine, context)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        empty = await client.post(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=_headers(context.identity),
            json={},
        )
        missing_unit = await client.post(
            f"/api/v1/sessions/{session_id}/conditions",
            headers=_headers(context.identity),
            json={"ambient_temperature": "23.1"},
        )

    for response in (empty, missing_unit):
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"


def test_openapi_documents_one_snapshot_without_delete() -> None:
    operations = create_app().openapi()["paths"][
        "/api/v1/sessions/{session_id}/conditions"
    ]

    assert set(operations) == {"get", "post", "patch"}
    assert all(item["security"] == [{"HTTPBearer": []}] for item in operations.values())


def _seed_context(
    engine: Engine,
    *,
    role: Role,
    link_actor_driver: bool = False,
) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"conditions-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Conditions Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Conditions Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id if link_actor_driver else None,
            display_name="Conditions Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Conditions Event {uuid4()}",
            starts_on=date(2026, 11, 15),
        )
        session.add(event)
        session.flush()
        return SeededContext(
            identity=SeededIdentity(
                user.user_id, membership.membership_id, team.team_id
            ),
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
        )


def _seed_race_session(engine: Engine, context: SeededContext) -> UUID:
    with Session(engine) as session, session.begin():
        race_session = RaceSession(
            team_id=context.identity.team_id,
            event_id=context.event_id,
            driver_id=context.driver_id,
            vehicle_id=context.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 15, 15, tzinfo=UTC),
        )
        session.add(race_session)
        session.flush()
        return race_session.session_id


def _seed_identity(engine: Engine, *, team_id: UUID, role: Role) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"condition-role-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(user.user_id, membership.membership_id, team_id)


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
