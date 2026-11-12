"""HTTP contracts for recipient priorities and honest Action execution."""

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
from raceops.learning.enums import (
    AnalysisEvidenceType,
    CauseClassification,
    ConfidenceLevel,
)
from raceops.learning.models import (
    ActionOutcome,
    AnalysisEvidenceReference,
    Hypothesis,
    Observation,
    SessionAnalysis,
)
from raceops.main import create_app
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.models import RaceSession

RUN_DATABASE_TESTS = os.getenv("RACEOPS_RUN_DB_TESTS") == "1"
JWT_SECRET = "decision-api-test-secret-never-used-in-production"
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
    driver: SeededIdentity
    source_session_id: UUID
    target_session_id: UUID


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
async def test_priority_limit_visibility_and_action_execution_are_enforced(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    foreign_context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.ENGINEER
    )
    manager = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.TEAM_MANAGER
    )
    mechanic = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.MECHANIC
    )
    administrator = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.ADMINISTRATOR
    )
    hypothesis_id = _seed_hypothesis(database_engine, context, engineer)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        priorities = []
        for number in range(1, 4):
            response = await client.post(
                f"/api/v1/sessions/{context.source_session_id}/priorities",
                headers=_headers(engineer),
                json={
                    "hypothesis_id": str(hypothesis_id) if number == 1 else None,
                    "recipient_role": "DRIVER",
                    "recipient_user_id": str(context.driver.user_id),
                    "description": f"Driver focus {number}",
                },
            )
            assert response.status_code == 201
            priorities.append(response.json())
        fourth_main = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "recipient_role": "DRIVER",
                "recipient_user_id": str(context.driver.user_id),
                "description": "Fourth main focus",
            },
        )
        note = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "recipient_role": "DRIVER",
                "recipient_user_id": str(context.driver.user_id),
                "description": "Additional note",
                "is_main": False,
            },
        )
        specific_target = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "target_intent": "SPECIFIC_SESSION",
                "target_session_id": str(context.target_session_id),
                "recipient_role": "ENGINEER",
                "description": "Review balance on the scheduled test",
            },
        )
        driver_priorities = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(context.driver),
        )
        manager_priorities = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(manager),
        )
        mechanic_priorities = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(mechanic),
        )
        manager_update = await client.patch(
            f"/api/v1/priorities/{priorities[0]['priority_id']}",
            headers=_headers(manager),
            json={"description": "Manager edit attempt"},
        )
        demoted = await client.patch(
            f"/api/v1/priorities/{priorities[2]['priority_id']}",
            headers=_headers(engineer),
            json={"is_main": False},
        )
        replacement_main = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "recipient_role": "DRIVER",
                "recipient_user_id": str(context.driver.user_id),
                "description": "Replacement main focus",
            },
        )
        invalid_same_target = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "target_intent": "SPECIFIC_SESSION",
                "target_session_id": str(context.source_session_id),
                "recipient_role": "ENGINEER",
                "description": "A source cannot target itself",
            },
        )

        created_action = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(engineer),
            json={
                "hypothesis_id": str(hypothesis_id),
                "priority_id": priorities[0]["priority_id"],
                "assignee_role": "DRIVER",
                "assignee_user_id": str(context.driver.user_id),
                "action_type": "DRIVING",
                "public_summary": "Release the brake earlier at T4.",
                "confidential_detail": "Compare release trace against best lap.",
            },
        )
        action_id = created_action.json()["action_id"]
        hidden_action = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(engineer),
            json={
                "assignee_role": "ENGINEER",
                "action_type": "ENGINEERING",
                "confidential_detail": "Test exact setup direction B.",
            },
        )
        driver_actions = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(context.driver),
        )
        manager_actions = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(manager),
        )
        mechanic_actions = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(mechanic),
        )
        administrator_actions = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(administrator),
        )
        premature_complete = await client.post(
            f"/api/v1/actions/{action_id}/complete",
            headers=_headers(context.driver),
        )
        planned = await client.post(
            f"/api/v1/actions/{action_id}/plan",
            headers=_headers(context.driver),
        )
        started = await client.post(
            f"/api/v1/actions/{action_id}/start",
            headers=_headers(context.driver),
        )
        completed = await client.post(
            f"/api/v1/actions/{action_id}/complete",
            headers=_headers(context.driver),
        )
        foreign_assignee = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(engineer),
            json={
                "assignee_role": "DRIVER",
                "assignee_user_id": str(foreign_context.driver.user_id),
                "action_type": "DRIVING",
                "public_summary": "Foreign assignee must be rejected.",
            },
        )
        manager_confidential = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(manager),
            json={
                "assignee_role": "ENGINEER",
                "action_type": "ENGINEERING",
                "confidential_detail": "Manager cannot write this.",
            },
        )
        mechanic_action = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(mechanic),
            json={
                "assignee_role": "MECHANIC",
                "assignee_user_id": str(mechanic.user_id),
                "action_type": "MECHANICAL",
                "public_summary": "Inspect left rear assembly.",
            },
        )
        mechanic_action_id = mechanic_action.json()["action_id"]
        await client.post(
            f"/api/v1/actions/{mechanic_action_id}/plan",
            headers=_headers(mechanic),
        )
        cancelled = await client.post(
            f"/api/v1/actions/{mechanic_action_id}/cancel",
            headers=_headers(mechanic),
            json={"reason": "Part unavailable before next session."},
        )
        driver_actions_after_mechanical = await client.get(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(context.driver),
        )

    assert [item["rank"] for item in priorities] == [1, 2, 3]
    assert all(item["target_intent"] == "NEXT_SESSION" for item in priorities)
    assert all("target_session_id" not in item for item in priorities)
    assert fourth_main.status_code == 409
    assert fourth_main.json()["code"] == "priority_scope_conflict"
    assert note.status_code == 201
    assert note.json()["is_main"] is False
    assert "rank" not in note.json()
    assert specific_target.status_code == 201
    assert specific_target.json()["target_session_id"] == str(context.target_session_id)
    assert driver_priorities.json()["total"] == 4
    assert all(
        "hypothesis_id" not in item for item in driver_priorities.json()["items"]
    )
    assert manager_priorities.json()["total"] == 5
    assert mechanic_priorities.json()["total"] == 0
    assert manager_update.status_code == 403
    assert demoted.status_code == 200
    assert demoted.json()["is_main"] is False
    assert "rank" not in demoted.json()
    assert replacement_main.status_code == 201
    assert replacement_main.json()["rank"] == 3
    assert invalid_same_target.status_code == 422

    assert created_action.status_code == 201
    assert created_action.json()["status"] == "PROPOSED"
    assert created_action.json()["confidential_detail"] == (
        "Compare release trace against best lap."
    )
    assert hidden_action.status_code == 201
    assert driver_actions.json()["total"] == 1
    driver_action = driver_actions.json()["items"][0]
    assert "confidential_detail" not in driver_action
    assert "hypothesis_id" not in driver_action
    assert "priority_id" not in driver_action
    assert manager_actions.json()["total"] == 2
    assert all(
        "confidential_detail" not in item for item in manager_actions.json()["items"]
    )
    assert mechanic_actions.json()["total"] == 0
    assert administrator_actions.json()["total"] == 0
    assert premature_complete.status_code == 409
    assert planned.json()["status"] == "PLANNED"
    assert started.json()["status"] == "IN_PROGRESS"
    assert completed.json()["status"] == "COMPLETED"
    assert "outcome" not in completed.json()
    assert foreign_assignee.status_code == 404
    assert manager_confidential.status_code == 403
    assert mechanic_action.status_code == 201
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert cancelled.json()["cancellation_reason"] == (
        "Part unavailable before next session."
    )
    assert driver_actions_after_mechanical.json()["total"] == 2
    assert any(
        item.get("public_summary") == "Inspect left rear assembly."
        for item in driver_actions_after_mechanical.json()["items"]
    )


