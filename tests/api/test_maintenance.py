"""HTTP contracts for team-scoped maintenance creation and reading."""

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
from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.main import create_app
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.models import MaintenanceRecord
from raceops.operations.enums import VehicleStatus
from raceops.operations.models import Vehicle

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "maintenance-api-test-secret-never-used-in-production"
PASSWORD = "a valid maintenance API password"
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
async def test_team_manager_creates_filters_and_reads_maintenance(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    vehicle_id = _seed_vehicle(database_engine, manager.team_id, "Manager Kart")
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(vehicle_id),
                "responsible_user_id": str(manager.user_id),
                "maintenance_type": "INSPECTION",
                "description": "  Inspect vibration under braking.  ",
            },
        )
        maintenance_id = created.json()["maintenance_id"]
        listed = await client.get(
            "/api/v1/maintenance-records",
            headers=headers,
            params={
                "vehicle_id": str(vehicle_id),
                "maintenance_type": "INSPECTION",
                "status": "OPEN",
                "limit": 10,
                "offset": 0,
            },
        )
        read = await client.get(
            f"/api/v1/maintenance-records/{maintenance_id}", headers=headers
        )

    body = created.json()
    assert created.status_code == 201
    assert body["vehicle_id"] == str(vehicle_id)
    assert body["responsible_user_id"] == str(manager.user_id)
    assert body["created_by_user_id"] == str(manager.user_id)
    assert body["maintenance_type"] == "INSPECTION"
    assert body["status"] == "OPEN"
    assert body["description"] == "Inspect vibration under braking."
    assert body["session_id"] is None
    assert body["observation_id"] is None
    assert body["action_id"] is None
    assert "team_id" not in body
    assert "visibility_level" not in body
    assert listed.status_code == 200
    assert listed.json()["items"] == [body]
    assert listed.json()["total"] == 1
    assert read.status_code == 200
    assert read.json() == body

    with Session(database_engine) as session:
        record = session.get_one(MaintenanceRecord, UUID(maintenance_id))
        vehicle = session.get_one(Vehicle, vehicle_id)
        assert record.status is MaintenanceStatus.OPEN
        assert vehicle.status is VehicleStatus.READY


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
@pytest.mark.parametrize("role", [Role.ENGINEER, Role.MECHANIC])
async def test_engineer_and_mechanic_can_create_and_read_records(
    application: FastAPI,
    database_engine: Engine,
    role: Role,
) -> None:
    actor = _seed_identity(database_engine, role=role)
    vehicle_id = _seed_vehicle(database_engine, actor.team_id, f"{role.value} Kart")
    headers = _headers(actor)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(vehicle_id),
                "responsible_user_id": str(actor.user_id),
                "maintenance_type": "REPAIR",
                "description": f"{role.value} repair",
            },
        )
        listed = await client.get("/api/v1/maintenance-records", headers=headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_administrator_reads_but_cannot_create_maintenance(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    administrator = _seed_identity(database_engine, role=Role.ADMINISTRATOR)
    vehicle_id = _seed_vehicle(database_engine, administrator.team_id, "Admin Kart")
    maintenance_id = _seed_record(database_engine, administrator, vehicle_id)
    headers = _headers(administrator)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/maintenance-records", headers=headers)
        read = await client.get(
            f"/api/v1/maintenance-records/{maintenance_id}", headers=headers
        )
        create = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(vehicle_id),
                "responsible_user_id": str(administrator.user_id),
                "maintenance_type": "INSPECTION",
                "description": "Forbidden administrator write",
            },
        )

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert read.status_code == 200
    assert create.status_code == 403
    assert create.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_cannot_discover_or_create_maintenance(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    driver = _seed_identity(database_engine, role=Role.DRIVER)
    vehicle_id = _seed_vehicle(database_engine, driver.team_id, "Driver Kart")
    maintenance_id = _seed_record(database_engine, driver, vehicle_id)
    headers = _headers(driver)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/maintenance-records", headers=headers)
        read = await client.get(
            f"/api/v1/maintenance-records/{maintenance_id}", headers=headers
        )
        create = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(vehicle_id),
                "responsible_user_id": str(driver.user_id),
                "maintenance_type": "INSPECTION",
                "description": "Forbidden driver write",
            },
        )

    for response in (listed, read, create):
        assert response.status_code == 403
        assert response.json()["code"] == "insufficient_permissions"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cross_team_resources_are_hidden_and_responsible_is_validated(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    actor = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    foreign = _seed_identity(database_engine, role=Role.MECHANIC)
    inactive = _seed_identity(
        database_engine,
        role=Role.MECHANIC,
        team_id=actor.team_id,
        membership_status=IdentityStatus.INACTIVE,
    )
    inactive_user = _seed_identity(
        database_engine,
        role=Role.MECHANIC,
        team_id=actor.team_id,
        user_status=IdentityStatus.INACTIVE,
    )
    own_vehicle_id = _seed_vehicle(database_engine, actor.team_id, "Own Kart")
    foreign_vehicle_id = _seed_vehicle(database_engine, foreign.team_id, "Foreign Kart")
    foreign_record_id = _seed_record(database_engine, foreign, foreign_vehicle_id)
    headers = _headers(actor)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        foreign_vehicle = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(foreign_vehicle_id),
                "responsible_user_id": str(actor.user_id),
                "maintenance_type": "REPAIR",
                "description": "Must not reveal foreign vehicle",
            },
        )
        foreign_responsible = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(own_vehicle_id),
                "responsible_user_id": str(foreign.user_id),
                "maintenance_type": "REPAIR",
                "description": "Must reject foreign responsible",
            },
        )
        inactive_responsible = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(own_vehicle_id),
                "responsible_user_id": str(inactive.user_id),
                "maintenance_type": "REPAIR",
                "description": "Must reject inactive responsible",
            },
        )
        inactive_user_responsible = await client.post(
            "/api/v1/maintenance-records",
            headers=headers,
            json={
                "vehicle_id": str(own_vehicle_id),
                "responsible_user_id": str(inactive_user.user_id),
                "maintenance_type": "REPAIR",
                "description": "Must reject inactive user",
            },
        )
        hidden = await client.get(
            f"/api/v1/maintenance-records/{foreign_record_id}", headers=headers
        )
        listed = await client.get("/api/v1/maintenance-records", headers=headers)

    assert foreign_vehicle.status_code == 404
    assert foreign_vehicle.json()["code"] == "resource_not_found"
    for response in (
        foreign_responsible,
        inactive_responsible,
        inactive_user_responsible,
    ):
        assert response.status_code == 409
        assert response.json()["code"] == "maintenance_responsible_conflict"
    assert hidden.status_code == 404
    assert hidden.json()["code"] == "resource_not_found"
    assert listed.json()["total"] == 0


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_maintenance_requests_reject_client_controlled_fields(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    vehicle_id = _seed_vehicle(database_engine, manager.team_id, "Validation Kart")
    base_payload = {
        "vehicle_id": str(vehicle_id),
        "responsible_user_id": str(manager.user_id),
        "maintenance_type": "INSPECTION",
        "description": "Valid description",
    }
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        rejected = []
        for forbidden in ("team_id", "status", "session_id", "visibility_level"):
            rejected.append(
                await client.post(
                    "/api/v1/maintenance-records",
                    headers=headers,
                    json={**base_payload, forbidden: str(uuid4())},
                )
            )
        rejected.extend(
            [
                await client.post(
                    "/api/v1/maintenance-records",
                    headers=headers,
                    json={**base_payload, "description": "   "},
                ),
                await client.post(
                    "/api/v1/maintenance-records",
                    headers=headers,
                    json={**base_payload, "maintenance_type": "OIL_CHANGE"},
                ),
                await client.get(
                    "/api/v1/maintenance-records?limit=101", headers=headers
                ),
            ]
        )

    for response in rejected:
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"


def test_openapi_documents_minimal_maintenance_contract() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    collection = paths["/api/v1/maintenance-records"]
    item = paths["/api/v1/maintenance-records/{maintenance_id}"]

    assert set(collection) == {"get", "post"}
    assert set(item) == {"get"}
    assert collection["get"]["security"] == [{"HTTPBearer": []}]
    assert collection["post"]["security"] == [{"HTTPBearer": []}]
    create_properties = schema["components"]["schemas"]["MaintenanceCreateRequest"][
        "properties"
    ]
    response_properties = schema["components"]["schemas"]["MaintenanceResponse"][
        "properties"
    ]
    assert set(create_properties) == {
        "vehicle_id",
        "responsible_user_id",
        "maintenance_type",
        "description",
    }
    assert "team_id" not in response_properties
    assert "visibility_level" not in response_properties


def _seed_identity(
    database_engine: Engine,
    *,
    role: Role,
    team_id: UUID | None = None,
    membership_status: IdentityStatus = IdentityStatus.ACTIVE,
    user_status: IdentityStatus = IdentityStatus.ACTIVE,
) -> SeededIdentity:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"maintenance-api-{uuid4()}@example.com",
            password_hash=hash_password(PASSWORD),
            status=user_status,
        )
        if team_id is None:
            team = Team(name=f"Maintenance API Team {uuid4()}")
        else:
            team = session.get_one(Team, team_id)
        membership = TeamMembership(
            user=user,
            team=team,
            role=role,
            status=membership_status,
        )
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team.team_id,
        )


def _seed_vehicle(database_engine: Engine, team_id: UUID, identifier: str) -> UUID:
    with Session(database_engine) as session, session.begin():
        vehicle = Vehicle(team_id=team_id, identifier=f"{identifier} {uuid4()}")
        session.add(vehicle)
        session.flush()
        return vehicle.vehicle_id


def _seed_record(
    database_engine: Engine,
    identity: SeededIdentity,
    vehicle_id: UUID,
) -> UUID:
    with Session(database_engine) as session, session.begin():
        record = MaintenanceRecord(
            team_id=identity.team_id,
            vehicle_id=vehicle_id,
            responsible_user_id=identity.user_id,
            created_by_user_id=identity.user_id,
            maintenance_type=MaintenanceType.INSPECTION,
            description="Seeded maintenance record.",
        )
        session.add(record)
        session.flush()
        return record.maintenance_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
