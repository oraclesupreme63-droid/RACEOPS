"""Unit contracts for Priority scope and Action execution honesty."""

from typing import cast
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import Table

from raceops.db.base import Base
from raceops.learning.decision_schemas import (
    ActionCreateRequest,
    PriorityCreateRequest,
    PriorityUpdateRequest,
)
from raceops.learning.enums import ActionStatus, TargetIntent
from raceops.learning.models import Action, Priority

USER_ID = UUID("8bbfd738-03e5-4a0b-b1db-37260c1b92c4")
SESSION_ID = UUID("ef510090-f1e1-4e54-b27e-d227fdf59771")


def test_priority_table_enforces_target_rank_and_team_safe_links() -> None:
    table = cast(Table, Priority.__table__)
    names = {cast(str | None, item.name) for item in table.constraints}
    index_names = {item.name for item in table.indexes}

    assert Base.metadata.tables["priorities"] is table
    assert "ck_priorities_main_rank_consistent" in names
    assert "ck_priorities_target_consistent" in names
    assert "fk_priorities_source_session_team" in names
    assert "fk_priorities_target_session_team" in names
    assert "fk_priorities_hypothesis_team" in names
    assert "uq_priorities_main_rank_scope" in index_names


def test_action_table_keeps_execution_separate_from_outcome() -> None:
    table = cast(Table, Action.__table__)
    names = {cast(str | None, item.name) for item in table.constraints}

    assert Base.metadata.tables["actions"] is table
    assert "ck_actions_has_motivation" in names
    assert "ck_actions_cancellation_consistent" in names
    assert "fk_actions_priority_team" in names
    assert "outcome" not in Action.__table__.columns
    assert ActionStatus.COMPLETED.value == "COMPLETED"


def test_priority_defaults_to_next_session_and_normalizes_description() -> None:
    payload = PriorityCreateRequest.model_validate(
        {
            "recipient_role": "DRIVER",
            "recipient_user_id": USER_ID,
            "description": "  Release the brake earlier at T4.  ",
        }
    )

    assert payload.target_intent is TargetIntent.NEXT_SESSION
    assert payload.target_session_id is None
    assert payload.description == "Release the brake earlier at T4."
    assert payload.is_main is True
    assert payload.rank is None


@pytest.mark.parametrize(
    "payload",
    [
        {
            "recipient_role": "DRIVER",
            "description": "Invalid target",
            "target_intent": "NEXT_SESSION",
            "target_session_id": SESSION_ID,
        },
        {
            "recipient_role": "DRIVER",
            "description": "Missing target",
            "target_intent": "SPECIFIC_SESSION",
        },
        {
            "recipient_role": "TEAM_MANAGER",
            "description": "Invalid recipient",
        },
        {
            "recipient_role": "DRIVER",
            "description": "Not main",
            "is_main": False,
            "rank": 1,
        },
    ],
)
def test_priority_rejects_inconsistent_scope(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        PriorityCreateRequest.model_validate(payload)


def test_action_requires_motivation_and_public_text_for_non_engineer() -> None:
    with pytest.raises(ValidationError):
        ActionCreateRequest.model_validate(
            {"assignee_role": "ENGINEER", "action_type": "ENGINEERING"}
        )
    with pytest.raises(ValidationError):
        ActionCreateRequest.model_validate(
            {
                "assignee_role": "MECHANIC",
                "action_type": "MECHANICAL",
                "confidential_detail": "Inspect the exact setup.",
            }
        )

    valid = ActionCreateRequest.model_validate(
        {
            "assignee_role": "MECHANIC",
            "action_type": "MECHANICAL",
            "public_summary": "  Inspect the left rear assembly.  ",
        }
    )
    assert valid.public_summary == "Inspect the left rear assembly."


def test_priority_update_requires_explicit_main_state_for_rank() -> None:
    with pytest.raises(ValidationError):
        PriorityUpdateRequest.model_validate({"rank": 2})
    with pytest.raises(ValidationError):
        PriorityUpdateRequest.model_validate({"is_main": False, "rank": 2})

    payload = PriorityUpdateRequest.model_validate({"is_main": True, "rank": 2})
    assert payload.rank == 2
