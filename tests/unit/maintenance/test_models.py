"""Unit contracts for maintenance enums and SQLAlchemy metadata."""

from typing import cast

from sqlalchemy import CheckConstraint, DefaultClause, Enum, ForeignKeyConstraint, Table

from raceops.db.base import Base
from raceops.iam.authorization import Visibility
from raceops.maintenance.enums import MaintenanceStatus, MaintenanceType
from raceops.maintenance.models import MaintenanceRecord


def test_maintenance_enums_have_stable_values() -> None:
    assert [kind.value for kind in MaintenanceType] == [
        "INSPECTION",
        "PREVENTIVE_SERVICE",
        "REPAIR",
        "REPLACEMENT",
    ]
    assert [status.value for status in MaintenanceStatus] == [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
    ]


def test_maintenance_table_is_registered_with_safe_defaults() -> None:
    table = cast(Table, MaintenanceRecord.__table__)
    status = table.c.status
    visibility = table.c.visibility_level

    assert table is Base.metadata.tables["maintenance_records"]
    assert cast(Enum, status.type).enum_class is MaintenanceStatus
    assert cast(Enum, visibility.type).enum_class is Visibility
    assert isinstance(status.server_default, DefaultClause)
    assert isinstance(visibility.server_default, DefaultClause)
    assert str(status.server_default.arg) == "OPEN"
    assert str(visibility.server_default.arg) == "ROLE_RESTRICTED"


def test_maintenance_context_and_users_are_team_scoped() -> None:
    table = cast(Table, MaintenanceRecord.__table__)
    foreign_keys = {
        constraint.name: tuple(constraint.column_keys)
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }

    assert foreign_keys["fk_maintenance_records_vehicle_team"] == (
        "vehicle_id",
        "team_id",
    )
    assert foreign_keys["fk_maintenance_records_responsible_membership"] == (
        "responsible_user_id",
        "team_id",
    )
    assert foreign_keys["fk_maintenance_records_creator_membership"] == (
        "created_by_user_id",
        "team_id",
    )
    assert foreign_keys["fk_maintenance_records_session_team"] == (
        "session_id",
        "team_id",
    )
    assert foreign_keys["fk_maintenance_records_observation_team"] == (
        "observation_id",
        "team_id",
    )
    assert foreign_keys["fk_maintenance_records_action_team"] == (
        "action_id",
        "team_id",
    )


def test_maintenance_checks_and_indexes_are_explicit() -> None:
    table = cast(Table, MaintenanceRecord.__table__)
    checks = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert checks == {
        "ck_maintenance_records_description_normalized",
        "ck_maintenance_records_completion_notes_normalized",
        "ck_maintenance_records_cancellation_reason_normalized",
        "ck_maintenance_records_lifecycle_consistent",
        "ck_maintenance_records_completion_time_order_valid",
        "ck_maintenance_records_cancellation_time_order_valid",
        "ck_maintenance_records_role_restricted",
    }
    assert {index.name for index in table.indexes} == {
        "ix_maintenance_records_team_vehicle_created",
        "ix_maintenance_records_team_status",
        "ix_maintenance_records_team_session",
        "ix_maintenance_records_team_observation",
        "ix_maintenance_records_team_action",
    }
