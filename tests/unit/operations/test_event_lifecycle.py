"""Unit contracts for the deliberately small Event lifecycle."""

from raceops.operations.enums import EventStatus
from raceops.operations.events import EVENT_STATUS_TRANSITIONS


def test_event_transition_matrix_is_complete_and_terminal_states_stay_closed() -> None:
    assert set(EVENT_STATUS_TRANSITIONS) == set(EventStatus)
    assert EVENT_STATUS_TRANSITIONS[EventStatus.PLANNED] == {
        EventStatus.ACTIVE,
        EventStatus.COMPLETED,
        EventStatus.CANCELLED,
    }
    assert EVENT_STATUS_TRANSITIONS[EventStatus.ACTIVE] == {
        EventStatus.COMPLETED,
        EventStatus.CANCELLED,
    }
    assert EVENT_STATUS_TRANSITIONS[EventStatus.COMPLETED] == set()
    assert EVENT_STATUS_TRANSITIONS[EventStatus.CANCELLED] == set()
    assert all(
        status not in targets for status, targets in EVENT_STATUS_TRANSITIONS.items()
    )
