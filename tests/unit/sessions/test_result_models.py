"""Unit contracts for Lap/Sector enums, metadata, and metric semantics."""

from typing import cast
from uuid import uuid4

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Table, UniqueConstraint

from raceops.db.base import Base
from raceops.sessions.enums import LapClassification, LapSource, SectorStatus
from raceops.sessions.models import Lap, Sector
from raceops.sessions.result_services import calculate_lap_metrics


def test_result_enums_have_stable_values() -> None:
    assert [item.value for item in LapSource] == ["MANUAL", "IMPORTED", "OTHER"]
    assert [item.value for item in LapClassification] == [
        "VALID",
        "INVALID",
        "OUT_LAP",
        "IN_LAP",
        "INCOMPLETE",
    ]
    assert [item.value for item in SectorStatus] == [
        "VALID",
        "INVALID",
        "INCOMPLETE",
    ]


def test_result_tables_enforce_positive_team_safe_ordered_data() -> None:
    lap_table = cast(Table, Lap.__table__)
    sector_table = cast(Table, Sector.__table__)

    assert Base.metadata.tables["laps"] is lap_table
    assert Base.metadata.tables["sectors"] is sector_table
    assert _constraint_names(lap_table, CheckConstraint) == {
        "ck_laps_lap_number_positive",
        "ck_laps_duration_us_positive",
    }
    assert _constraint_names(sector_table, CheckConstraint) == {
        "ck_sectors_sector_order_positive",
        "ck_sectors_duration_us_positive",
    }
    assert "fk_laps_session_team" in _constraint_names(lap_table, ForeignKeyConstraint)
    assert "fk_sectors_lap_team" in _constraint_names(
        sector_table, ForeignKeyConstraint
    )
    assert "uq_laps_session_lap_number" in _constraint_names(
        lap_table, UniqueConstraint
    )
    assert "uq_sectors_lap_sector_order" in _constraint_names(
        sector_table, UniqueConstraint
    )


def test_metrics_exclude_non_valid_laps_and_use_integer_microseconds() -> None:
    valid_slow = _lap(1, 62_000_000, LapClassification.VALID)
    valid_fast = _lap(2, 60_000_000, LapClassification.VALID)
    invalid = _lap(3, 1, LapClassification.INVALID)

    metrics = calculate_lap_metrics([valid_slow, valid_fast, invalid])

    assert metrics.total_laps == 3
    assert metrics.eligible_laps == 2
    assert metrics.excluded_laps == 1
    assert metrics.best_lap_id == valid_fast.lap_id
    assert metrics.best_lap_us == 60_000_000
    assert metrics.average_lap_us == 61_000_000
    assert metrics.consistency_us == 1_000_000


def test_metrics_do_not_invent_values_when_data_is_insufficient() -> None:
    no_eligible = calculate_lap_metrics(
        [_lap(1, 60_000_000, LapClassification.OUT_LAP)]
    )
    one_eligible = calculate_lap_metrics([_lap(1, 60_000_001, LapClassification.VALID)])

    assert no_eligible.best_lap_us is None
    assert no_eligible.average_lap_us is None
    assert no_eligible.consistency_us is None
    assert one_eligible.average_lap_us == 60_000_001
    assert one_eligible.consistency_us is None


def _lap(number: int, duration_us: int, classification: LapClassification) -> Lap:
    return Lap(
        lap_id=uuid4(),
        team_id=uuid4(),
        session_id=uuid4(),
        lap_number=number,
        duration_us=duration_us,
        classification=classification,
    )


def _constraint_names(table: Table, kind: type[object]) -> set[str | None]:
    return {
        cast(str | None, constraint.name)
        for constraint in table.constraints
        if isinstance(constraint, kind)
    }