def test_openapi_documents_decisions_without_delete() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/sessions/{source_session_id}/priorities"]) == {
        "get",
        "post",
    }
    assert set(paths["/api/v1/priorities/{priority_id}"]) == {"get", "patch"}
    assert set(paths["/api/v1/sessions/{source_session_id}/actions"]) == {
        "get",
        "post",
    }
    assert set(paths["/api/v1/actions/{action_id}"]) == {"get"}
    for transition_name in ("plan", "start", "complete", "cancel"):
        assert set(paths[f"/api/v1/actions/{{action_id}}/{transition_name}"]) == {
            "post"
        }


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_outcome_resolves_next_session_and_preserves_authorized_chain(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    foreign_context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.ENGINEER
    )
    manager = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.TEAM_MANAGER
    )
    hypothesis_id = _seed_hypothesis(database_engine, context, engineer)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        priority = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/priorities",
            headers=_headers(engineer),
            json={
                "hypothesis_id": str(hypothesis_id),
                "recipient_role": "DRIVER",
                "recipient_user_id": str(context.driver.user_id),
                "description": "Improve brake release at T4.",
            },
        )
        created = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(engineer),
            json={
                "hypothesis_id": str(hypothesis_id),
                "priority_id": priority.json()["priority_id"],
                "assignee_role": "DRIVER",
                "assignee_user_id": str(context.driver.user_id),
                "action_type": "DRIVING",
                "public_summary": "Release the brake earlier at T4.",
                "confidential_detail": "Compare the release trace.",
            },
        )
        action_id = created.json()["action_id"]
        not_evaluated = await client.get(
            f"/api/v1/actions/{action_id}/outcome", headers=_headers(engineer)
        )
        premature = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(engineer),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "IMPROVED",
                "public_conclusion": "Too early.",
            },
        )
        for transition_name in ("plan", "start", "complete"):
            transitioned = await client.post(
                f"/api/v1/actions/{action_id}/{transition_name}",
                headers=_headers(engineer),
            )
            assert transitioned.status_code == 200
        wrong_team = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(engineer),
            json={
                "evaluation_session_id": str(foreign_context.target_session_id),
                "classification": "IMPROVED",
                "public_conclusion": "Foreign evidence must be hidden.",
            },
        )
        evaluated = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(engineer),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "IMPROVED",
                "public_conclusion": "Consistency improved in Practice 2.",
                "confidential_conclusion": "The brake-release trace also improved.",
                "concluded_hypothesis_status": "PARTIALLY_SUPPORTED",
            },
        )
        duplicate = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(engineer),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "INCONCLUSIVE",
                "public_conclusion": "Duplicate evaluation.",
            },
        )
        resolved_action = await client.get(
            f"/api/v1/actions/{action_id}", headers=_headers(engineer)
        )
        resolved_priority = await client.get(
            f"/api/v1/priorities/{priority.json()['priority_id']}",
            headers=_headers(engineer),
        )
        engineer_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(engineer),
        )
        manager_evaluation = await client.get(
            f"/api/v1/actions/{action_id}/outcome", headers=_headers(manager)
        )
        driver_chain = await client.get(
            f"/api/v1/actions/{action_id}/learning-chain",
            headers=_headers(context.driver),
        )
        driver_write = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(context.driver),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "IMPROVED",
                "public_conclusion": "Driver cannot author Outcome.",
            },
        )

    assert created.status_code == 201
    assert priority.status_code == 201
    assert created.json()["evaluation_status"] == "NOT_EVALUATED"
    assert not_evaluated.status_code == 200
    assert not_evaluated.json() == {
        "action_id": action_id,
        "evaluation_status": "NOT_EVALUATED",
    }
    assert premature.status_code == 409
    assert premature.json()["code"] == "invalid_action_outcome"
    assert wrong_team.status_code == 404
    assert evaluated.status_code == 201
    assert evaluated.json()["classification"] == "IMPROVED"
    assert evaluated.json()["concluded_hypothesis_status"] == "PARTIALLY_SUPPORTED"
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "action_outcome_conflict"
    assert resolved_action.json()["target_intent"] == "SPECIFIC_SESSION"
    assert resolved_action.json()["target_session_id"] == str(context.target_session_id)
    assert resolved_action.json()["evaluation_status"] == "IMPROVED"
    assert resolved_priority.json()["target_intent"] == "SPECIFIC_SESSION"
    assert resolved_priority.json()["target_session_id"] == str(
        context.target_session_id
    )
    engineer_chain_body = engineer_chain.json()
    assert (
        engineer_chain_body["priority"]["priority_id"] == priority.json()["priority_id"]
    )
    assert engineer_chain_body["hypothesis"]["status"] == "PARTIALLY_SUPPORTED"
    assert engineer_chain_body["analysis"]["technical_detail"]
    assert engineer_chain_body["analysis"]["evidence"][0]["evidence_type"] == (
        "OBSERVATION"
    )
    assert engineer_chain_body["evaluation"]["outcome"]["confidential_conclusion"]
    manager_outcome = manager_evaluation.json()["outcome"]
    assert "confidential_conclusion" not in manager_outcome
    assert "concluded_hypothesis_status" not in manager_outcome
    driver_chain_body = driver_chain.json()
    assert "hypothesis" not in driver_chain_body
    assert "analysis" not in driver_chain_body
    assert driver_chain_body["evaluation"]["evaluation_status"] == "IMPROVED"
    assert "confidential_conclusion" not in driver_chain_body["evaluation"]["outcome"]
    assert driver_write.status_code == 403

    with Session(database_engine) as session:
        assert (
            session.query(ActionOutcome).filter_by(action_id=UUID(action_id)).count()
            == 1
        )
        hypothesis = session.get_one(Hypothesis, hypothesis_id)
        assert hypothesis.status.value == "PARTIALLY_SUPPORTED"


