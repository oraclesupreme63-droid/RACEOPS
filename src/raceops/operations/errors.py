"""Controlled failures for operational resource use cases."""


class DriverUserConflictError(RuntimeError):
    """Raised when a requested User cannot be linked to a Driver."""
