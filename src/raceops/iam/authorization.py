"""Deny-by-default RBAC, team ownership, and visibility policies."""

from collections.abc import Mapping, Set
from enum import StrEnum
from types import MappingProxyType
from typing import Final
from uuid import UUID

from raceops.iam.enums import Role
from raceops.iam.errors import (
    InsufficientPermissionsError,
    ResourceNotFoundError,
)
from raceops.iam.identity import CurrentIdentity


class Permission(StrEnum):
    """Stable server-side capabilities; relationship rules still apply."""

    MANAGE_MEMBERS = "MANAGE_MEMBERS"
    READ_TEAM_CONFIGURATION = "READ_TEAM_CONFIGURATION"
    READ_DRIVERS = "READ_DRIVERS"
    MANAGE_DRIVERS = "MANAGE_DRIVERS"
    READ_VEHICLES = "READ_VEHICLES"
    MANAGE_VEHICLES = "MANAGE_VEHICLES"
    READ_TRACKS = "READ_TRACKS"
    WRITE_TRACKS = "WRITE_TRACKS"
    READ_EVENTS = "READ_EVENTS"
    WRITE_EVENTS = "WRITE_EVENTS"
    READ_SESSIONS = "READ_SESSIONS"
    WRITE_SESSIONS = "WRITE_SESSIONS"
    READ_RESULTS = "READ_RESULTS"
    WRITE_RESULTS = "WRITE_RESULTS"
    READ_CONDITIONS = "READ_CONDITIONS"
    WRITE_CONDITIONS = "WRITE_CONDITIONS"
    READ_DRIVER_FEEDBACK = "READ_DRIVER_FEEDBACK"
    CREATE_DRIVER_FEEDBACK = "CREATE_DRIVER_FEEDBACK"
    UPDATE_DRIVER_FEEDBACK = "UPDATE_DRIVER_FEEDBACK"
    READ_OBSERVATIONS = "READ_OBSERVATIONS"
    WRITE_OBSERVATIONS = "WRITE_OBSERVATIONS"
    READ_ANALYSIS_SUMMARIES = "READ_ANALYSIS_SUMMARIES"
    WRITE_ANALYSIS = "WRITE_ANALYSIS"
    READ_PRIORITIES = "READ_PRIORITIES"
    WRITE_PRIORITIES = "WRITE_PRIORITIES"
    UPDATE_PRIORITIES = "UPDATE_PRIORITIES"
    READ_ACTIONS = "READ_ACTIONS"
    CREATE_ACTIONS = "CREATE_ACTIONS"
    UPDATE_ASSIGNED_ACTIONS = "UPDATE_ASSIGNED_ACTIONS"
    WRITE_ACTION_OUTCOMES = "WRITE_ACTION_OUTCOMES"
    READ_HISTORY = "READ_HISTORY"


class Visibility(StrEnum):
    """Conservative record visibility levels defined by the domain model."""

    TEAM = "TEAM"
    ROLE_RESTRICTED = "ROLE_RESTRICTED"
    ENGINEERING_CONFIDENTIAL = "ENGINEERING_CONFIDENTIAL"


