"""Domain conflicts for Session planning policies."""


class SessionAssignmentConflictError(RuntimeError):
    """A Driver or Vehicle is not eligible for the planned Session."""


class SessionNotEditableError(RuntimeError):
    """Only a PLANNED Session may be edited."""


class EventTrackLockedError(RuntimeError):
    """An Event with Sessions cannot be moved to another Track."""


class InvalidSessionStatusTransitionError(RuntimeError):
    """The requested activity command is invalid for the current status."""


class InvalidResultsStatusTransitionError(RuntimeError):
    """Results cannot be locked from the current Session state."""


class ResultsLockedError(RuntimeError):
    """A write was attempted after Session results became immutable."""


class LapNumberConflictError(RuntimeError):
    """A Lap number is already used inside the Session."""


class SectorOrderConflictError(RuntimeError):
    """A Sector order is already used inside the Lap."""


class ConditionSnapshotExistsError(RuntimeError):
    """The Session already owns its single P0 Condition Snapshot."""


class InvalidConditionSnapshotError(RuntimeError):
    """Known conditions violate value/unit or non-empty invariants."""
