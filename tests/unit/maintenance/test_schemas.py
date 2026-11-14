"""Unit contracts for maintenance request and response schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from raceops.maintenance.enums import MaintenanceType
from raceops.maintenance.schemas import (
    MaintenanceCancelRequest,
    MaintenanceCompleteRequest,
    MaintenanceCreateRequest,
    MaintenanceUpdateRequest,
)


def test_create_request_normalizes_description() -> None:
    payload = MaintenanceCreateRequest(
        vehicle_id=uuid4(),
        responsible_user_id=uuid4(),
        maintenance_type=MaintenanceType.INSPECTION,
        description="  Inspect brake assembly.  ",
    )

    assert payload.description == "Inspect brake assembly."


@pytest.mark.parametrize("field", ["team_id", "status", "created_by_user_id"])
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


def test_create_request_accepts_explicit_optional_causal_references() -> None:
    session_id = uuid4()
    observation_id = uuid4()
    action_id = uuid4()

    payload = MaintenanceCreateRequest(
        vehicle_id=uuid4(),
        responsible_user_id=uuid4(),
        session_id=session_id,
        observation_id=observation_id,
        action_id=action_id,
        maintenance_type=MaintenanceType.REPAIR,
        description="Investigate recorded symptom.",
    )

    assert payload.session_id == session_id
    assert payload.observation_id == observation_id
    assert payload.action_id == action_id


def test_update_and_terminal_requests_normalize_text() -> None:
    update = MaintenanceUpdateRequest(description="  Inspect steering column.  ")
    complete = MaintenanceCompleteRequest(
        completion_notes="  Bearing replaced and verified.  "
    )
    cancel = MaintenanceCancelRequest(cancellation_reason="  Duplicate work order.  ")

    assert update.description == "Inspect steering column."
    assert complete.completion_notes == "Bearing replaced and verified."
    assert cancel.cancellation_reason == "Duplicate work order."


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"description": None},
        {"maintenance_type": None},
        {"responsible_user_id": None},
        {"description": "   "},
        {"status": "COMPLETED"},
    ],
)
def test_update_request_requires_non_null_allowed_changes(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        MaintenanceUpdateRequest.model_validate(payload)


@pytest.mark.parametrize(
    ("schema", "field"),
    [
        (MaintenanceCompleteRequest, "completion_notes"),
        (MaintenanceCancelRequest, "cancellation_reason"),
    ],
)
def test_terminal_requests_require_non_blank_text(
    schema: type[MaintenanceCompleteRequest] | type[MaintenanceCancelRequest],
    field: str,
) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate({field: "   "})
