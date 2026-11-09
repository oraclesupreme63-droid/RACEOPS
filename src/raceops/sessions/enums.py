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