_ADMINISTRATOR_PERMISSIONS = frozenset(
    {
        Permission.MANAGE_MEMBERS,
        Permission.READ_TEAM_CONFIGURATION,
        Permission.READ_DRIVERS,
        Permission.MANAGE_DRIVERS,
        Permission.READ_VEHICLES,
        Permission.MANAGE_VEHICLES,
        Permission.READ_TRACKS,
        Permission.WRITE_TRACKS,
        Permission.READ_EVENTS,
        Permission.WRITE_EVENTS,
        Permission.READ_SESSIONS,
        Permission.WRITE_SESSIONS,
        Permission.READ_RESULTS,
        Permission.WRITE_RESULTS,
        Permission.READ_CONDITIONS,
        Permission.WRITE_CONDITIONS,
        Permission.READ_DRIVER_FEEDBACK,
        Permission.READ_OBSERVATIONS,
        Permission.READ_ANALYSIS_SUMMARIES,
        Permission.READ_PRIORITIES,
        Permission.READ_ACTIONS,
        Permission.READ_HISTORY,
    }
)
_TEAM_MANAGER_PERMISSIONS = frozenset(
    {
        Permission.READ_TEAM_CONFIGURATION,
        Permission.READ_DRIVERS,
        Permission.MANAGE_DRIVERS,
        Permission.READ_VEHICLES,
        Permission.MANAGE_VEHICLES,
        Permission.READ_TRACKS,
        Permission.WRITE_TRACKS,
        Permission.READ_EVENTS,
        Permission.WRITE_EVENTS,
        Permission.READ_SESSIONS,
        Permission.WRITE_SESSIONS,
        Permission.READ_RESULTS,
        Permission.WRITE_RESULTS,
        Permission.READ_CONDITIONS,
        Permission.WRITE_CONDITIONS,
        Permission.READ_DRIVER_FEEDBACK,
        Permission.CREATE_DRIVER_FEEDBACK,
        Permission.READ_OBSERVATIONS,
        Permission.READ_ANALYSIS_SUMMARIES,
        Permission.READ_PRIORITIES,
        Permission.WRITE_PRIORITIES,
        Permission.READ_ACTIONS,
        Permission.CREATE_ACTIONS,
        Permission.UPDATE_ASSIGNED_ACTIONS,
        Permission.WRITE_ACTION_OUTCOMES,
        Permission.READ_HISTORY,
    }
)
_ENGINEER_PERMISSIONS = frozenset(
    {
        Permission.READ_TEAM_CONFIGURATION,
        Permission.READ_DRIVERS,
        Permission.READ_VEHICLES,
        Permission.READ_TRACKS,
        Permission.WRITE_TRACKS,
        Permission.READ_EVENTS,
        Permission.WRITE_EVENTS,
        Permission.READ_SESSIONS,
        Permission.WRITE_SESSIONS,
        Permission.READ_RESULTS,
        Permission.WRITE_RESULTS,
        Permission.READ_CONDITIONS,
        Permission.WRITE_CONDITIONS,
        Permission.READ_DRIVER_FEEDBACK,
        Permission.CREATE_DRIVER_FEEDBACK,
        Permission.UPDATE_DRIVER_FEEDBACK,
        Permission.READ_OBSERVATIONS,
        Permission.WRITE_OBSERVATIONS,
        Permission.READ_ANALYSIS_SUMMARIES,
        Permission.WRITE_ANALYSIS,
        Permission.READ_PRIORITIES,
        Permission.WRITE_PRIORITIES,
        Permission.UPDATE_PRIORITIES,
        Permission.READ_ACTIONS,
        Permission.CREATE_ACTIONS,
        Permission.UPDATE_ASSIGNED_ACTIONS,
        Permission.WRITE_ACTION_OUTCOMES,
        Permission.READ_HISTORY,
    }
)
_MECHANIC_PERMISSIONS = frozenset(
    {
        Permission.READ_TEAM_CONFIGURATION,
        Permission.READ_DRIVERS,
        Permission.READ_VEHICLES,
        Permission.READ_TRACKS,
        Permission.READ_EVENTS,
        Permission.READ_SESSIONS,
        Permission.READ_RESULTS,
        Permission.READ_CONDITIONS,
        Permission.WRITE_CONDITIONS,
        Permission.READ_DRIVER_FEEDBACK,
        Permission.CREATE_DRIVER_FEEDBACK,
        Permission.READ_OBSERVATIONS,
        Permission.WRITE_OBSERVATIONS,
        Permission.READ_ANALYSIS_SUMMARIES,
        Permission.READ_PRIORITIES,
        Permission.READ_ACTIONS,
        Permission.CREATE_ACTIONS,
        Permission.UPDATE_ASSIGNED_ACTIONS,
        Permission.WRITE_ACTION_OUTCOMES,
        Permission.READ_HISTORY,
    }
)
_DRIVER_PERMISSIONS = frozenset(
    {
        Permission.READ_TEAM_CONFIGURATION,
        Permission.READ_DRIVERS,
        Permission.READ_VEHICLES,
        Permission.READ_TRACKS,
        Permission.READ_EVENTS,
        Permission.READ_SESSIONS,
        Permission.READ_RESULTS,
        Permission.READ_CONDITIONS,
        Permission.READ_DRIVER_FEEDBACK,
        Permission.CREATE_DRIVER_FEEDBACK,
        Permission.UPDATE_DRIVER_FEEDBACK,
        Permission.READ_OBSERVATIONS,
        Permission.READ_ANALYSIS_SUMMARIES,
        Permission.READ_PRIORITIES,
        Permission.READ_ACTIONS,
        Permission.UPDATE_ASSIGNED_ACTIONS,
        Permission.READ_HISTORY,
    }
)

