"""HTTP contracts for login and current identity."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import jwt
import pytest
from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from raceops.api.dependencies import require_permission
from raceops.core.config import Settings
from raceops.iam.authorization import (
    Permission,
    enforce_team_scope,
)
from raceops.iam.credentials import hash_password
from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import JWT_ALGORITHM, issue_access_token
from raceops.main import create_app

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "identity-api-test-secret-never-used-in-production"
PASSWORD = "a valid test password"
requires_database = pytest.mark.skipif(
    not RUN_DATABASE_TESTS,
    reason="set RACEOPS_RUN_DB_TESTS=1 with PostgreSQL available",
)


@dataclass(frozen=True, slots=True)
class SeededIdentity:
    user_id: UUID
    email: str
    membership_id: UUID
    team_id: UUID
    team_name: str


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
async def test_login_and_me_complete_single_membership_flow(
    application: FastAPI,
    database_engine: Engine,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seeded = _seed_identity(database_engine, role=Role.ENGINEER)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": seeded.email.upper(), "password": PASSWORD},
        )
        token = login_response.json()["access_token"]
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    output = capsys.readouterr().out
    assert login_response.status_code == 200
    assert login_response.json() == {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900,
    }
    assert set(payload) == {"sub", "mid", "jti", "iat", "exp"}
    assert seeded.email not in payload.values()
    assert token not in output
    assert PASSWORD not in output
    assert me_response.status_code == 200
    assert me_response.json() == {
        "user": {
            "user_id": str(seeded.user_id),
            "email": seeded.email,
            "status": "ACTIVE",
        },
        "team": {
            "team_id": str(seeded.team_id),
            "name": seeded.team_name,
            "status": "ACTIVE",
        },
        "membership": {
            "membership_id": str(seeded.membership_id),
            "role": "ENGINEER",
            "status": "ACTIVE",
        },
    }
    assert "password" not in me_response.text
    assert "jti" not in me_response.text


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_valid_credentials_require_and_accept_team_selection(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    seeded = _seed_identity(database_engine, role=Role.DRIVER)
    second = _add_team_membership(
        database_engine,
        user_id=seeded.user_id,
        role=Role.MECHANIC,
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        context_response = await client.post(
            "/api/v1/auth/login",
            json={"email": seeded.email, "password": PASSWORD},
        )
        selected_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": seeded.email,
                "password": PASSWORD,
                "team_id": str(second.team_id),
            },
        )
        selected_token = selected_response.json()["access_token"]
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {selected_token}"},
        )

    assert context_response.status_code == 409
    context_body = context_response.json()
    assert context_body["code"] == "team_context_required"
    assert {team["team_id"]: team["name"] for team in context_body["teams"]} == {
        str(seeded.team_id): seeded.team_name,
        str(second.team_id): second.team_name,
    }
    assert all("role" not in team for team in context_body["teams"])
    assert selected_response.status_code == 200
    assert me_response.json()["team"]["team_id"] == str(second.team_id)
    assert me_response.json()["membership"]["role"] == "MECHANIC"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
@pytest.mark.parametrize(
    "rejection",
    [
        "unknown_email",
        "wrong_password",
        "inactive_user",
        "inactive_membership",
        "inactive_team",
        "invalid_team_context",
    ],
)
async def test_login_rejections_share_one_public_problem(
    application: FastAPI,
    database_engine: Engine,
    rejection: str,
) -> None:
    seeded = _seed_identity(database_engine, role=Role.DRIVER)
    email = seeded.email
    password = PASSWORD
    team_id: str | None = None

    if rejection == "unknown_email":
        email = f"unknown-{uuid4()}@example.com"
    elif rejection == "wrong_password":
        password = "a different test password"
    elif rejection == "invalid_team_context":
        team_id = str(uuid4())
    else:
        _deactivate(database_engine, seeded, rejection)

    request_body = {"email": email, "password": password}
    if team_id is not None:
        request_body["team_id"] = team_id
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/v1/auth/login", json=request_body)

    body = response.json()
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert body["title"] == "Invalid credentials"
    assert body["code"] == "invalid_credentials"
    assert body["detail"] == "The supplied credentials or team context are invalid."
    assert email not in response.text
    assert password not in response.text


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_me_rejects_missing_tampered_expired_and_inactive_identity(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    seeded = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    valid_token = issue_access_token(
        user_id=seeded.user_id,
        membership_id=seeded.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    expired_token = issue_access_token(
        user_id=seeded.user_id,
        membership_id=seeded.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=1),
        now=datetime.now(UTC) - timedelta(minutes=2),
    )
    tampered_token = f"{valid_token[:-1]}{'a' if valid_token[-1] != 'a' else 'b'}"
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        responses = [
            await client.get("/api/v1/auth/me"),
            await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {tampered_token}"},
            ),
            await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {expired_token}"},
            ),
        ]
        _deactivate(database_engine, seeded, "inactive_membership")
        responses.append(
            await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {valid_token}"},
            )
        )

    for response in responses:
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.json()["code"] == "invalid_access_token"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_me_reads_role_change_without_reissuing_token(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    seeded = _seed_identity(database_engine, role=Role.DRIVER)
    token = issue_access_token(
        user_id=seeded.user_id,
        membership_id=seeded.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        with Session(database_engine) as session:
            membership = session.get_one(TeamMembership, seeded.membership_id)
            membership.role = Role.ENGINEER
            session.commit()
        second = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert first.json()["membership"]["role"] == "DRIVER"
    assert second.json()["membership"]["role"] == "ENGINEER"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_rbac_dependency_applies_least_privilege_to_every_role(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    manage_members = require_permission(Permission.MANAGE_MEMBERS)
    read_team_configuration = require_permission(Permission.READ_TEAM_CONFIGURATION)

    @application.get("/api/v1/testing/manage-members")
    def manage_members_probe(
        actor: Annotated[CurrentIdentity, Depends(manage_members)],
    ) -> dict[str, str]:
        return {"role": actor.role}

    @application.get("/api/v1/testing/team-configuration")
    def team_configuration_probe(
        actor: Annotated[CurrentIdentity, Depends(read_team_configuration)],
    ) -> dict[str, str]:
        return {"role": actor.role}

    seeded_by_role = {role: _seed_identity(database_engine, role=role) for role in Role}
    tokens = {
        role: issue_access_token(
            user_id=seeded.user_id,
            membership_id=seeded.membership_id,
            secret=JWT_SECRET,
            ttl=timedelta(minutes=15),
        )
        for role, seeded in seeded_by_role.items()
    }
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for role, token in tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            manage_response = await client.get(
                "/api/v1/testing/manage-members",
                headers=headers,
            )
            configuration_response = await client.get(
                "/api/v1/testing/team-configuration",
                headers=headers,
            )

            expected_manage_status = 200 if role is Role.ADMINISTRATOR else 403
            assert manage_response.status_code == expected_manage_status
            if expected_manage_status == 403:
                assert manage_response.json()["code"] == "insufficient_permissions"
            assert configuration_response.status_code == 200

        driver = seeded_by_role[Role.DRIVER]
        with Session(database_engine) as session:
            membership = session.get_one(TeamMembership, driver.membership_id)
            membership.role = Role.ADMINISTRATOR
            session.commit()
        changed_role_response = await client.get(
            "/api/v1/testing/manage-members",
            headers={"Authorization": f"Bearer {tokens[Role.DRIVER]}"},
        )

    assert changed_role_response.status_code == 200
    assert changed_role_response.json()["role"] == "ADMINISTRATOR"


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_cross_team_resource_is_hidden_with_not_found(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    read_team_configuration = require_permission(Permission.READ_TEAM_CONFIGURATION)

    @application.get("/api/v1/testing/team-resources/{resource_team_id}")
    def team_resource_probe(
        resource_team_id: UUID,
        actor: Annotated[CurrentIdentity, Depends(read_team_configuration)],
    ) -> dict[str, str]:
        enforce_team_scope(actor, resource_team_id)
        return {"team_id": str(resource_team_id)}

    actor = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    other = _seed_identity(database_engine, role=Role.TEAM_MANAGER)
    token = issue_access_token(
        user_id=actor.user_id,
        membership_id=actor.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        own_response = await client.get(
            f"/api/v1/testing/team-resources/{actor.team_id}",
            headers=headers,
        )
        cross_team_response = await client.get(
            f"/api/v1/testing/team-resources/{other.team_id}",
            headers=headers,
        )

    assert own_response.status_code == 200
    assert cross_team_response.status_code == 404
    assert cross_team_response.headers["content-type"] == "application/problem+json"
    assert cross_team_response.json()["code"] == "resource_not_found"
    assert other.team_name not in cross_team_response.text


def test_openapi_documents_identity_contract_without_hashes() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]
    serialized_schema = str(schema).lower()

    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/me" in paths
    assert paths["/api/v1/auth/me"]["get"]["security"] == [{"HTTPBearer": []}]
    assert "teamcontextproblemdetails" in serialized_schema
    assert "password_hash" not in serialized_schema


@pytest.mark.anyio
async def test_login_validation_does_not_echo_rejected_password() -> None:
    application = create_app()
    rejected_password = "private-" * 20
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "driver@example.com",
                "password": rejected_password,
            },
        )

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "REQUEST_VALIDATION_ERROR"
    assert rejected_password not in response.text


def _seed_identity(database_engine: Engine, *, role: Role) -> SeededIdentity:
    unique = uuid4()
    email = f"api-user-{unique}@example.com"
    team_name = f"API Team {unique}"
    with Session(database_engine) as session, session.begin():
        user = User(email=email, password_hash=hash_password(PASSWORD))
        team = Team(name=team_name)
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            email=email,
            membership_id=membership.membership_id,
            team_id=team.team_id,
            team_name=team_name,
        )


def _add_team_membership(
    database_engine: Engine,
    *,
    user_id: UUID,
    role: Role,
) -> SeededIdentity:
    unique = uuid4()
    team_name = f"Additional API Team {unique}"
    with Session(database_engine) as session, session.begin():
        user = session.get_one(User, user_id)
        team = Team(name=team_name)
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(
            user_id=user.user_id,
            email=user.email,
            membership_id=membership.membership_id,
            team_id=team.team_id,
            team_name=team_name,
        )


def _deactivate(
    database_engine: Engine,
    seeded: SeededIdentity,
    rejection: str,
) -> None:
    with Session(database_engine) as session:
        if rejection == "inactive_user":
            session.get_one(User, seeded.user_id).status = IdentityStatus.INACTIVE
        elif rejection == "inactive_membership":
            session.get_one(
                TeamMembership,
                seeded.membership_id,
            ).status = IdentityStatus.INACTIVE
        elif rejection == "inactive_team":
            session.get_one(Team, seeded.team_id).status = IdentityStatus.INACTIVE
        else:
            raise ValueError(f"unsupported rejection: {rejection}")
        session.commit()
