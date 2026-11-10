"""HTTP contracts for Session planning and relationship-scoped access."""

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
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.main import create_app
from raceops.operations.enums import DriverStatus, VehicleStatus
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.enums import SessionStatus
from raceops.sessions.models import RaceSession

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "session-api-test-secret-never-used-in-production"
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
    track_id: UUID
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
async def test_manager_creates_filters_reads_and_edits_planned_session(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(context.identity)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/sessions",
            headers=headers,
            json={
                "event_id": str(context.event_id),
                "driver_id": str(context.driver_id),
                "vehicle_id": str(context.vehicle_id),
                "session_type": "  Practice 1  ",
                "scheduled_at": "2026-11-15T09:30:00-06:00",
            },
        )
        session_id = created.json()["session_id"]
        listed = await client.get(
            f"/api/v1/sessions?event_id={context.event_id}"
            f"&driver_id={context.driver_id}&vehicle_id={context.vehicle_id}"
            "&status=PLANNED&results_status=OPEN",
            headers=headers,
        )
        read = await client.get(f"/api/v1/sessions/{session_id}", headers=headers)
        updated = await client.patch(
            f"/api/v1/sessions/{session_id}",
            headers=headers,
            json={
                "session_type": "Qualifying",
                "scheduled_at": "2026-11-15T17:00:00+00:00",
            },
        )
        deleted = await client.delete(f"/api/v1/sessions/{session_id}", headers=headers)

    body = created.json()
    assert created.status_code == 201
    assert body["session_type"] == "Practice 1"
    assert body["scheduled_at"] == "2026-11-15T15:30:00Z"
    assert body["status"] == "PLANNED"
    assert body["results_status"] == "OPEN"
    assert body["started_at"] is None
    assert body["ended_at"] is None
    assert "team_id" not in body
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert read.status_code == 200
    assert read.json()["session_id"] == session_id
    assert updated.status_code == 200
    assert updated.json()["session_type"] == "Qualifying"
    assert deleted.status_code == 405


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_assignment_validation_is_atomic_and_hides_foreign_resources(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ENGINEER)
    foreign = _seed_context(database_engine, role=Role.TEAM_MANAGER)
    with Session(database_engine) as session, session.begin():
        inactive_driver = Driver(
            team_id=context.identity.team_id,
            display_name="Inactive Driver",
            status=DriverStatus.INACTIVE,
        )
        unavailable_vehicle = Vehicle(
            team_id=context.identity.team_id,
            identifier=f"Unavailable {uuid4()}",
            status=VehicleStatus.MAINTENANCE,
        )
        session.add_all([inactive_driver, unavailable_vehicle])
        foreign_session = _race_session(foreign)
        session.add(foreign_session)
        session.flush()
        inactive_driver_id = inactive_driver.driver_id
        unavailable_vehicle_id = unavailable_vehicle.vehicle_id
        foreign_session_id = foreign_session.session_id

    base_payload = {
        "event_id": str(context.event_id),
        "driver_id": str(context.driver_id),
        "vehicle_id": str(context.vehicle_id),
        "session_type": "Practice",
        "scheduled_at": "2026-11-15T15:00:00Z",
    }
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        inactive = await client.post(
            "/api/v1/sessions",
            headers=_headers(context.identity),
            json={**base_payload, "driver_id": str(inactive_driver_id)},
        )
        unavailable = await client.post(
            "/api/v1/sessions",
            headers=_headers(context.identity),
            json={**base_payload, "vehicle_id": str(unavailable_vehicle_id)},
        )
        foreign_event = await client.post(
            "/api/v1/sessions",
            headers=_headers(context.identity),
            json={**base_payload, "event_id": str(foreign.event_id)},
        )
        hidden_foreign_session = await client.get(
            f"/api/v1/sessions/{foreign_session_id}",
            headers=_headers(context.identity),
        )

    assert inactive.status_code == 409
    assert inactive.json()["code"] == "session_assignment_conflict"
    assert unavailable.status_code == 409
    assert unavailable.json()["code"] == "session_assignment_conflict"
    assert foreign_event.status_code == 404
    assert foreign_event.json()["code"] == "resource_not_found"
    assert hidden_foreign_session.status_code == 404
    assert hidden_foreign_session.json()["code"] == "resource_not_found"
    with Session(database_engine) as session:
        count = session.scalar(
            select(func.count())
            .select_from(RaceSession)
            .where(RaceSession.team_id == context.identity.team_id)
        )
    assert count == 0


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_administrator_writes_and_mechanic_has_read_only_session_access(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ADMINISTRATOR)
    mechanic = _seed_identity_for_team(
        database_engine,
        team_id=context.identity.team_id,
        role=Role.MECHANIC,
    )
    payload = {
        "event_id": str(context.event_id),
        "driver_id": str(context.driver_id),
        "vehicle_id": str(context.vehicle_id),
        "session_type": "Practice",
        "scheduled_at": "2026-11-15T15:00:00Z",
    }
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/sessions",
            headers=_headers(context.identity),
            json=payload,
        )
        session_id = created.json()["session_id"]
        read = await client.get(
            f"/api/v1/sessions/{session_id}", headers=_headers(mechanic)
        )
        write = await client.patch(
            f"/api/v1/sessions/{session_id}",
            headers=_headers(mechanic),
            json={"session_type": "Forbidden edit"},
        )
        command = await client.post(
            f"/api/v1/sessions/{session_id}/start", headers=_headers(mechanic)
        )

    assert created.status_code == 201
    assert read.status_code == 200
    assert write.status_code == 403
    assert write.json()["code"] == "insufficient_permissions"
    assert command.status_code == 403
    assert command.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_reads_only_assigned_session_event_and_vehicle(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.DRIVER, link_actor_driver=True)
    with Session(database_engine) as session, session.begin():
        other_track = Track(
            team_id=context.identity.team_id,
            name=f"Other Track {uuid4()}",
        )
        other_driver = Driver(
            team_id=context.identity.team_id,
            display_name="Other Driver",
        )
        other_vehicle = Vehicle(
            team_id=context.identity.team_id,
            identifier=f"Other Vehicle {uuid4()}",
        )
        session.add_all([other_track, other_driver, other_vehicle])
        session.flush()
        other_event = Event(
            team_id=context.identity.team_id,
            track_id=other_track.track_id,
            name=f"Other Event {uuid4()}",
            starts_on=date(2026, 11, 20),
        )
        session.add(other_event)
        session.flush()
        own_session = _race_session(context)
        other_session = RaceSession(
            team_id=context.identity.team_id,
            event_id=other_event.event_id,
            driver_id=other_driver.driver_id,
            vehicle_id=other_vehicle.vehicle_id,
            session_type="Practice",
            scheduled_at=datetime(2026, 11, 20, 15, tzinfo=UTC),
        )
        session.add_all([own_session, other_session])
        session.flush()
        own_session_id = own_session.session_id
        other_session_id = other_session.session_id
        other_event_id = other_event.event_id
        other_vehicle_id = other_vehicle.vehicle_id

    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        sessions = await client.get("/api/v1/sessions", headers=headers)
        own = await client.get(f"/api/v1/sessions/{own_session_id}", headers=headers)
        hidden_session = await client.get(
            f"/api/v1/sessions/{other_session_id}", headers=headers
        )
        events = await client.get("/api/v1/events", headers=headers)
        hidden_event = await client.get(
            f"/api/v1/events/{other_event_id}", headers=headers
        )
        vehicles = await client.get("/api/v1/vehicles", headers=headers)
        hidden_vehicle = await client.get(
            f"/api/v1/vehicles/{other_vehicle_id}", headers=headers
        )
        write = await client.post(
            "/api/v1/sessions",
            headers=headers,
            json={
                "event_id": str(context.event_id),
                "driver_id": str(context.driver_id),
                "vehicle_id": str(context.vehicle_id),
                "session_type": "Qualifying",
                "scheduled_at": "2026-11-15T18:00:00Z",
            },
        )

    assert sessions.status_code == 200
    assert sessions.json()["total"] == 1
    assert sessions.json()["items"][0]["session_id"] == str(own_session_id)
    assert own.status_code == 200
    assert hidden_session.status_code == 404
    assert events.status_code == 200
    assert events.json()["total"] == 1
    assert events.json()["items"][0]["event_id"] == str(context.event_id)
    assert hidden_event.status_code == 404
    assert vehicles.status_code == 200
    assert vehicles.json()["total"] == 1
    assert vehicles.json()["items"][0]["vehicle_id"] == str(context.vehicle_id)
    assert hidden_vehicle.status_code == 404
    assert write.status_code == 403


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_non_planned_edit_and_event_track_move_are_rejected(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.TEAM_MANAGER)
    with Session(database_engine) as session, session.begin():
        active_session = _race_session(context)
        active_session.status = SessionStatus.ACTIVE
        active_session.started_at = datetime(2026, 11, 15, 15, tzinfo=UTC)
        new_track = Track(
            team_id=context.identity.team_id,
            name=f"New Track {uuid4()}",
        )
        session.add_all([active_session, new_track])
        session.flush()
        active_session_id = active_session.session_id
        new_track_id = new_track.track_id

    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        edit = await client.patch(
            f"/api/v1/sessions/{active_session_id}",
            headers=headers,
            json={"session_type": "Changed"},
        )
        move = await client.patch(
            f"/api/v1/events/{context.event_id}",
            headers=headers,
            json={"track_id": str(new_track_id)},
        )
        metadata = await client.patch(
            f"/api/v1/events/{context.event_id}",
            headers=headers,
            json={"name": "Allowed metadata update"},
        )

    assert edit.status_code == 409
    assert edit.json()["code"] == "session_not_editable"
    assert move.status_code == 409
    assert move.json()["code"] == "event_track_locked"
    assert metadata.status_code == 200
    assert metadata.json()["name"] == "Allowed metadata update"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_session_activity_cycle_preserves_server_timestamps_and_locks_results(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.TEAM_MANAGER)
    with Session(database_engine) as session, session.begin():
        race_session = _race_session(context)
        session.add(race_session)
        session.flush()
        session_id = race_session.session_id

    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        invalid_pause = await client.post(
            f"/api/v1/sessions/{session_id}/pause", headers=headers
        )
        started = await client.post(
            f"/api/v1/sessions/{session_id}/start", headers=headers
        )
        started_at = started.json()["started_at"]
        paused = await client.post(
            f"/api/v1/sessions/{session_id}/pause", headers=headers
        )
        resumed = await client.post(
            f"/api/v1/sessions/{session_id}/resume", headers=headers
        )
        completed = await client.post(
            f"/api/v1/sessions/{session_id}/complete", headers=headers
        )
        invalid_terminal = await client.post(
            f"/api/v1/sessions/{session_id}/start", headers=headers
        )
        locked = await client.post(
            f"/api/v1/sessions/{session_id}/lock-results", headers=headers
        )
        repeated_lock = await client.post(
            f"/api/v1/sessions/{session_id}/lock-results", headers=headers
        )

    assert invalid_pause.status_code == 409
    assert invalid_pause.json()["code"] == "invalid_session_status_transition"
    assert started.status_code == 200
    assert started.json()["status"] == "ACTIVE"
    assert started_at is not None
    assert started.json()["ended_at"] is None
    assert paused.json()["status"] == "PAUSED"
    assert paused.json()["started_at"] == started_at
    assert resumed.json()["status"] == "ACTIVE"
    assert resumed.json()["started_at"] == started_at
    assert completed.json()["status"] == "COMPLETED"
    assert completed.json()["started_at"] == started_at
    assert completed.json()["ended_at"] is not None
    assert invalid_terminal.status_code == 409
    assert invalid_terminal.json()["code"] == "invalid_session_status_transition"
    assert locked.status_code == 200
    assert locked.json()["results_status"] == "LOCKED"
    assert locked.json()["results_locked_by_user_id"] == str(context.identity.user_id)
    assert locked.json()["results_locked_at"] is not None
    assert repeated_lock.status_code == 409
    assert repeated_lock.json()["code"] == "invalid_results_status_transition"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cancel_supports_each_non_terminal_state_and_terminal_lock(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ENGINEER)
    with Session(database_engine) as session, session.begin():
        planned = _race_session(context)
        active = _race_session(context)
        active.scheduled_at = datetime(2026, 11, 15, 16, tzinfo=UTC)
        paused = _race_session(context)
        paused.scheduled_at = datetime(2026, 11, 15, 17, tzinfo=UTC)
        paused_complete = _race_session(context)
        paused_complete.scheduled_at = datetime(2026, 11, 15, 18, tzinfo=UTC)
        session.add_all([planned, active, paused, paused_complete])
        session.flush()
        planned_id = planned.session_id
        active_id = active.session_id
        paused_id = paused.session_id
        paused_complete_id = paused_complete.session_id

    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        premature_lock = await client.post(
            f"/api/v1/sessions/{planned_id}/lock-results", headers=headers
        )
        cancelled_planned = await client.post(
            f"/api/v1/sessions/{planned_id}/cancel", headers=headers
        )
        locked_cancelled = await client.post(
            f"/api/v1/sessions/{planned_id}/lock-results", headers=headers
        )
        await client.post(f"/api/v1/sessions/{active_id}/start", headers=headers)
        cancelled_active = await client.post(
            f"/api/v1/sessions/{active_id}/cancel", headers=headers
        )
        await client.post(f"/api/v1/sessions/{paused_id}/start", headers=headers)
        await client.post(f"/api/v1/sessions/{paused_id}/pause", headers=headers)
        cancelled_paused = await client.post(
            f"/api/v1/sessions/{paused_id}/cancel", headers=headers
        )
        await client.post(
            f"/api/v1/sessions/{paused_complete_id}/start", headers=headers
        )
        await client.post(
            f"/api/v1/sessions/{paused_complete_id}/pause", headers=headers
        )
        completed_paused = await client.post(
            f"/api/v1/sessions/{paused_complete_id}/complete", headers=headers
        )
        repeated_cancel = await client.post(
            f"/api/v1/sessions/{planned_id}/cancel", headers=headers
        )

    assert premature_lock.status_code == 409
    assert premature_lock.json()["code"] == "invalid_results_status_transition"
    assert cancelled_planned.json()["status"] == "CANCELLED"
    assert cancelled_planned.json()["started_at"] is None
    assert cancelled_planned.json()["ended_at"] is not None
    assert locked_cancelled.json()["results_status"] == "LOCKED"
    assert cancelled_active.json()["status"] == "CANCELLED"
    assert cancelled_active.json()["started_at"] is not None
    assert cancelled_paused.json()["status"] == "CANCELLED"
    assert cancelled_paused.json()["started_at"] is not None
    assert completed_paused.json()["status"] == "COMPLETED"
    assert completed_paused.json()["ended_at"] is not None
    assert repeated_cancel.status_code == 409
    assert repeated_cancel.json()["code"] == "invalid_session_status_transition"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_start_revalidates_driver_and_vehicle_without_changing_session(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.ADMINISTRATOR)
    with Session(database_engine) as session, session.begin():
        driver_blocked = _race_session(context)
        second_driver = Driver(
            team_id=context.identity.team_id,
            display_name="Second Driver",
        )
        second_vehicle = Vehicle(
            team_id=context.identity.team_id,
            identifier=f"Second Vehicle {uuid4()}",
        )
        session.add_all([driver_blocked, second_driver, second_vehicle])
        session.flush()
        vehicle_blocked = RaceSession(
            team_id=context.identity.team_id,
            event_id=context.event_id,
            driver_id=second_driver.driver_id,
            vehicle_id=second_vehicle.vehicle_id,
            session_type="Qualifying",
            scheduled_at=datetime(2026, 11, 15, 16, tzinfo=UTC),
        )
        session.add(vehicle_blocked)
        session.flush()
        driver_blocked_id = driver_blocked.session_id
        vehicle_blocked_id = vehicle_blocked.session_id
        driver = session.get(Driver, context.driver_id)
        vehicle = session.get(Vehicle, second_vehicle.vehicle_id)
        assert driver is not None
        assert vehicle is not None
        driver.status = DriverStatus.INACTIVE
        vehicle.status = VehicleStatus.MAINTENANCE

    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        invalid_driver = await client.post(
            f"/api/v1/sessions/{driver_blocked_id}/start", headers=headers
        )
        invalid_vehicle = await client.post(
            f"/api/v1/sessions/{vehicle_blocked_id}/start", headers=headers
        )
        preserved_driver = await client.get(
            f"/api/v1/sessions/{driver_blocked_id}", headers=headers
        )
        preserved_vehicle = await client.get(
            f"/api/v1/sessions/{vehicle_blocked_id}", headers=headers
        )

    assert invalid_driver.status_code == 409
    assert invalid_driver.json()["code"] == "session_assignment_conflict"
    assert invalid_vehicle.status_code == 409
    assert invalid_vehicle.json()["code"] == "session_assignment_conflict"
    assert preserved_driver.json()["status"] == "PLANNED"
    assert preserved_driver.json()["started_at"] is None
    assert preserved_vehicle.json()["status"] == "PLANNED"
    assert preserved_vehicle.json()["started_at"] is None


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_session_payload_rejects_server_fields_naive_time_and_empty_patch(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine, role=Role.TEAM_MANAGER)
    payload = {
        "event_id": str(context.event_id),
        "driver_id": str(context.driver_id),
        "vehicle_id": str(context.vehicle_id),
        "session_type": "Practice",
        "scheduled_at": "2026-11-15T15:00:00Z",
    }
    headers = _headers(context.identity)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        server_field = await client.post(
            "/api/v1/sessions",
            headers=headers,
            json={**payload, "status": "ACTIVE", "team_id": str(uuid4())},
        )
        naive_time = await client.post(
            "/api/v1/sessions",
            headers=headers,
            json={**payload, "scheduled_at": "2026-11-15T15:00:00"},
        )
        created = await client.post("/api/v1/sessions", headers=headers, json=payload)
        empty_patch = await client.patch(
            f"/api/v1/sessions/{created.json()['session_id']}",
            headers=headers,
            json={},
        )
        immutable_event = await client.patch(
            f"/api/v1/sessions/{created.json()['session_id']}",
            headers=headers,
            json={"event_id": str(context.event_id)},
        )

    for response in (server_field, naive_time, empty_patch, immutable_event):
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"