ROLE_PERMISSIONS: Final[Mapping[Role, frozenset[Permission]]] = MappingProxyType(
    {
        Role.ADMINISTRATOR: _ADMINISTRATOR_PERMISSIONS,
        Role.TEAM_MANAGER: _TEAM_MANAGER_PERMISSIONS,
        Role.ENGINEER: _ENGINEER_PERMISSIONS,
        Role.MECHANIC: _MECHANIC_PERMISSIONS,
        Role.DRIVER: _DRIVER_PERMISSIONS,
    }
)


def has_permission(role: Role, permission: Permission) -> bool:
    """Return whether a role has one explicitly granted capability."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def enforce_permission(actor: CurrentIdentity, permission: Permission) -> None:
    """Reject an authenticated actor unless the permission is explicit."""
    if not has_permission(actor.role, permission):
        raise InsufficientPermissionsError


def is_same_team(actor: CurrentIdentity, resource_team_id: UUID) -> bool:
    """Return whether a resource belongs to the actor's selected team."""
    return actor.team_id == resource_team_id


def enforce_team_scope(actor: CurrentIdentity, resource_team_id: UUID) -> None:
    """Hide cross-team resources behind the same not-found outcome."""
    if not is_same_team(actor, resource_team_id):
        raise ResourceNotFoundError


def is_visible_to_actor(
    actor: CurrentIdentity,
    *,
    resource_team_id: UUID,
    visibility: Visibility,
    allowed_roles: Set[Role] = frozenset(),
    is_related: bool = False,
    mechanic_explicitly_authorized: bool = False,
) -> bool:
    """Evaluate Team, relationship, Role, and Visibility without leaking cause."""
    if not is_same_team(actor, resource_team_id):
        return False

    if visibility is Visibility.TEAM:
        return actor.role is not Role.DRIVER or is_related

    if visibility is Visibility.ROLE_RESTRICTED:
        return actor.role in allowed_roles or is_related

    if visibility is Visibility.ENGINEERING_CONFIDENTIAL:
        if actor.role is Role.ENGINEER:
            return True
        return actor.role is Role.MECHANIC and mechanic_explicitly_authorized

    return False


def enforce_visibility(
    actor: CurrentIdentity,
    *,
    resource_team_id: UUID,
    visibility: Visibility,
    allowed_roles: Set[Role] = frozenset(),
    is_related: bool = False,
    mechanic_explicitly_authorized: bool = False,
) -> None:
    """Hide records that fail team, relationship, role, or visibility checks."""
    if not is_visible_to_actor(
        actor,
        resource_team_id=resource_team_id,
        visibility=visibility,
        allowed_roles=allowed_roles,
        is_related=is_related,
        mechanic_explicitly_authorized=mechanic_explicitly_authorized,
    ):
        raise ResourceNotFoundError
