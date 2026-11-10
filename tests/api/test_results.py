"""HTTP contracts for Lap, Sector, metrics, locking, and scoped reads."""

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
from raceops.sessions.models import Lap, RaceSession

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "result-api-test-secret-never-used-in-production"
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
async def test_complete_result_flow_metrics_conflicts_and_locking(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ADMINISTRATOR)
    session_id = _seed_race_session(database_engine, context)
    headers = _headers(context.identity)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.post(
            f"/api/v1/sessions/{session_id}/laps",
            headers=headers,
            json={
                "lap_number": 1,
                "duration_us": 62_000_000,
                "sectors": [
                    {"sector_order": 2, "duration_us": 31_000_000},
                    {"sector_order": 1, "duration_us": 30_000_000},
                ],
            },
        )
        first_lap_id = first.json()["lap_id"]
        sectors = await client.get(
            f"/api/v1/laps/{first_lap_id}/sectors", headers=headers
        )
        first_sector_id = sectors.json()["items"][0]["sector_id"]
        second = await client.post(
            f"/api/v1/sessions/{session_id}/laps",
            headers=headers,
            json={"lap_number": 2, "duration_us": 60_000_000},
        )
        excluded = await client.post(
            f"/api/v1/sessions/{session_id}/laps",
            headers=headers,
            json={
                "lap_number": 3,
                "duration_us": 1,
                "classification": "INVALID",
                "source": "IMPORTED",
            },
        )
        duplicate_lap = await client.post(
            f"/api/v1/sessions/{session_id}/laps",
            headers=headers,
            json={"lap_number": 2, "duration_us": 59_000_000},
        )
        updated = await client.patch(
            f"/api/v1/laps/{first_lap_id}",
            headers=headers,
            json={"duration_us": 61_000_000},
        )
        duplicate_sector = await client.post(
            f"/api/v1/laps/{first_lap_id}/sectors",
            headers=headers,
            json={"sector_order": 1, "duration_us": 29_000_000},
        )
        updated_sector = await client.patch(
            f"/api/v1/sectors/{first_sector_id}",
            headers=headers,
            json={"status": "INVALID"},
        )
        valid_laps = await client.get(
            f"/api/v1/sessions/{session_id}/laps?classification=VALID",
            headers=headers,
        )
        summary = await client.get(
            f"/api/v1/sessions/{session_id}/results-summary", headers=headers
        )
        await client.post(f"/api/v1/sessions/{session_id}/start", headers=headers)
        await client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
        locked = await client.post(
            f"/api/v1/sessions/{session_id}/lock-results", headers=headers
        )
        locked_lap_write = await client.patch(
            f"/api/v1/laps/{first_lap_id}",
            headers=headers,
            json={"duration_us": 63_000_000},
        )
        locked_sector_write = await client.patch(
            f"/api/v1/sectors/{first_sector_id}",
            headers=headers,
            json={"duration_us": 1},
        )

    assert first.status_code == 201
    assert first.json()["source"] == "MANUAL"
    assert first.json()["is_eligible"] is True
    assert [item["sector_order"] for item in sectors.json()["items"]] == [1, 2]
    assert second.status_code == 201
    assert excluded.status_code == 201
    assert excluded.json()["is_eligible"] is False
    assert duplicate_lap.status_code == 409
    assert duplicate_lap.json()["code"] == "lap_number_conflict"
    assert updated.json()["duration_us"] == 61_000_000
    assert duplicate_sector.status_code == 409
    assert duplicate_sector.json()["code"] == "sector_order_conflict"
    assert updated_sector.json()["status"] == "INVALID"
    assert valid_laps.json()["total"] == 2
    assert summary.json() == {
        "session_id": str(session_id),
        "total_laps": 3,
        "eligible_laps": 2,
        "excluded_laps": 1,
        "best_lap_id": second.json()["lap_id"],
        "best_lap_us": 60_000_000,
        "average_lap_us": 60_500_000,
        "consistency_us": 500_000,
    }
    assert locked.json()["results_status"] == "LOCKED"
    for response in (locked_lap_write, locked_sector_write):
        assert response.status_code == 409
        assert response.json()["code"] == "results_locked"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_result_reads_follow_driver_relationship_and_role_permissions(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.DRIVER, link_actor_driver=True)
    own_session_id = _seed_race_session(database_engine, context, with_lap=True)
    mechanic = _seed_identity(
        database_engine, team_id=context.identity.team_id, role=Role.MECHANIC
    )
    with Session(database_engine) as session, session.begin():
        unrelated_driver = Driver(
            team_id=context.identity.team_id,
            display_name="Unrelated Driver",
        )
        session.add(unrelated_driver)
        session.flush()
        unrelated = RaceSession(
            team_id=context.identity.team_id,
            event_id=context.event_id,
            driver_id=unrelated_driver.driver_id,
            vehicle_id=context.vehicle_id,
            session_type="Qualifying",
            scheduled_at=datetime(2026, 11, 15, 16, tzinfo=UTC),
        )
        session.add(unrelated)
        session.flush()
        unrelated_session_id = unrelated.session_id
        session.add(
            Lap(
                team_id=context.identity.team_id,
                session_id=unrelated_session_id,
                lap_number=1,
                duration_us=59_000_000,
            )
        )

    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        driver_read = await client.get(
            f"/api/v1/sessions/{own_session_id}/laps",
            headers=_headers(context.identity),
        )
        driver_hidden = await client.get(
            f"/api/v1/sessions/{unrelated_session_id}/laps",
            headers=_headers(context.identity),
        )
        driver_write = await client.post(
            f"/api/v1/sessions/{own_session_id}/laps",
            headers=_headers(context.identity),
            json={"lap_number": 2, "duration_us": 61_000_000},
        )
        mechanic_read = await client.get(
            f"/api/v1/sessions/{own_session_id}/results-summary",
            headers=_headers(mechanic),
        )
        mechanic_write = await client.post(
            f"/api/v1/sessions/{own_session_id}/laps",
            headers=_headers(mechanic),
            json={"lap_number": 2, "duration_us": 61_000_000},
        )

    assert driver_read.status_code == 200
    assert driver_read.json()["total"] == 1
    assert driver_hidden.status_code == 404
    assert driver_write.status_code == 403
    assert mechanic_read.status_code == 200
    assert mechanic_write.status_code == 403


