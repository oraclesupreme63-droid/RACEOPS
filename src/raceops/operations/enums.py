"""Stable lifecycle values for RaceOps operational resources."""

from enum import StrEnum


class DriverStatus(StrEnum):
    """Whether a Driver can be selected for future work."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class VehicleStatus(StrEnum):
    """Explicit operational availability of a Vehicle."""

    READY = "READY"
    MAINTENANCE = "MAINTENANCE"
    UNAVAILABLE = "UNAVAILABLE"
    RETIRED = "RETIRED"


class EventStatus(StrEnum):
    """Small V1 lifecycle for an Event."""

    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
