"""HTTP contracts for team-scoped Driver management."""

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
from raceops.operations.enums import DriverStatus
from raceops.operations.models import Driver

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "driver-api-test-secret-never-used-in-production"
PASSWORD = "a valid driver API password"
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
async def test_team_manager_completes_driver_lifecycle(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    linked_user_id = _add_member(database_engine, manager.team_id, Role.DRIVER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/api/v1/drivers",
            headers=headers,
            json={
                "display_name": "  Alex Rivera  ",
                "user_id": str(linked_user_id),
            },
        )
        driver_id = created.json()["driver_id"]
        listed = await client.get(
            "/api/v1/drivers?status=ACTIVE&limit=10&offset=0",
            headers=headers,
        )
        updated = await client.patch(
            f"/api/v1/drivers/{driver_id}",
            headers=headers,
            json={"display_name": "Alex R.", "user_id": None},
        )
        deactivated = await client.post(
            f"/api/v1/drivers/{driver_id}/deactivate",
            headers=headers,
        )
        deactivated_again = await client.post(
            f"/api/v1/drivers/{driver_id}/deactivate",
            headers=headers,
        )
        active_page = await client.get(
            "/api/v1/drivers?status=ACTIVE",
            headers=headers,
        )
        inactive_page = await client.get(
            "/api/v1/drivers?status=INACTIVE",
            headers=headers,
        )
        activated = await client.post(
            f"/api/v1/drivers/{driver_id}/activate",
            headers=headers,
        )
        read = await client.get(f"/api/v1/drivers/{driver_id}", headers=headers)
        delete = await client.delete(f"/api/v1/drivers/{driver_id}", headers=headers)

    created_body = created.json()
    assert created.status_code == 201
    assert created_body["display_name"] == "Alex Rivera"
    assert created_body["user_id"] == str(linked_user_id)
    assert created_body["status"] == "ACTIVE"
    assert "team_id" not in created_body
    assert listed.status_code == 200
    assert listed.json()["items"] == [created_body]
    assert listed.json()["total"] == 1
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Alex R."
    assert updated.json()["user_id"] is None
    assert deactivated.json()["status"] == "INACTIVE"
    assert deactivated_again.json()["status"] == "INACTIVE"
    assert active_page.json()["total"] == 0
    assert inactive_page.json()["total"] == 1
    assert activated.json()["status"] == "ACTIVE"
    assert read.json()["driver_id"] == driver_id
    assert delete.status_code == 405

    with Session(database_engine) as session:
        preserved = session.get_one(Driver, UUID(driver_id))
        assert preserved.status is DriverStatus.ACTIVE


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
@pytest.mark.parametrize("role", [Role.ENGINEER, Role.MECHANIC, Role.DRIVER])
async def test_read_only_roles_cannot_manage_drivers(
    application: FastAPI,
    database_engine: Engine,
    role: Role,
) -> None:
    actor = _seed_identity(database_engine, role=role)
    with Session(database_engine) as session, session.begin():
        visible_driver = Driver(
            team_id=actor.team_id,
            user_id=actor.user_id if role is Role.DRIVER else None,
            display_name="Visible Driver",
        )
        session.add(visible_driver)
    headers = _headers(actor)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post(
            "/api/v1/drivers",
            headers=headers,
            json={"display_name": "Forbidden Driver"},
        )
        listed = await client.get("/api/v1/drivers", headers=headers)

    assert create.status_code == 403
    assert create.json()["code"] == "insufficient_permissions"
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["display_name"] == "Visible Driver"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_reads_only_own_linked_profile(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    actor = _seed_identity(database_engine, role=Role.DRIVER)
    other_user_id = _add_member(database_engine, actor.team_id, Role.DRIVER)
    with Session(database_engine) as session, session.begin():
        own = Driver(
            team_id=actor.team_id,
            user_id=actor.user_id,
            display_name="Own Driver",
        )
        other = Driver(
            team_id=actor.team_id,
            user_id=other_user_id,
            display_name="Other Driver",
        )
        session.add_all([own, other])
        session.flush()
        own_id = own.driver_id
        other_id = other.driver_id

    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/drivers", headers=headers)
        own_read = await client.get(f"/api/v1/drivers/{own_id}", headers=headers)
        other_read = await client.get(f"/api/v1/drivers/{other_id}", headers=headers)
        own_update = await client.patch(
            f"/api/v1/drivers/{own_id}",
            headers=headers,
            json={"display_name": "Unauthorized Change"},
        )

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert [item["driver_id"] for item in listed.json()["items"]] == [str(own_id)]
    assert own_read.status_code == 200
    assert other_read.status_code == 404
    assert other_read.json()["code"] == "resource_not_found"
    assert "Other Driver" not in other_read.text
    assert own_update.status_code == 403


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cross_team_driver_is_hidden_from_management_operations(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    actor = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    other = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    with Session(database_engine) as session, session.begin():
        foreign_driver = Driver(
            team_id=other.team_id,
            display_name="Hidden Foreign Driver",
        )
        session.add(foreign_driver)
        session.flush()
        foreign_driver_id = foreign_driver.driver_id

    headers = _headers(actor)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        listed = await client.get("/api/v1/drivers", headers=headers)
        read = await client.get(f"/api/v1/drivers/{foreign_driver_id}", headers=headers)
        update = await client.patch(
            f"/api/v1/drivers/{foreign_driver_id}",
            headers=headers,
            json={"display_name": "Attempted Leak"},
        )
        deactivate = await client.post(
            f"/api/v1/drivers/{foreign_driver_id}/deactivate",
            headers=headers,
        )

    assert listed.json()["total"] == 0
    for response in (read, update, deactivate):
        assert response.status_code == 404
        assert response.json()["code"] == "resource_not_found"
        assert "Hidden Foreign Driver" not in response.text


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_user_link_conflicts_share_one_safe_response(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    linked_user_id = _add_member(database_engine, manager.team_id, Role.DRIVER)
    inactive_user_id = _add_member(
        database_engine,
        manager.team_id,
        Role.DRIVER,
        status=IdentityStatus.INACTIVE,
    )
    foreign = _seed_identity(database_engine, role=Role.DRIVER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.post(
            "/api/v1/drivers",
            headers=headers,
            json={"display_name": "Linked", "user_id": str(linked_user_id)},
        )
        unlinked = await client.post(
            "/api/v1/drivers",
            headers=headers,
            json={"display_name": "Unlinked"},
        )
        conflicts = [
            await client.post(
                "/api/v1/drivers",
                headers=headers,
                json={"display_name": "Duplicate", "user_id": str(linked_user_id)},
            ),
            await client.post(
                "/api/v1/drivers",
                headers=headers,
                json={"display_name": "Inactive", "user_id": str(inactive_user_id)},
            ),
            await client.post(
                "/api/v1/drivers",
                headers=headers,
                json={"display_name": "Foreign", "user_id": str(foreign.user_id)},
            ),
            await client.patch(
                f"/api/v1/drivers/{unlinked.json()['driver_id']}",
                headers=headers,
                json={"user_id": str(linked_user_id)},
            ),
        ]

    assert first.status_code == 201
    assert unlinked.status_code == 201
    for response in conflicts:
        assert response.status_code == 409
        assert response.json()["code"] == "driver_user_conflict"
        assert response.json()["detail"] == (
            "The requested user cannot be linked to this driver."
        )


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_driver_requests_reject_client_ownership_and_invalid_changes(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manager = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    headers = _headers(manager)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        rejected = [
            await client.post(
                "/api/v1/drivers",
                headers=headers,
                json={"display_name": "Injected", "team_id": str(uuid4())},
            ),
            await client.post(
                "/api/v1/drivers",
                headers=headers,
                json={"display_name": "   "},
            ),
            await client.get("/api/v1/drivers?limit=101", headers=headers),
        ]
        created = await client.post(
            "/api/v1/drivers",
            headers=headers,
            json={"display_name": "Valid Driver"},
        )
        driver_id = created.json()["driver_id"]
        rejected.extend(
            [
                await client.patch(
                    f"/api/v1/drivers/{driver_id}", headers=headers, json={}
                ),
                await client.patch(
                    f"/api/v1/drivers/{driver_id}",
                    headers=headers,
                    json={"display_name": None},
                ),
            ]
        )

    assert created.status_code == 201
    for response in rejected:
        assert response.status_code == 422
        assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"
        assert "Injected" not in response.text


def test_openapi_documents_driver_contract_and_no_delete() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    collection = paths["/api/v1/drivers"]
    item = paths["/api/v1/drivers/{driver_id}"]

    assert set(collection) == {"get", "post"}
    assert set(item) == {"get", "patch"}
    assert "/api/v1/drivers/{driver_id}/activate" in paths
    assert "/api/v1/drivers/{driver_id}/deactivate" in paths
    assert collection["get"]["security"] == [{"HTTPBearer": []}]
    assert collection["post"]["security"] == [{"HTTPBearer": []}]
    assert (
        "team_id"
        not in schema["components"]["schemas"]["DriverCreateRequest"]["properties"]
    )
    assert (
        "team_id" not in schema["components"]["schemas"]["DriverResponse"]["properties"]
    )


def _seed_identity(database_engine: Engine, *, role: Role) -> SeededIdentity:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"driver-api-{uuid4()}@example.com",
            password_hash=hash_password(PASSWORD),
        )
        team = Team(name=f"Driver API Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            membership_id=membership.membership_id,
            team_id=team.team_id,
        )


def _add_member(
    database_engine: Engine,
    team_id: UUID,
    role: Role,
    *,
    status: IdentityStatus = IdentityStatus.ACTIVE,
) -> UUID:
    with Session(database_engine) as session, session.begin():
        user = User(
            email=f"driver-link-{uuid4()}@example.com",
            password_hash="$argon2id$driver-link-placeholder",
            status=status,
        )
        membership = TeamMembership(
            user=user,
            team_id=team_id,
            role=role,
            status=status,
        )
        session.add(membership)
        session.flush()
        return user.user_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
