"""HTTP contracts for same-Team Track catalog and Event planning."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, timedelta
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
from raceops.iam.credentials import hash_password
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.main import create_app
from raceops.operations.enums import EventStatus
from raceops.operations.models import Event, Track

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "track-event-api-test-secret-never-used-in-production"
PASSWORD = "a valid track event API password"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)


@dataclass(frozen=True, slots=True)
class SeededIdentity:
    user_id: UUID
    membership_id: UUID
    team_id: UUID


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
    settings = Settings(
        env="test",
        database_url=base_settings.database_url,
        jwt_secret=SecretStr(JWT_SECRET),
        access_token_ttl_minutes=15,
    )
    app = create_app(settings)
    try:
        yield app
    finally:
        app.state.db_engine.dispose()


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_team_manager_completes_track_and_event_lifecycle(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first_track = await client.post(
            "/api/v1/tracks",
            headers=headers,
            json={"name": "  Autódromo Norte  ", "location": "  Monterrey  "},
        )
        first_track_id = first_track.json()["track_id"]
        second_track = await client.post(
            "/api/v1/tracks",
            headers=headers,
            json={"name": "Kartódromo Sur"},
        )
        second_track_id = second_track.json()["track_id"]
        track_page = await client.get(
            "/api/v1/tracks?limit=10&offset=0",
            headers=headers,
        )
        updated_track = await client.patch(
            f"/api/v1/tracks/{first_track_id}",
            headers=headers,
            json={"name": "Autódromo Norte GP", "location": None},
        )
        created_event = await client.post(
            "/api/v1/events",
            headers=headers,
            json={
                "track_id": first_track_id,
                "name": "  Fecha 1  ",
                "starts_on": "2026-11-15",
                "ends_on": "2026-11-16",
                "description": "  Primera fecha  ",
            },
        )
        event_id = created_event.json()["event_id"]
        updated_event = await client.patch(
            f"/api/v1/events/{event_id}",
            headers=headers,
            json={
                "track_id": second_track_id,
                "name": "Fecha 1 revisada",
                "ends_on": None,
                "description": None,
            },
        )
        filtered = await client.get(
            f"/api/v1/events?status=PLANNED&track_id={second_track_id}",
            headers=headers,
        )
        active = await client.post(
            f"/api/v1/events/{event_id}/activate",
            headers=headers,
        )
        repeated_active = await client.post(
            f"/api/v1/events/{event_id}/activate",
            headers=headers,
        )
        completed = await client.post(
            f"/api/v1/events/{event_id}/complete",
            headers=headers,
        )
        invalid_terminal_change = await client.post(
            f"/api/v1/events/{event_id}/cancel",
            headers=headers,
        )
        read = await client.get(f"/api/v1/events/{event_id}", headers=headers)
        event_delete = await client.delete(
            f"/api/v1/events/{event_id}", headers=headers
        )
        track_delete = await client.delete(
            f"/api/v1/tracks/{first_track_id}", headers=headers
        )

    first_track_body = first_track.json()
    assert first_track.status_code == 201
    assert first_track_body["name"] == "Autódromo Norte"
    assert first_track_body["location"] == "Monterrey"
    assert "team_id" not in first_track_body
    assert track_page.status_code == 200
    assert track_page.json()["total"] == 2
    assert updated_track.json()["name"] == "Autódromo Norte GP"
    assert updated_track.json()["location"] is None

    created_body = created_event.json()
    assert created_event.status_code == 201
    assert created_body["name"] == "Fecha 1"
    assert created_body["description"] == "Primera fecha"
    assert created_body["status"] == "PLANNED"
    assert "team_id" not in created_body
    assert updated_event.json()["track_id"] == second_track_id
    assert updated_event.json()["ends_on"] is None
    assert updated_event.json()["description"] is None
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["event_id"] == event_id
    assert active.json()["status"] == "ACTIVE"
    assert repeated_active.status_code == 409
    assert repeated_active.json()["code"] == "invalid_event_status_transition"
    assert completed.json()["status"] == "COMPLETED"
    assert invalid_terminal_change.status_code == 409
    assert invalid_terminal_change.json()["code"] == ("invalid_event_status_transition")
    assert read.json()["status"] == "COMPLETED"
    assert event_delete.status_code == 405
    assert track_delete.status_code == 405

    with Session(database_engine) as session:
        preserved = session.get_one(Event, UUID(event_id))
        assert preserved.status is EventStatus.COMPLETED
        assert preserved.track_id == UUID(second_track_id)


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
@pytest.mark.parametrize("role", [Role.ADMINISTRATOR, Role.ENGINEER])
async def test_authorized_roles_manage_tracks_and_events(
    application: FastAPI,
    database_engine: Engine,
    role: Role,
) -> None:
    actor = _seed_identity(database_engine, role=role)
    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        track = await client.post(
            "/api/v1/tracks",
            headers=headers,
            json={"name": f"{role.value} Track"},
        )
        event = await client.post(
            "/api/v1/events",
            headers=headers,
            json={
                "track_id": track.json()["track_id"],
                "name": f"{role.value} Event",
                "starts_on": "2026-12-01",
            },
        )
        completed = await client.post(
            f"/api/v1/events/{event.json()['event_id']}/complete",
            headers=headers,
        )

    assert track.status_code == 201
    assert event.status_code == 201
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_mechanic_reads_but_cannot_write_tracks_or_events(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    mechanic = _seed_identity(database_engine, role=Role.MECHANIC)
    track_id, event_id = _seed_track_and_event(database_engine, mechanic.team_id)
    headers = _headers(mechanic)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        track_read = await client.get(f"/api/v1/tracks/{track_id}", headers=headers)
        event_read = await client.get(f"/api/v1/events/{event_id}", headers=headers)
        track_write = await client.patch(
            f"/api/v1/tracks/{track_id}",
            headers=headers,
            json={"name": "Forbidden"},
        )
        event_write = await client.patch(
            f"/api/v1/events/{event_id}",
            headers=headers,
            json={"name": "Forbidden"},
        )
        transition = await client.post(
            f"/api/v1/events/{event_id}/activate",
            headers=headers,
        )

    assert track_read.status_code == 200
    assert event_read.status_code == 200
    for response in (track_write, event_write, transition):
        assert response.status_code == 403
        assert response.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_reads_track_catalog_but_events_require_session_relationship(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    driver = _seed_identity(database_engine, role=Role.DRIVER)
    track_id, event_id = _seed_track_and_event(database_engine, driver.team_id)
    headers = _headers(driver)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        tracks = await client.get("/api/v1/tracks", headers=headers)
        track = await client.get(f"/api/v1/tracks/{track_id}", headers=headers)
        events = await client.get("/api/v1/events", headers=headers)
        event = await client.get(f"/api/v1/events/{event_id}", headers=headers)
        track_write = await client.post(
            "/api/v1/tracks",
            headers=headers,
            json={"name": "Forbidden"},
        )

    assert tracks.status_code == 200
    assert tracks.json()["total"] == 1
    assert track.status_code == 200
    assert events.status_code == 200
    assert events.json()["total"] == 0
    assert event.status_code == 404
    assert event.json()["code"] == "resource_not_found"
    assert track_write.status_code == 403
    assert track_write.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cross_team_tracks_and_events_are_hidden(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    actor = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    foreign = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    foreign_track_id, foreign_event_id = _seed_track_and_event(
        database_engine, foreign.team_id
    )
    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        track_page = await client.get("/api/v1/tracks", headers=headers)
        event_page = await client.get("/api/v1/events", headers=headers)
        track_read = await client.get(
            f"/api/v1/tracks/{foreign_track_id}", headers=headers
        )
        event_read = await client.get(
            f"/api/v1/events/{foreign_event_id}", headers=headers
        )
        track_update = await client.patch(
            f"/api/v1/tracks/{foreign_track_id}",
            headers=headers,
            json={"name": "Attempted Leak"},
        )
        event_update = await client.patch(
            f"/api/v1/events/{foreign_event_id}",
            headers=headers,
            json={"name": "Attempted Leak"},
        )
        event_transition = await client.post(
            f"/api/v1/events/{foreign_event_id}/cancel",
            headers=headers,
        )
        foreign_track_link = await client.post(
            "/api/v1/events",
            headers=headers,
            json={
                "track_id": str(foreign_track_id),
                "name": "Cross Team Event",
                "starts_on": "2026-12-10",
            },
        )

    assert track_page.json()["total"] == 0
    assert event_page.json()["total"] == 0
    for response in (
        track_read,
        event_read,
        track_update,
        event_update,
        event_transition,
        foreign_track_link,
    ):
        assert response.status_code == 404
        assert response.json()["code"] == "resource_not_found"
        assert "Attempted Leak" not in response.text


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_requests_reject_ownership_state_and_invalid_metadata(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    track_id, event_id = _seed_track_and_event(database_engine, manager.team_id)
    headers = _headers(manager)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        rejected = [
            await client.post(
                "/api/v1/tracks",
                headers=headers,
                json={"name": "Injected", "team_id": str(uuid4())},
            ),
            await client.post(
                "/api/v1/tracks",
                headers=headers,
                json={"name": "   "},
            ),
            await client.patch(f"/api/v1/tracks/{track_id}", headers=headers, json={}),
            await client.get("/api/v1/tracks?limit=101", headers=headers),
            await client.post(
                "/api/v1/events",
                headers=headers,
                json={
                    "track_id": str(track_id),
                    "name": "Injected",
                    "starts_on": "2026-12-10",
                    "team_id": str(uuid4()),
                },
            ),
            await client.post(
                "/api/v1/events",
                headers=headers,
                json={
                    "track_id": str(track_id),
                    "name": "Injected",
                    "starts_on": "2026-12-10",
                    "status": "COMPLETED",
                },
            ),
            await client.post(
                "/api/v1/events",
                headers=headers,
                json={
                    "track_id": str(track_id),
                    "name": "Bad Dates",
                    "starts_on": "2026-12-10",
                    "ends_on": "2026-12-09",
                },
            ),
            await client.patch(f"/api/v1/events/{event_id}", headers=headers, json={}),
        ]
        final_range_conflict = await client.patch(
            f"/api/v1/events/{event_id}",
            headers=headers,
            json={"starts_on": "2026-11-03"},
        )
        preserved = await client.get(f"/api/v1/events/{event_id}", headers=headers)

    for response in rejected:
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"
        assert "Injected" not in response.text
    assert final_range_conflict.status_code == 422
    assert final_range_conflict.json()["code"] == "invalid_event_date_range"
    assert preserved.json()["starts_on"] == "2026-11-01"
    assert preserved.json()["ends_on"] == "2026-11-02"


def test_openapi_documents_track_event_contracts_and_no_delete() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    track_collection = paths["/api/v1/tracks"]
    track_item = paths["/api/v1/tracks/{track_id}"]
    event_collection = paths["/api/v1/events"]
    event_item = paths["/api/v1/events/{event_id}"]

    assert set(track_collection) == {"get", "post"}
    assert set(track_item) == {"get", "patch"}
    assert set(event_collection) == {"get", "post"}
    assert set(event_item) == {"get", "patch"}
    for endpoint_command in ("activate", "complete", "cancel"):
        assert f"/api/v1/events/{{event_id}}/{endpoint_command}" in paths
    assert track_collection["get"]["security"] == [{"HTTPBearer": []}]
    assert event_collection["post"]["security"] == [{"HTTPBearer": []}]
    track_create = schema["components"]["schemas"]["TrackCreateRequest"]["properties"]
    event_create = schema["components"]["schemas"]["EventCreateRequest"]["properties"]
    assert "team_id" not in track_create
    assert "team_id" not in event_create
    assert "status" not in event_create


def _seed_identity(database_engine: Engine, *, role: Role) -> SeededIdentity:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"track-event-api-{uuid4()}@example.com",
            password_hash=hash_password(PASSWORD),
        )
        team = Team(name=f"Track Event API Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team.team_id,
        )


def _seed_track_and_event(
    database_engine: Engine,
    team_id: UUID,
) -> tuple[UUID, UUID]:
    with Session(database_engine) as session, session.begin():
        track = Track(team_id=team_id, name=f"Seed Track {uuid4()}")
        session.add(track)
        session.flush()
        event = Event(
            team_id=team_id,
            track_id=track.track_id,
            name=f"Seed Event {uuid4()}",
            starts_on=date(2026, 11, 1),
            ends_on=date(2026, 11, 2),
        )
        session.add(event)
        session.flush()
        return track.track_id, event.event_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
