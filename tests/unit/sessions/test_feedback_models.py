"""Unit contracts for low-friction, traceable Driver Feedback."""

from typing import cast

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Table

from raceops.db.base import Base
from raceops.sessions.feedback_schemas import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
)
from raceops.sessions.models import DriverFeedback


def test_feedback_table_preserves_team_safe_session_driver_and_author() -> None:
    table = cast(Table, DriverFeedback.__table__)
    names = {cast(str | None, constraint.name) for constraint in table.constraints}

    assert Base.metadata.tables["driver_feedback"] is table
    assert "fk_driver_feedback_session_team" in names
    assert "fk_driver_feedback_driver_team" in names
    assert "fk_driver_feedback_author_user_id_users" in names
    assert "uq_driver_feedback_feedback_team" in names
    assert "ck_driver_feedback_description_normalized" in names
    assert (
        sum(
            isinstance(constraint, ForeignKeyConstraint)
            for constraint in table.constraints
        )
        == 3
    )
    assert any(
        isinstance(constraint, CheckConstraint) for constraint in table.constraints
    )


def test_feedback_create_requires_only_description_and_normalizes_context() -> None:
    payload = FeedbackCreateRequest(
        description="  Rear instability under braking.  ",
        corner_or_zone=" T4 ",
        driving_phase=" Entry ",
    )

    assert payload.description == "Rear instability under braking."
    assert payload.corner_or_zone == "T4"
    assert payload.driving_phase == "Entry"
    assert payload.severity is None
    assert payload.confidence is None


@pytest.mark.parametrize("description", ["", "   ", None])
def test_feedback_create_rejects_missing_or_blank_description(
    description: str | None,
) -> None:
    with pytest.raises(ValidationError):
        FeedbackCreateRequest.model_validate({"description": description})


def test_feedback_update_allows_clearing_context_but_not_description() -> None:
    payload = FeedbackUpdateRequest(corner_or_zone=None)
    assert payload.model_dump(exclude_unset=True) == {"corner_or_zone": None}

    with pytest.raises(ValidationError):
        FeedbackUpdateRequest(description=None)
    with pytest.raises(ValidationError):
        FeedbackUpdateRequest()
