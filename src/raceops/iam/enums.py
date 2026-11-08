"""Stable identity values shared by persistence and API contracts."""

from enum import StrEnum


class IdentityStatus(StrEnum):
    """Lifecycle status for identity records preserved in history."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Role(StrEnum):
    """One primary authorization role within a team membership."""

    ADMINISTRATOR = "ADMINISTRATOR"
    TEAM_MANAGER = "TEAM_MANAGER"
    ENGINEER = "ENGINEER"
    MECHANIC = "MECHANIC"
    DRIVER = "DRIVER"