def test_openapi_documents_outcomes_without_destructive_endpoints() -> None:
    paths = create_app().openapi()["paths"]

    assert set(paths["/api/v1/actions/{action_id}/outcome"]) == {"get", "post"}
    assert set(paths["/api/v1/actions/{action_id}/learning-chain"]) == {"get"}


@pytest.mark.anyio
@pytest.mark.integration
@requires_database
async def test_mechanic_can_only_record_public_outcome_for_assigned_work(
    application: FastAPI,
    database_engine: Engine,
) -> None:
    context = _seed_context(database_engine)
    engineer = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.ENGINEER
    )
    mechanic = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.MECHANIC
    )
    other_mechanic = _seed_identity(
        database_engine, team_id=context.driver.team_id, role=Role.MECHANIC
    )
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            f"/api/v1/sessions/{context.source_session_id}/actions",
            headers=_headers(engineer),
            json={
                "assignee_role": "MECHANIC",
                "assignee_user_id": str(mechanic.user_id),
                "action_type": "MECHANICAL",
                "public_summary": "Inspect and adjust the left rear assembly.",
            },
        )
        action_id = created.json()["action_id"]
        for transition_name in ("plan", "start", "complete"):
            transitioned = await client.post(
                f"/api/v1/actions/{action_id}/{transition_name}",
                headers=_headers(mechanic),
            )
            assert transitioned.status_code == 200
        hidden_from_other = await client.get(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(other_mechanic),
        )
        forbidden_confidential = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(mechanic),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "NO_MEASURABLE_EFFECT",
                "confidential_conclusion": "Mechanic cannot publish this detail.",
            },
        )
        evaluated = await client.post(
            f"/api/v1/actions/{action_id}/outcome",
            headers=_headers(mechanic),
            json={
                "evaluation_session_id": str(context.target_session_id),
                "classification": "NO_MEASURABLE_EFFECT",
                "public_conclusion": "No repeatable handling change was measured.",
            },
        )

    assert hidden_from_other.status_code == 404
    assert forbidden_confidential.status_code == 403
    assert evaluated.status_code == 201
    assert evaluated.json()["classification"] == "NO_MEASURABLE_EFFECT"


