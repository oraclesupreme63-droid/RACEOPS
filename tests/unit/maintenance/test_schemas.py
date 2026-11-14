"""Unit contracts for maintenance request and response schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from raceops.maintenance.enums import MaintenanceType
from raceops.maintenance.schemas import MaintenanceCreateRequest


def test_create_request_normalizes_description() -> None:
    payload = MaintenanceCreateRequest(
        vehicle_id=uuid4(),
        responsible_user_id=uuid4(),
        maintenance_type=MaintenanceType.INSPECTION,
        description="  Inspect brake assembly.  ",
    )

    assert payload.description == "Inspect brake assembly."


@pytest.mark.parametrize("field", ["team_id", "status", "session_id"])
def test_create_request_forbids_server_controlled_fields(field: str) -> None:
    data = {
        "vehicle_id": uuid4(),
        "responsible_user_id": uuid4(),
        "maintenance_type": "REPAIR",
        "description": "Repair wheel bearing.",
        field: uuid4(),
    }

    with pytest.raises(ValidationError):
        MaintenanceCreateRequest.model_validate(data)
