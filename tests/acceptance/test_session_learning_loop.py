"""Acceptance proof for the complete v0.4 Session Learning Loop."""

import json
import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from raceops.core.config import Settings
from raceops.iam.enums import Role
from raceops.iam.models import Team, TeamMembership, User
from raceops.iam.tokens import issue_access_token
from raceops.main import create_app

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "acceptance-test-secret-never-used-in-production"
DATASET_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "session_learning_loop_v0.4.json"
)
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
async def test_complete_session_learning_loop_and_role_projections(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    """Execute the product thesis through HTTP with synthetic evidence."""
    data = _load_dataset()
    identities = _seed_team_roles(database_engine)
    manager = identities[Role.TEAM_MANAGER]
    engineer = identities[Role.ENGINEER]
    mechanic = identities[Role.MECHANIC]
    driver_identity = identities[Role.DRIVER]
    administrator = identities[Role.ADMINISTRATOR]
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        track = await client.post(
            "/api/v1/tracks", headers=_headers(manager), json=data["track"]
        )
        _expect(track, 201, "create Track")
        event_payload = {**data["event"], "track_id": track.json()["track_id"]}
        event = await client.post(
            "/api/v1/events", headers=_headers(manager), json=event_payload
        )
        _expect(event, 201, "create Event")
        driver_payload = {
            **data["driver"],
            "user_id": str(driver_identity.user_id),
        }
        driver = await client.post(
            "/api/v1/drivers", headers=_headers(manager), json=driver_payload
        )
        _expect(driver, 201, "create Driver")
        vehicle = await client.post(
            "/api/v1/vehicles", headers=_headers(manager), json=data["vehicle"]
        )
        _expect(vehicle, 201, "create Vehicle")

        shared_assignment = {
            "event_id": event.json()["event_id"],
            "driver_id": driver.json()["driver_id"],
            "vehicle_id": vehicle.json()["vehicle_id"],
        }
        source = await client.post(
            "/api/v1/sessions",
            headers=_headers(engineer),
            json={**shared_assignment, **data["source_session"]},
        )
        evaluation = await client.post(
            "/api/v1/sessions",
            headers=_headers(engineer),
            json={**shared_assignment, **data["evaluation_session"]},
        )
        _expect(source, 201, "create source Session")
        _expect(evaluation, 201, "create evaluation Session")
        source_id = source.json()["session_id"]
        evaluation_id = evaluation.json()["session_id"]

        source_condition = await client.post(
            f"/api/v1/sessions/{source_id}/conditions",
            headers=_headers(engineer),
            json=data["source_conditions"],
        )
        _expect(source_condition, 201, "record source Conditions")
        _expect(
            await client.post(
                f"/api/v1/sessions/{source_id}/start", headers=_headers(engineer)
            ),
            200,
            "start source Session",
        )
        source_lap_ids = await _create_laps(
            client,
            source_id,
            cast(list[dict[str, Any]], data["source_laps"]),
            engineer,
        )
        source_feedback = await client.post(
            f"/api/v1/sessions/{source_id}/feedback",
            headers=_headers(driver_identity),
            json=data["source_feedback"],
        )
        _expect(source_feedback, 201, "record source Driver Feedback")
        observation = await client.post(
            "/api/v1/observations",
            headers=_headers(mechanic),
            json={
                **data["observation"],
                "session_id": source_id,
                "vehicle_id": vehicle.json()["vehicle_id"],
            },
        )
        _expect(observation, 201, "record Observation")
        _expect(
            await client.post(
                f"/api/v1/sessions/{source_id}/complete",
                headers=_headers(engineer),
            ),
            200,
            "complete source Session",
        )
        _expect(
            await client.post(
                f"/api/v1/sessions/{source_id}/lock-results",
                headers=_headers(engineer),
            ),
            200,
            "lock source results",
        )
        source_summary = await client.get(
            f"/api/v1/sessions/{source_id}/results-summary",
            headers=_headers(engineer),
        )
        _expect(source_summary, 200, "read source metrics")

        analysis = await client.post(
            f"/api/v1/sessions/{source_id}/analyses",
            headers=_headers(engineer),
            json={
                **data["analysis"],
                "evidence": [
                    {
                        "evidence_type": "DRIVER_FEEDBACK",
                        "reference_id": source_feedback.json()["feedback_id"],
                    },
                    {
                        "evidence_type": "LAP",
                        "reference_id": source_lap_ids[1],
                    },
                    {
                        "evidence_type": "OBSERVATION",
                        "reference_id": observation.json()["observation_id"],
                    },
                ],
            },
        )
        _expect(analysis, 201, "create Session Analysis")
        hypothesis = await client.post(
            f"/api/v1/analyses/{analysis.json()['analysis_id']}/hypotheses",
            headers=_headers(engineer),
            json=data["hypothesis"],
        )
        _expect(hypothesis, 201, "create Hypothesis")
        priority = await client.post(
            f"/api/v1/sessions/{source_id}/priorities",
            headers=_headers(engineer),
            json={
                **data["priority"],
                "recipient_user_id": str(driver_identity.user_id),
                "hypothesis_id": hypothesis.json()["hypothesis_id"],
            },
        )
        _expect(priority, 201, "create Priority")
        action = await client.post(
            f"/api/v1/sessions/{source_id}/actions",
            headers=_headers(engineer),
            json={
                **data["action"],
                "assignee_user_id": str(driver_identity.user_id),
                "hypothesis_id": hypothesis.json()["hypothesis_id"],
                "priority_id": priority.json()["priority_id"],
            },
        )
        _expect(action, 201, "create Action")
        action_id = action.json()["action_id"]
        assert action.json()["target_intent"] == "NEXT_SESSION"
        assert action.json()["evaluation_status"] == "NOT_EVALUATED"
        for transition in ("plan", "start", "complete"):
            _expect(
                await client.post(
                    f"/api/v1/actions/{action_id}/{transition}",
                    headers=_headers(driver_identity),
                ),
                200,
                f"{transition} assigned Action",
            )

        evaluation_condition = await client.post(
            f"/api/v1/sessions/{evaluation_id}/conditions",
            headers=_headers(mechanic),
            json=data["evaluation_conditions"],
        )
        _expect(evaluation_condition, 201, "record evaluation Conditions")
        _expect(
            await client.post(
                f"/api/v1/sessions/{evaluation_id}/start",
                headers=_headers(engineer),
            ),
            200,
            "start evaluation Session",
        )
        await _create_laps(
            client,
            evaluation_id,
            cast(list[dict[str, Any]], data["evaluation_laps"]),
            engineer,
        )
        evaluation_feedback = await client.post(
            f"/api/v1/sessions/{evaluation_id}/feedback",
            headers=_headers(driver_identity),
            json=data["evaluation_feedback"],
        )
        _expect(evaluation_feedback, 201, "record evaluation Driver Feedback")
        _expect(
            await client.post(
                f"/api/v1/sessions/{evaluation_id}/complete",
                headers=_headers(engineer),
            ),
            200,
            "complete evaluation Session",
        )
        _expect(
            await client.post(
                f"/api/v1/sessions/{evaluation_id}/lock-results",
                headers=_headers(engineer),
            ),
            200,
            "lock evaluation results",
        )
        evaluation_summary = await client.get(
            f"/api/v1/sessions/{evaluation_id}/results-summary",
            headers=_headers(engineer),
        )
        _expect(evaluation_summary, 200, "read evaluation metrics")
        assert (
            evaluation_summary.json()["best_lap_us"]
            < (source_summary.json()["best_lap_us"])
        )

        outcome = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(engineer),
            json={**data["outcome"], "evaluation_session_id": evaluation_id},
        )
        _expect(outcome, 201, "record Action Outcome")
        assert outcome.json()["classification"] == "IMPROVED"

        engineer_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(engineer),
        )
        driver_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(driver_identity),
        )
        manager_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(manager),
        )
        mechanic_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(mechanic),
        )
        administrator_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(administrator),
        )
        driver_summaries = await client.get(
            f"/api/v1/sessions/{source_id}/analysis-summaries",
            headers=_headers(driver_identity),
        )

    _expect(engineer_chain, 200, "read Engineering learning chain")
    engineer_body = engineer_chain.json()
    assert (
        engineer_body["analysis"]["technical_detail"]
        == (data["analysis"]["technical_detail"])
    )
    assert len(engineer_body["analysis"]["evidence"]) == 3
    assert engineer_body["hypothesis"]["status"] == "PARTIALLY_SUPPORTED"
    assert engineer_body["priority"]["target_session_id"] == evaluation_id
    assert engineer_body["action"]["target_session_id"] == evaluation_id
    assert engineer_body["evaluation"]["evaluation_status"] == "IMPROVED"
    assert "confidential_conclusion" in engineer_body["evaluation"]["outcome"]

    _expect(driver_chain, 200, "read Driver learning chain")
    driver_body = driver_chain.json()
    assert "analysis" not in driver_body
    assert "hypothesis" not in driver_body
    assert "confidential_detail" not in driver_body["action"]
    assert "confidential_conclusion" not in driver_body["evaluation"]["outcome"]
    assert driver_body["evaluation"]["outcome"]["public_conclusion"]

    _expect(manager_chain, 200, "read Team Manager learning chain")
    manager_body = manager_chain.json()
    assert "analysis" not in manager_body
    assert "hypothesis" not in manager_body
    assert "confidential_detail" not in manager_body["action"]
    assert "confidential_conclusion" not in manager_body["evaluation"]["outcome"]
    assert mechanic_chain.status_code == 404
    assert administrator_chain.status_code == 404
    _expect(driver_summaries, 200, "read Driver authorized Analysis summary")
    assert (
        driver_summaries.json()[0]["authorized_summary"]
        == (data["analysis"]["authorized_summary"])
    )