def _seed_context(engine: Engine) -> SeededContext:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"decision-driver-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        team = Team(name=f"Decision Team {uuid4()}")
        membership = TeamMembership(user=user, team=team, role=Role.DRIVER)
        session.add(membership)
        session.flush()
        track = Track(team_id=team.team_id, name=f"Decision Track {uuid4()}")
        driver = Driver(
            team_id=team.team_id,
            user_id=user.user_id,
            display_name="Decision Driver",
        )
        vehicle = Vehicle(team_id=team.team_id, identifier=f"Kart {uuid4()}")
        session.add_all([track, driver, vehicle])
        session.flush()
        event = Event(
            team_id=team.team_id,
            track_id=track.track_id,
            name=f"Decision Event {uuid4()}",
            starts_on=date(2026, 11, 20),
        )
        session.add(event)
        session.flush()
        source = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice 1",
            scheduled_at=datetime(2026, 11, 20, 15, tzinfo=UTC),
        )
        target = RaceSession(
            team_id=team.team_id,
            event_id=event.event_id,
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            session_type="Practice 2",
            scheduled_at=datetime(2026, 11, 20, 16, tzinfo=UTC),
        )
        session.add_all([source, target])
        session.flush()
        return SeededContext(
            driver=SeededIdentity(user.user_id, membership.membership_id, team.team_id),
            source_session_id=source.session_id,
            target_session_id=target.session_id,
        )


