"""HTTP contracts for team-scoped Vehicle management."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import timedelta
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
from raceops.operations.enums import VehicleStatus
from raceops.operations.models import Vehicle

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "vehicle-api-test-secret-never-used-in-production"
PASSWORD = "a valid vehicle API password"
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
async def test_team_manager_completes_vehicle_lifecycle(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/vehicles",
            headers=headers,
            json={"identifier": "  Kart 27  "},
        )
        vehicle_id = created.json()["vehicle_id"]
        listed = await client.get(
            "/api/v1/vehicles?status=READY&limit=10&offset=0",
            headers=headers,
        )
        updated = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            headers=headers,
            json={"identifier": "Kart 27B"},
        )
        maintenance = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-maintenance",
            headers=headers,
        )
        unavailable = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-unavailable",
            headers=headers,
        )
        ready = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-ready",
            headers=headers,
        )
        retired = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/retire",
            headers=headers,
        )
        invalid_after_retirement = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-ready",
            headers=headers,
        )
        read = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
        delete = await client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=headers)

    created_body = created.json()
    assert created.status_code == 201
    assert created_body["identifier"] == "Kart 27"
    assert created_body["status"] == "READY"
    assert "team_id" not in created_body
    assert listed.status_code == 200
    assert listed.json()["items"] == [created_body]
    assert listed.json()["total"] == 1
    assert updated.json()["identifier"] == "Kart 27B"
    assert maintenance.json()["status"] == "MAINTENANCE"
    assert unavailable.json()["status"] == "UNAVAILABLE"
    assert ready.json()["status"] == "READY"
    assert retired.json()["status"] == "RETIRED"
    assert invalid_after_retirement.status_code == 409
    assert (
        invalid_after_retirement.json()["code"] == "invalid_vehicle_status_transition"
    )
    assert read.json()["status"] == "RETIRED"
    assert delete.status_code == 405

    with Session(database_engine) as session:
        preserved = session.get_one(Vehicle, UUID(vehicle_id))
        assert preserved.status is VehicleStatus.RETIRED


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_same_state_transition_is_rejected_without_modification(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/vehicles",
            headers=headers,
            json={"identifier": "Same State Kart"},
        )
        vehicle_id = created.json()["vehicle_id"]
        invalid = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-ready",
            headers=headers,
        )
        read = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)

    assert invalid.status_code == 409
    assert invalid.json()["code"] == "invalid_vehicle_status_transition"
    assert read.json()["status"] == "READY"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_administrator_can_manage_vehicles(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    administrator = _seed_identity(database_engine, role=Role.ADMINISTRATOR)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/vehicles",
            headers=_headers(administrator),
            json={"identifier": "Administrator Kart"},
        )

    assert created.status_code == 201


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
@pytest.mark.parametrize("role", [Role.ENGINEER, Role.MECHANIC])
async def test_operational_roles_read_but_cannot_manage_vehicles(
    application: FastAPI,
    database_engine: Engine,
    role: Role,
) -> None:
    actor = _seed_identity(database_engine, role=role)
    vehicle_id = _seed_vehicle(database_engine, actor.team_id, f"{role.value} Kart")
    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/vehicles", headers=headers)
        read = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
        create = await client.post(
            "/api/v1/vehicles",
            headers=headers,
            json={"identifier": "Forbidden"},
        )
        update = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            headers=headers,
            json={"identifier": "Forbidden"},
        )
        transition = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/mark-maintenance",
            headers=headers,
        )

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert read.status_code == 200
    for response in (create, update, transition):
        assert response.status_code == 403
        assert response.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_vehicle_access_is_deferred_until_session_relationship_exists(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    driver = _seed_identity(database_engine, role=Role.DRIVER)
    vehicle_id = _seed_vehicle(database_engine, driver.team_id, "Driver Team Kart")
    headers = _headers(driver)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/vehicles", headers=headers)
        read = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
        create = await client.post(
            "/api/v1/vehicles",
            headers=headers,
            json={"identifier": "Forbidden"},
        )

    for response in (listed, read, create):
        assert response.status_code == 403
        assert response.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cross_team_vehicle_is_hidden_from_all_operations(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    actor = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    foreign = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    vehicle_id = _seed_vehicle(database_engine, foreign.team_id, "Hidden Kart")
    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/vehicles", headers=headers)
        read = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
        update = await client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            headers=headers,
            json={"identifier": "Attempted Leak"},
        )
        transition = await client.post(
            f"/api/v1/vehicles/{vehicle_id}/retire",
            headers=headers,
        )

    assert listed.json()["total"] == 0
    for response in (read, update, transition):
        assert response.status_code == 404
        assert response.json()["code"] == "resource_not_found"
        assert "Hidden Kart" not in response.text


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_identifier_is_unique_per_team_but_reusable_across_teams(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    first = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    second = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        initial = await client.post(
            "/api/v1/vehicles",
            headers=_headers(first),
            json={"identifier": "Kart 7"},
        )
        duplicate = await client.post(
            "/api/v1/vehicles",
            headers=_headers(first),
            json={"identifier": "Kart 7"},
        )
        other_team = await client.post(
            "/api/v1/vehicles",
            headers=_headers(second),
            json={"identifier": "Kart 7"},
        )

    assert initial.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "vehicle_identifier_conflict"
    assert other_team.status_code == 201


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_vehicle_requests_reject_client_controlled_and_invalid_fields(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        rejected = [
            await client.post(
                "/api/v1/vehicles",
                headers=headers,
                json={"identifier": "Injected", "team_id": str(uuid4())},
            ),
            await client.post(
                "/api/v1/vehicles",
                headers=headers,
                json={"identifier": "Injected", "status": "RETIRED"},
            ),
            await client.post(
                "/api/v1/vehicles",
                headers=headers,
                json={"identifier": "   "},
            ),
            await client.get("/api/v1/vehicles?limit=101", headers=headers),
        ]
        created = await client.post(
            "/api/v1/vehicles",
            headers=headers,
            json={"identifier": "Valid Kart"},
        )
        rejected.append(
            await client.patch(
                f"/api/v1/vehicles/{created.json()['vehicle_id']}",
                headers=headers,
                json={},
            )
        )

    assert created.status_code == 201
    for response in rejected:
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"
        assert "Injected" not in response.text


def test_openapi_documents_vehicle_contract_and_no_delete() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    collection = paths["/api/v1/vehicles"]
    item = paths["/api/v1/vehicles/{vehicle_id}"]

    assert set(collection) == {"get", "post"}
    assert set(item) == {"get", "patch"}
    for endpoint_command in (
        "mark-ready",
        "mark-maintenance",
        "mark-unavailable",
        "retire",
    ):
        assert f"/api/v1/vehicles/{{vehicle_id}}/{endpoint_command}" in paths
    assert collection["get"]["security"] == [{"HTTPBearer": []}]
    assert collection["post"]["security"] == [{"HTTPBearer": []}]
    create_properties = schema["components"]["schemas"]["VehicleCreateRequest"][
        "properties"
    ]
    response_properties = schema["components"]["schemas"]["VehicleResponse"][
        "properties"
    ]
    assert "team_id" not in create_properties
    assert "status" not in create_properties
    assert "team_id" not in response_properties


def _seed_identity(database_engine: Engine, *, role: Role) -> SeededIdentity:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"vehicle-api-{uuid4()}@example.com",
            password_hash=hash_password(PASSWORD),
        )
        team = Team(name=f"Vehicle API Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team.team_id,
        )


def _seed_vehicle(database_engine: Engine, team_id: UUID, identifier: str) -> UUID:
    with Session(database_engine) as session, session.begin():
        vehicle = Vehicle(team_id=team_id, identifier=identifier)
        session.add(vehicle)
        session.flush()
        return vehicle.vehicle_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