def test_openapi_documents_session_planning_and_lifecycle_contract() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    collection = paths["/api/v1/sessions"]
    item = paths["/api/v1/sessions/{session_id}"]

    assert set(collection) == {"get", "post"}
    assert set(item) == {"get", "patch"}
    assert collection["get"]["security"] == [{"HTTPBearer": []}]
    create_fields = schema["components"]["schemas"]["SessionCreateRequest"][
        "properties"
    ]
    update_fields = schema["components"]["schemas"]["SessionUpdateRequest"][
        "properties"
    ]
    assert "team_id" not in create_fields
    assert "status" not in create_fields
    assert "event_id" not in update_fields
    for command_name in (
        "start",
        "pause",
        "resume",
        "complete",
        "cancel",
        "lock-results",
    ):
        command_path = f"/api/v1/sessions/{{session_id}}/{command_name}"
        assert set(paths[command_path]) == {"post"}
        assert paths[command_path]["post"]["security"] == [{"HTTPBearer": []}]


def _seed_context(
    database_engine: Engine,
    *,
    role: Role,
    link_actor_driver: bool = False,
) -> SeededContext:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"session-api-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Session API Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Session Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id if link_actor_driver else None,
            display_name="Session Driver",
        )
        vehicle = Vehicle(
            team_id=team.team_id,
            identifier=f"Kart {uuid4()}",
        )
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Session Event {uuid4()}",
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
            track_id=track.track_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
        )


def _race_session(context: SeededContext) -> RaceSession:
    return RaceSession(
        team_id=context.identity.team_id,
        event_id=context.event_id,
        driver_id=context.driver_id,
        vehicle_id=context.vehicle_id,
        session_type="Practice",
        scheduled_at=datetime(2026, 11, 15, 15, tzinfo=UTC),
    )


def _seed_identity_for_team(
    database_engine: Engine,
    *,
    team_id: UUID,
    role: Role,
) -> SeededIdentity:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"session-role-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team_id,
        )


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
