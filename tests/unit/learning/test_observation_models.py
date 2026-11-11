"""Unit contracts for honest, contextual Observations."""

from typing import cast
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Table

from raceops.db.base import Base
from raceops.iam.authorization import Visibility
from raceops.learning.models import Observation
from raceops.learning.schemas import (
    ObservationCreateRequest,
    ObservationUpdateRequest,
)


def test_observation_table_requires_context_and_team_safe_references() -> None:
    table = cast(Table, Observation.__table__)
    names = {cast(str | None, constraint.name) for constraint in table.constraints}

    assert Base.metadata.tables["observations"] is table
    assert "ck_observations_has_session_or_vehicle" in names
    assert "fk_observations_session_team" in names
    assert "fk_observations_vehicle_team" in names
    assert "fk_observations_author_user_id_users" in names
    assert "uq_observations_observation_team" in names
    assert any(
        isinstance(constraint, CheckConstraint) for constraint in table.constraints
    )
    assert (
        sum(
            isinstance(constraint, ForeignKeyConstraint)
            for constraint in table.constraints
        )
        == 4
    )


def test_create_observation_normalizes_evidence_without_causal_fields() -> None:
    payload = ObservationCreateRequest(
        vehicle_id=UUID("448d3e72-f453-40ee-bd46-c28ccb3e5b44"),
        description="  Vibration felt under braking.  ",
        category=" Mechanical ",
    )

    assert payload.description == "Vibration felt under braking."
    assert payload.category == "Mechanical"
    assert payload.visibility_level is Visibility.ROLE_RESTRICTED
    assert "cause" not in ObservationCreateRequest.model_fields
    assert "confirmed" not in ObservationCreateRequest.model_fields


@pytest.mark.parametrize(
    "payload",
    [
        {"description": "No context"},
        {"vehicle_id": "448d3e72-f453-40ee-bd46-c28ccb3e5b44", "description": ""},
        {
            "vehicle_id": "448d3e72-f453-40ee-bd46-c28ccb3e5b44",
            "description": "   ",
        },
    ],
)
def test_create_observation_rejects_missing_context_or_description(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ObservationCreateRequest.model_validate(payload)


def test_update_keeps_context_and_visibility_immutable() -> None:
    payload = ObservationUpdateRequest(category=None)

    assert payload.model_dump(exclude_unset=True) == {"category": None}
    with pytest.raises(ValidationError):
        ObservationUpdateRequest.model_validate({"visibility_level": "TEAM"})
    with pytest.raises(ValidationError):
        ObservationUpdateRequest()
