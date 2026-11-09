"""Controlled failures for operational resource use cases."""


class DriverUserConflictError(RuntimeError):
    """Raised when a requested User cannot be linked to a Driver."""


class VehicleIdentifierConflictError(RuntimeError):
    """Raised when a Vehicle identifier is already used in the Team."""


class InvalidVehicleStatusTransitionError(RuntimeError):
    """Raised when the requested Vehicle lifecycle transition is forbidden."""


class EventDateRangeError(RuntimeError):
    """Raised when an Event end date precedes its start date."""


class InvalidEventStatusTransitionError(RuntimeError):
    """Raised when the requested Event lifecycle transition is forbidden."""
