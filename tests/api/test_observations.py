"""HTTP contracts for contextual, visibility-scoped Observations."""

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
from sqlalchemy import create_engine, select
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
JWT_SECRET = "observation-api-test-secret-never-used-in-production"
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
async def test_engineer_creates_and_mechanic_updates_honest_observation(
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
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/observations",
            headers=_headers(engineer),
            json={
                "session_id": str(context.session_id),
                "vehicle_id": str(context.vehicle_id),
                "description": "  Vibration observed under braking.  ",
                "category": " Mechanical ",
            },
        )
        observation_id = created.json()["observation_id"]
        read = await client.get(
            f"/api/v1/observations/{observation_id}", headers=_headers(mechanic)
        )
        updated = await client.patch(
            f"/api/v1/observations/{observation_id}",
            headers=_headers(mechanic),
            json={"description": "Vibration reproduced under heavy braking."},
        )

    assert created.status_code == 201
    body = created.json()
    assert body["session_id"] == str(context.session_id)
    assert body["vehicle_id"] == str(context.vehicle_id)
    assert body["author_user_id"] == str(engineer.user_id)
    assert body["description"] == "Vibration observed under braking."
    assert body["category"] == "Mechanical"
    assert body["visibility_level"] == "ROLE_RESTRICTED"
    assert "cause" not in body
    assert "confirmed" not in body
    assert read.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["author_user_id"] == str(engineer.user_id)


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_visibility_filters_before_counting_for_every_role(
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
    mechanic = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.MECHANIC
    )
    administrator = _seed_identity(
        database_engine,
        team_id=context.driver_identity.team_id,
        role=Role.ADMINISTRATOR,
    )
    unrelated_driver = _seed_identity(
        database_engine,
        team_id=context.driver_identity.team_id,
        role=Role.DRIVER,
        create_driver_profile=True,
    )
    _seed_driver_session_with_vehicle(database_engine, unrelated_driver, context)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created: dict[str, str] = {}
        for visibility in (
            "TEAM",
            "ROLE_RESTRICTED",
            "ENGINEERING_CONFIDENTIAL",
        ):
            response = await client.post(
                "/api/v1/observations",
                headers=_headers(engineer),
                json={
                    "session_id": str(context.session_id),
                    "description": f"Evidence {visibility}",
                    "visibility_level": visibility,
                },
            )
            assert response.status_code == 201
            created[visibility] = response.json()["observation_id"]

        totals: dict[str, int] = {}
        for name, identity in {
            "engineer": engineer,
            "manager": manager,
            "mechanic": mechanic,
            "administrator": administrator,
            "driver": context.driver_identity,
            "unrelated_driver": unrelated_driver,
        }.items():
            response = await client.get(
                "/api/v1/observations", headers=_headers(identity)
            )
            assert response.status_code == 200
            totals[name] = response.json()["total"]

        hidden_confidential = await client.get(
            f"/api/v1/observations/{created['ENGINEERING_CONFIDENTIAL']}",
            headers=_headers(mechanic),
        )
        denied_confidential = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={
                "vehicle_id": str(context.vehicle_id),
                "description": "Mechanic confidential attempt",
                "visibility_level": "ENGINEERING_CONFIDENTIAL",
            },
        )
        denied_driver_write = await client.post(
            "/api/v1/observations",
            headers=_headers(context.driver_identity),
            json={
                "session_id": str(context.session_id),
                "description": "Driver cannot create observations",
            },
        )

    assert totals == {
        "engineer": 3,
        "manager": 2,
        "mechanic": 2,
        "administrator": 1,
        "driver": 1,
        "unrelated_driver": 0,
    }
    assert hidden_confidential.status_code == 404
    assert denied_confidential.status_code == 403
    assert denied_driver_write.status_code == 403


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_vehicle_context_filters_and_cross_team_targets_are_enforced(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    foreign_context = _seed_context(database_engine)
    mechanic = _seed_identity(
        database_engine, team_id=context.driver_identity.team_id, role=Role.MECHANIC
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={
                "vehicle_id": str(context.vehicle_id),
                "description": "Left rear play observed",
            },
        )
        filtered = await client.get(
            f"/api/v1/observations?vehicle_id={context.vehicle_id}",
            headers=_headers(mechanic),
        )
        missing_context = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={"description": "Missing context"},
        )
        foreign_target = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={
                "vehicle_id": str(foreign_context.vehicle_id),
                "description": "Foreign target",
            },
        )
        false_cause = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={
                "vehicle_id": str(context.vehicle_id),
                "description": "Evidence only",
                "confirmed_cause": True,
            },
        )
        visibility_change = await client.patch(
            f"/api/v1/observations/{created.json()['observation_id']}",
            headers=_headers(mechanic),
            json={"visibility_level": "TEAM"},
        )

    assert created.status_code == 201
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert missing_context.status_code == 422
    assert foreign_target.status_code == 404
    assert false_cause.status_code == 422
    assert visibility_change.status_code == 422


def test_openapi_documents_observations_without_delete() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/observations"]) == {"get", "post"}
    assert set(paths["/api/v1/observations/{observation_id}"]) == {"get", "patch"}


def _seed_context(engine: Engine) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"observation-driver-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Observation Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=Role.DRIVER)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Observation Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id,
            display_name="Observation Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Observation Event {uuid4()}",
            starts_on=date(2026, 11, 16),
        )
        session.add(event)
        session.flush()
        race_session = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 16, 15, tzinfo=UTC),
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


def _seed_identity(
    engine: Engine,
    *,
    team_id: UUID,
    role: Role,
    create_driver_profile: bool = False,
) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"observation-{role.value.lower()}-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        if create_driver_profile:
            session.add(
                Driver(
                    team_id=team_id,
                    user_id=user.user_id,
                    display_name=f"Unrelated Driver {uuid4()}",
                )
            )
        return SeededIdentity(user.user_id, membership.membership_id, team_id)


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}


def _seed_driver_session_with_vehicle(
    engine: Engine,
    identity: SeededIdentity,
    context: SeededContext,
) -> None:
    with Session(engine) as session, session.begin():
        driver = session.scalar(
            select(Driver).where(
                Driver.team_id == identity.team_id,
                Driver.user_id == identity.user_id,
            )
        )
        assert driver is not None
        session.add(
            RaceSession(
                team_id=identity.team_id,
                event_id=context.event_id,
                driver_id=driver.driver_id,
                vehicle_id=context.vehicle_id,
                session_type="Shared Vehicle Test",
                scheduled_at=datetime(2026, 11, 16, 16, tzinfo=UTC),
            )
        )
