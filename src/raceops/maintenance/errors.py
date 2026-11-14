"""Controlled failures for maintenance use cases."""


class MaintenanceResponsibleConflictError(RuntimeError):
    """Raised when the responsible User is not active in the selected Team."""


class InvalidMaintenanceStatusTransitionError(RuntimeError):
    """Raised when a maintenance lifecycle command is not allowed."""


class MaintenanceRecordLockedError(RuntimeError):
    """Raised when normal editing targets a record that is no longer OPEN."""


class MaintenanceContextConflictError(RuntimeError):
    """Raised when optional causal references contradict one another."""
