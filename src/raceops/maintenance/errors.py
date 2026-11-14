"""Controlled failures for maintenance use cases."""


class MaintenanceResponsibleConflictError(RuntimeError):
    """Raised when the responsible User is not active in the selected Team."""
