"""Domain conflicts for Session planning policies."""


class SessionAssignmentConflictError(RuntimeError):
    """A Driver or Vehicle is not eligible for the planned Session."""


class SessionNotEditableError(RuntimeError):
    """Only a PLANNED Session may be edited."""


class EventTrackLockedError(RuntimeError):
    """An Event with Sessions cannot be moved to another Track."""