async def _create_laps(
    client: AsyncClient,
    session_id: str,
    laps: list[dict[str, Any]],
    actor: SeededIdentity,
) -> list[str]:
    lap_ids: list[str] = []
    for lap in laps:
        response = await client.post(
            f"/api/v1/sessions/{session_id}/laps",
            headers=_headers(actor),
            json=lap,
        )
        _expect(response, 201, f"create Lap {lap['lap_number']}")
        lap_ids.append(cast(str, response.json()["lap_id"]))
    return lap_ids


def _load_dataset() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(DATASET_PATH.read_text(encoding="utf-8")))


def _seed_team_roles(engine: Engine) -> dict[Role, SeededIdentity]:
    with Session(engine) as session, session.begin():
        team = Team(name=f"Acceptance Team {uuid4()}")
        session.add(team)
        session.flush()
        identities: dict[Role, SeededIdentity] = {}
        for role in Role:
            user = User(
                email=f"acceptance-{role.value.lower()}-{uuid4()}@example.com",
                password_hash="unused-acceptance-password-hash",
            )
            membership = TeamMembership(user=user, team=team, role=role)
            session.add(membership)
            session.flush()
            identities[role] = SeededIdentity(
                user_id=user.user_id,
                membership_id=membership.membership_id,
                team_id=team.team_id,
            )
        return identities


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}


def _expect(response: Response, expected: int, step: str) -> None:
    assert response.status_code == expected, (
        f"{step}: expected {expected}, got {response.status_code}: {response.text}"
    )