def _seed_identity(engine: Engine, *, team_id: UUID, role: Role) -> SeededIdentity:
    with Session(engine) as session, session.begin():
        user = User(
            email=f"decision-{role.value.lower()}-{uuid4()}@example.com",
            password_hash="unused-test-password-hash",
        )
        membership = TeamMembership(user=user, team_id=team_id, role=role)
        session.add(membership)
        session.flush()
        return SeededIdentity(user.user_id, membership.membership_id, team_id)


def _seed_hypothesis(
    engine: Engine,
    context: SeededContext,
    engineer: SeededIdentity,
) -> UUID:
    with Session(engine) as session, session.begin():
        observation = Observation(
            team_id=context.driver.team_id,
            session_id=context.source_session_id,
            author_user_id=engineer.user_id,
            description="Rear instability under braking at T4.",
            category="HANDLING",
        )
        session.add(observation)
        session.flush()
        analysis = SessionAnalysis(
            team_id=context.driver.team_id,
            session_id=context.source_session_id,
            author_user_id=engineer.user_id,
            authorized_summary="Working on rear stability.",
            technical_detail="Rear instability follows abrupt brake release.",
        )
        analysis.evidence_refs = [
            AnalysisEvidenceReference(
                team_id=context.driver.team_id,
                evidence_type=AnalysisEvidenceType.OBSERVATION,
                reference_id=observation.observation_id,
            )
        ]
        session.add(analysis)
        session.flush()
        hypothesis = Hypothesis(
            team_id=context.driver.team_id,
            analysis_id=analysis.analysis_id,
            description="Brake release may amplify rear instability.",
            cause_classification=CauseClassification.DRIVER_TECHNIQUE,
            confidence=ConfidenceLevel.MEDIUM,
        )
        session.add(hypothesis)
        session.flush()
        return hypothesis.hypothesis_id


def _headers(identity: SeededIdentity) -> dict[str, str]:
    token = issue_access_token(
        user_id=identity.user_id,
        membership_id=identity.membership_id,
        secret=JWT_SECRET,
        ttl=timedelta(minutes=15),
    )
    return {"Authorization": f"Bearer {token}"}
