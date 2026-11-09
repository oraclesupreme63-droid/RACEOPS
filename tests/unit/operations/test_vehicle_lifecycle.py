"""Unit contracts for the controlled Vehicle lifecycle."""

import pytest

from raceops.operations.enums import VehicleStatus
from raceops.operations.vehicles import (
    VEHICLE_STATUS_TRANSITIONS,
    is_vehicle_assignable,
)


def test_vehicle_transition_matrix_is_complete_and_retired_is_terminal() -> None:
    assert set(VEHICLE_STATUS_TRANSITIONS) == set(VehicleStatus)
    assert VEHICLE_STATUS_TRANSITIONS[VehicleStatus.READY] == {
        VehicleStatus.MAINTENANCE,
        VehicleStatus.UNAVAILABLE,
        VehicleStatus.RETIRED,
    }
    assert VEHICLE_STATUS_TRANSITIONS[VehicleStatus.MAINTENANCE] == {
        VehicleStatus.READY,
        VehicleStatus.UNAVAILABLE,
        VehicleStatus.RETIRED,
    }
    assert VEHICLE_STATUS_TRANSITIONS[VehicleStatus.UNAVAILABLE] == {
        VehicleStatus.READY,
        VehicleStatus.MAINTENANCE,
        VehicleStatus.RETIRED,
    }
    assert VEHICLE_STATUS_TRANSITIONS[VehicleStatus.RETIRED] == set()
    assert all(
        status not in targets for status, targets in VEHICLE_STATUS_TRANSITIONS.items()
    )


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (VehicleStatus.READY, True),
        (VehicleStatus.MAINTENANCE, False),
        (VehicleStatus.UNAVAILABLE, False),
        (VehicleStatus.RETIRED, False),
    ],
)
def test_only_ready_vehicle_is_assignable(
    status: VehicleStatus,
    expected: bool,
) -> None:
    assert is_vehicle_assignable(status) is expected
