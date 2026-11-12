"""Unit contracts for honest Action Outcome semantics."""

from typing import cast
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import Table

from raceops.db.base import Base
from raceops.learning.enums import (
    ActionEvaluationStatus,
    ActionOutcomeClassification,
)
from raceops.learning.models import ActionOutcome
from raceops.learning.outcome_schemas import ActionOutcomeCreateRequest

SESSION_ID = UUID("b74d7cbf-c3c7-42f7-8f58-63dc5d152218")


def test_action_outcome_table_requires_team_safe_action_and_session() -> None:
    table = cast(Table, ActionOutcome.__table__)
    names = {cast(str | None, item.name) for item in table.constraints}

    assert Base.metadata.tables["action_outcomes"] is table
    assert "fk_action_outcomes_action_team" in names
    assert "fk_action_outcomes_evaluation_session_team" in names
    assert "uq_action_outcomes_action" in names
    assert "ck_action_outcomes_has_conclusion" in names


def test_not_evaluated_is_derived_and_never_a_stored_classification() -> None:
    assert ActionEvaluationStatus.NOT_EVALUATED.value == "NOT_EVALUATED"
    assert "NOT_EVALUATED" not in {item.value for item in ActionOutcomeClassification}
    assert ActionOutcomeClassification.NO_MEASURABLE_EFFECT.value == (
        "NO_MEASURABLE_EFFECT"
    )


def test_outcome_request_requires_conclusion_and_rejects_proposed_status() -> None:
    with pytest.raises(ValidationError):
        ActionOutcomeCreateRequest.model_validate(
            {
                "evaluation_session_id": SESSION_ID,
                "classification": "IMPROVED",
            }
        )
    with pytest.raises(ValidationError):
        ActionOutcomeCreateRequest.model_validate(
            {
                "evaluation_session_id": SESSION_ID,
                "classification": "INCONCLUSIVE",
                "public_conclusion": "Insufficient evidence.",
                "concluded_hypothesis_status": "PROPOSED",
            }
        )

    payload = ActionOutcomeCreateRequest.model_validate(
        {
            "evaluation_session_id": SESSION_ID,
            "classification": "NO_MEASURABLE_EFFECT",
            "public_conclusion": "  No repeatable change was measured.  ",
        }
    )
    assert payload.public_conclusion == "No repeatable change was measured."
