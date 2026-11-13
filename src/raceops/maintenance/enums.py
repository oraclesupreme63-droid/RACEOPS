"""Controlled vocabulary for vehicle maintenance interventions."""

from enum import StrEnum


class MaintenanceType(StrEnum):
    """Small V1 classification of recorded intervention work."""

    INSPECTION = "INSPECTION"
    PREVENTIVE_SERVICE = "PREVENTIVE_SERVICE"
    REPAIR = "REPAIR"
    REPLACEMENT = "REPLACEMENT"


class MaintenanceStatus(StrEnum):
    """Execution state independent from Vehicle availability."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
