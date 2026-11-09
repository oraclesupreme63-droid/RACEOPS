"""Unit contracts for Session enums and SQLAlchemy metadata."""

from typing import cast

from sqlalchemy import (
    CheckConstraint,
    DefaultClause,
    Enum,
    ForeignKeyConstraint,
    Table,
)

from raceops.db.base import Base
from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.models import RaceSession


def test_session_enums_have_stable_values() -> None:
    assert [status.value for status in SessionStatus] == [
        "PLANNED",
        "ACTIVE",
        "PAUSED",
        "COMPLETED",
        "CANCELLED",
    ]
    assert [status.value for status in ResultsStatus] == ["OPEN", "LOCKED"]


def test_session_table_is_registered_in_shared_metadata() -> None:
    assert RaceSession.__table__ is Base.metadata.tables["sessions"]


def test_session_status_columns_have_independent_defaults() -> None:
    table = cast(Table, RaceSession.__table__)
    activity_status = table.c.status
    results_status = table.c.results_status

    assert cast(Enum, activity_status.type).enum_class is SessionStatus
    assert cast(Enum, results_status.type).enum_class is ResultsStatus
    assert isinstance(activity_status.server_default, DefaultClause)
    assert isinstance(results_status.server_default, DefaultClause)
    assert str(activity_status.server_default.arg) == "PLANNED"
    assert str(results_status.server_default.arg) == "OPEN"


def test_session_cross_team_references_use_composite_foreign_keys() -> None:
    table = cast(Table, RaceSession.__table__)
    foreign_keys = {
        constraint.name: tuple(constraint.column_keys)
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }

    assert foreign_keys["fk_sessions_event_team"] == ("event_id", "team_id")
    assert foreign_keys["fk_sessions_driver_team"] == ("driver_id", "team_id")
    assert foreign_keys["fk_sessions_vehicle_team"] == ("vehicle_id", "team_id")


def test_session_checks_and_indexes_are_explicit() -> None:
    table = cast(Table, RaceSession.__table__)
    check_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert check_names == {
        "ck_sessions_session_type_normalized",
        "ck_sessions_activity_timestamps_consistent",
        "ck_sessions_activity_time_order_valid",
        "ck_sessions_results_lock_consistent",
        "ck_sessions_results_lock_requires_terminal_activity",
    }
    assert {index.name for index in table.indexes} == {
        "ix_sessions_team_scheduled_at",
        "ix_sessions_team_event",
        "ix_sessions_team_driver",
        "ix_sessions_team_vehicle",
    }
