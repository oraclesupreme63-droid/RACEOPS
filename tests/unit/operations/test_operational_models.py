"""Unit contracts for operational enums and SQLAlchemy metadata."""

from typing import cast

from sqlalchemy import (
    CheckConstraint,
    DefaultClause,
    Enum,
    ForeignKeyConstraint,
    Table,
    UniqueConstraint,
)

from raceops.db.base import Base
from raceops.operations.enums import DriverStatus, EventStatus, VehicleStatus
from raceops.operations.models import Driver, Event, Track, Vehicle


def test_operational_enums_have_stable_values() -> None:
    assert [status.value for status in DriverStatus] == ["ACTIVE", "INACTIVE"]
    assert [status.value for status in VehicleStatus] == [
        "READY",
        "MAINTENANCE",
        "UNAVAILABLE",
        "RETIRED",
    ]
    assert [status.value for status in EventStatus] == [
        "PLANNED",
        "ACTIVE",
        "COMPLETED",
        "CANCELLED",
    ]


def test_operational_tables_are_registered_in_shared_metadata() -> None:
    assert {"drivers", "vehicles", "tracks", "events"} <= set(Base.metadata.tables)
    assert Driver.__table__ is Base.metadata.tables["drivers"]
    assert Vehicle.__table__ is Base.metadata.tables["vehicles"]
    assert Track.__table__ is Base.metadata.tables["tracks"]
    assert Event.__table__ is Base.metadata.tables["events"]


def test_status_columns_have_expected_enums_and_defaults() -> None:
    driver_status = cast(Table, Driver.__table__).c.status
    vehicle_status = cast(Table, Vehicle.__table__).c.status
    event_status = cast(Table, Event.__table__).c.status

    assert cast(Enum, driver_status.type).enum_class is DriverStatus
    assert cast(Enum, vehicle_status.type).enum_class is VehicleStatus
    assert cast(Enum, event_status.type).enum_class is EventStatus
    assert isinstance(driver_status.server_default, DefaultClause)
    assert isinstance(vehicle_status.server_default, DefaultClause)
    assert isinstance(event_status.server_default, DefaultClause)
    assert str(driver_status.server_default.arg) == "ACTIVE"
    assert str(vehicle_status.server_default.arg) == "READY"
    assert str(event_status.server_default.arg) == "PLANNED"


def test_driver_and_vehicle_uniqueness_is_scoped_to_team() -> None:
    driver_table = cast(Table, Driver.__table__)
    vehicle_table = cast(Table, Vehicle.__table__)

    driver_unique = {
        constraint.name
        for constraint in driver_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    vehicle_unique = {
        constraint.name
        for constraint in vehicle_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert driver_unique == {
        "uq_drivers_driver_team",
        "uq_drivers_team_user",
    }
    assert vehicle_unique == {
        "uq_vehicles_team_identifier",
        "uq_vehicles_vehicle_team",
    }


def test_cross_team_links_are_protected_by_composite_foreign_keys() -> None:
    driver_table = cast(Table, Driver.__table__)
    event_table = cast(Table, Event.__table__)
    driver_foreign_keys = {
        constraint.name: tuple(constraint.column_keys)
        for constraint in driver_table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    event_foreign_keys = {
        constraint.name: tuple(constraint.column_keys)
        for constraint in event_table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }

    assert driver_foreign_keys["fk_drivers_user_team_membership"] == (
        "user_id",
        "team_id",
    )
    assert event_foreign_keys["fk_events_track_team"] == (
        "track_id",
        "team_id",
    )


def test_operational_checks_and_indexes_are_explicit() -> None:
    tables = [
        cast(Table, Driver.__table__),
        cast(Table, Vehicle.__table__),
        cast(Table, Track.__table__),
        cast(Table, Event.__table__),
    ]
    check_names = {
        constraint.name
        for table in tables
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert check_names == {
        "ck_drivers_display_name_normalized",
        "ck_vehicles_identifier_normalized",
        "ck_tracks_name_normalized",
        "ck_tracks_location_normalized",
        "ck_events_name_normalized",
        "ck_events_date_range_valid",
        "ck_events_description_normalized",
    }
    assert {index.name for index in cast(Table, Event.__table__).indexes} == {
        "ix_events_team_starts_on"
    }