def test_openapi_documents_results_without_destructive_endpoints() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/sessions/{session_id}/laps"]) == {"get", "post"}
    assert set(paths["/api/v1/laps/{lap_id}"]) == {"get", "patch"}
    assert set(paths["/api/v1/laps/{lap_id}/sectors"]) == {"get", "post"}
    assert set(paths["/api/v1/sectors/{sector_id}"]) == {"get", "patch"}
    assert set(paths["/api/v1/sessions/{session_id}/results-summary"]) == {"get"}


def _seed_context(
    engine: Engine,
    *,
    role: Role,
    link_actor_driver: bool = False,
) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"results-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Results Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Results Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id if link_actor_driver else None,
            display_name="Results Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Results Event {uuid4()}",
            starts_on=date(2026, 11, 15),
        )
        session.add(event)
        session.flush()
        return SeededContext(
            identity=SeededIdentity(
                user_id=user.user_id,
                membership_id=membership.membership_id,
                team_id=team.team_id,
            ),
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
        )


def _seed_race_session(
    engine: Engine,
    context: SeededContext,
    *,
    with_lap: bool = False,
) -> UUID:
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
        if with_lap:
            session.add(
                Lap(
                    team_id=context.identity.team_id,
                    session_id=race_session.session_id,
                    lap_number=1,
                    duration_us=60_000_000,
                )
            )
        return race_session.session_id


def _seed_identity(engine: Engine, *, team_id: UUID, role: Role) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"result-role-{uuid4()}@example.com",
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
