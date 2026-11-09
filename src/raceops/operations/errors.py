"""Controlled failures for operational resource use cases."""


class DriverUserConflictError(RuntimeError):
    """Raised when a requested User cannot be linked to a Driver."""


class VehicleIdentifierConflictError(RuntimeError):
    """Raised when a Vehicle identifier is already used in the Team."""


class InvalidVehicleStatusTransitionError(RuntimeError):
    """Raised when the requested Vehicle lifecycle transition is forbidden."""
