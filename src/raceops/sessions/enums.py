"""Stable lifecycle values for motorsport Sessions and their results."""

from enum import StrEnum


class SessionStatus(StrEnum):
    """Lifecycle of the on-track activity."""

    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ResultsStatus(StrEnum):
    """Independent mutability state for recorded Session results."""

    OPEN = "OPEN"
    LOCKED = "LOCKED"


class LapSource(StrEnum):
    """Traceable origin of one canonical lap result."""

    MANUAL = "MANUAL"
    IMPORTED = "IMPORTED"
    OTHER = "OTHER"


class LapClassification(StrEnum):
    """Whether and why a lap participates in primary metrics."""

    VALID = "VALID"
    INVALID = "INVALID"
    OUT_LAP = "OUT_LAP"
    IN_LAP = "IN_LAP"
    INCOMPLETE = "INCOMPLETE"


class SectorStatus(StrEnum):
    """Data-quality state for an optional sector result."""

    VALID = "VALID"
    INVALID = "INVALID"
    INCOMPLETE = "INCOMPLETE"
