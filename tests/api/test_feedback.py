"""HTTP contracts for own and verbally communicated Driver Feedback."""

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
JWT_SECRET = "feedback-api-test-secret-never-used-in-production"
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
    event_id: UUID
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
async def test_driver_records_lists_and_updates_own_feedback(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    headers = _headers(context.driver_identity)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=headers,
            json={"description": "  Rear instability under braking.  "},
        )
        second = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=headers,
            json={"description": "Front rotation improved", "corner_or_zone": "T7"},
        )
        listed = await client.get(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=headers,
        )
        updated = await client.patch(
            f"/api/v1/feedback/{created.json()['feedback_id']}",
            headers=headers,
            json={"corner_or_zone": " T4 ", "severity": " Medium "},
        )

    assert created.status_code == 201
    assert second.status_code == 201
    body = created.json()
    assert body["session_id"] == str(context.session_id)
    assert body["driver_id"] == str(context.driver_id)
    assert body["author_user_id"] == str(context.driver_identity.user_id)
    assert body["description"] == "Rear instability under braking."
    assert body["visibility_level"] == "ROLE_RESTRICTED"
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert updated.status_code == 200
    assert updated.json()["corner_or_zone"] == "T4"
    assert updated.json()["severity"] == "Medium"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_engineer_records_verbal_feedback_with_separate_author(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.ENGINEER
    )
    manager = _seed_identity(
        database_engine,
        team_id=context.driver_identity.team_id,
        role=Role.TEAM_MANAGER,
    )
    _, other_driver_id = _seed_other_driver_session(database_engine, context)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(engineer),
            json={
                "description": "Rear moves on corner entry",
                "corner_or_zone": "T4",
                "driving_phase": "Entry",
                "confidence": "High",
            },
        )
        feedback_id = created.json()["feedback_id"]
        driver_read = await client.get(
            f"/api/v1/feedback/{feedback_id}",
            headers=_headers(context.driver_identity),
        )
        manager_read = await client.get(
            f"/api/v1/feedback/{feedback_id}", headers=_headers(manager)
        )
        engineer_update = await client.patch(
            f"/api/v1/feedback/{feedback_id}",
            headers=_headers(engineer),
            json={"confidence": "Medium"},
        )
        driver_update = await client.patch(
            f"/api/v1/feedback/{feedback_id}",
            headers=_headers(context.driver_identity),
            json={"confidence": "Low"},
        )
        manager_update = await client.patch(
            f"/api/v1/feedback/{feedback_id}",
            headers=_headers(manager),
            json={"confidence": "Low"},
        )
        reassignment = await client.patch(
            f"/api/v1/sessions/{context.session_id}",
            headers=_headers(manager),
            json={"driver_id": str(other_driver_id)},
        )

    assert created.status_code == 201
    assert created.json()["driver_id"] == str(context.driver_id)
    assert created.json()["author_user_id"] == str(engineer.user_id)
    assert driver_read.status_code == 200
    assert manager_read.status_code == 200
    assert engineer_update.status_code == 200
    assert engineer_update.json()["confidence"] == "Medium"
    assert driver_update.status_code == 404
    assert manager_update.status_code == 403
    assert reassignment.status_code == 409
    assert reassignment.json()["code"] == "session_driver_locked_by_feedback"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_visibility_and_driver_assignment_hide_unrelated_feedback(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.ENGINEER
    )
    mechanic = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.MECHANIC
    )
    administrator = _seed_identity(
        database_engine,
        team_id=context.driver_identity.team_id,
        role=Role.ADMINISTRATOR,
    )
    other_session_id, _ = _seed_other_driver_session(database_engine, context)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(engineer),
            json={"description": "Communicated feedback"},
        )
        feedback_id = created.json()["feedback_id"]
        mechanic_list = await client.get(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(mechanic),
        )
        mechanic_read = await client.get(
            f"/api/v1/feedback/{feedback_id}", headers=_headers(mechanic)
        )
        admin_list = await client.get(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(administrator),
        )
        unrelated_create = await client.post(
            f"/api/v1/sessions/{other_session_id}/feedback",
            headers=_headers(context.driver_identity),
            json={"description": "Should remain hidden"},
        )
        mechanic_created = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(mechanic),
            json={"description": "Driver said the brakes felt long"},
        )
        mechanic_own_read = await client.get(
            f"/api/v1/feedback/{mechanic_created.json()['feedback_id']}",
            headers=_headers(mechanic),
        )

    assert created.status_code == 201
    assert mechanic_list.status_code == 200
    assert mechanic_list.json()["total"] == 0
    assert mechanic_read.status_code == 404
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 0
    assert unrelated_create.status_code == 404
    assert mechanic_created.status_code == 201
    assert mechanic_own_read.status_code == 200


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_feedback_request_rejects_blank_or_client_owned_identity(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        blank = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(context.driver_identity),
            json={"description": "   "},
        )
        forged = await client.post(
            f"/api/v1/sessions/{context.session_id}/feedback",
            headers=_headers(context.driver_identity),
            json={"description": "Valid", "driver_id": str(uuid4())},
        )

    assert blank.status_code == 422
    assert forged.status_code == 422
    assert blank.json()["code"] == "REQUEST_VALIDATION_ERROR"


def test_openapi_documents_feedback_without_delete() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/sessions/{session_id}/feedback"]) == {"get", "post"}
    assert set(paths["/api/v1/feedback/{feedback_id}"]) == {"get", "patch"}


def _seed_context(engine: Engine) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"feedback-driver-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Feedback Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=Role.DRIVER)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Feedback Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id,
            display_name="Feedback Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Feedback Event {uuid4()}",
            starts_on=date(2026, 11, 15),
        )
        session.add(event)
        session.flush()
        race_session = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 15, 15, tzinfo=UTC),
        )
        session.add(race_session)
        session.flush()
        return SeededContext(
            driver_identity=SeededIdentity(
                user.user_id, membership.membership_id, team.team_id
            ),
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_id=race_session.session_id,
        )


def _seed_identity(engine: Engine, *, team_id: UUID, role: Role) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"feedback-{role.value.lower()}-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(user.user_id, membership.membership_id, team_id)


def _seed_other_driver_session(
    engine: Engine, context: SeededContext
) -> tuple[UUID, UUID]:
    with Session(engine) as session, session.begin():
        driver = Driver(
            team_id=context.driver_identity.team_id,
            display_name="Other Driver",
        )
        session.add(driver)
        session.flush()
        race_session = RaceSession(
            team_id=context.driver_identity.team_id,
            event_id=context.event_id,
            driver_id=driver.driver_id,
            vehicle_id=context.vehicle_id,
            session_type="Qualifying",
            scheduled_at=datetime(2026, 11, 15, 16, tzinfo=UTC),
        )
        session.add(race_session)
        session.flush()
        return race_session.session_id, driver.driver_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
