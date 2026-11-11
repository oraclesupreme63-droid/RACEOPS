"""Unit contracts for sparse Condition Snapshot integrity."""

from decimal import Decimal
from typing import cast
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Table, UniqueConstraint

from raceops.db.base import Base
from raceops.sessions.condition_schemas import ConditionCreateRequest
from raceops.sessions.models import ConditionSnapshot


def test_condition_table_enforces_one_team_safe_non_empty_snapshot() -> None:
    table = cast(Table, ConditionSnapshot.__table__)
    names = {cast(str | None, constraint.name) for constraint in table.constraints}

    assert Base.metadata.tables["condition_snapshots"] is table
    assert "fk_condition_snapshots_session_team" in names
    assert "uq_condition_snapshots_session" in names
    assert "ck_condition_snapshots_ambient_temperature_value_unit_pair" in names
    assert "ck_condition_snapshots_track_temperature_value_unit_pair" in names
    assert "ck_condition_snapshots_at_least_one_known_condition" in names
    assert any(
        isinstance(constraint, ForeignKeyConstraint) for constraint in table.constraints
    )
    assert any(
        isinstance(constraint, UniqueConstraint) for constraint in table.constraints
    )
    assert any(
        isinstance(constraint, CheckConstraint) for constraint in table.constraints
    )


def test_condition_request_keeps_unknown_values_absent_and_normalizes_text() -> None:
    payload = ConditionCreateRequest(
        ambient_temperature=Decimal("24.500"),
        ambient_temperature_unit="  °C  ",
        weather="  Cloudy  ",
    )

    assert payload.ambient_temperature == Decimal("24.500")
    assert payload.ambient_temperature_unit == "°C"
    assert payload.weather == "Cloudy"
    assert payload.track_temperature is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"source": "Manual"},
        {"ambient_temperature": "24.5"},
        {"ambient_temperature_unit": "C"},
        {"track_temperature": "31.2"},
    ],
)
def test_condition_request_rejects_empty_or_unpaired_measurements(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ConditionCreateRequest.model_validate(payload)


def test_condition_model_accepts_decimal_values_without_zero_filling() -> None:
    snapshot = ConditionSnapshot(
        condition_id=uuid4(),
        team_id=uuid4(),
        session_id=uuid4(),
        weather="Dry",
    )

    assert snapshot.weather == "Dry"
    assert snapshot.ambient_temperature is None
    assert snapshot.track_temperature is None
