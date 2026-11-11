"""Unit contracts for deny-by-default RBAC and Visibility."""

from uuid import UUID, uuid4

import pytest

from raceops.iam.authorization import (
    ROLE_PERMISSIONS,
    Permission,
    Visibility,
    enforce_permission,
    enforce_team_scope,
    enforce_visibility,
    has_permission,
    is_visible_to_actor,
)
from raceops.iam.enums import Role
from raceops.iam.errors import (
    InsufficientPermissionsError,
    ResourceNotFoundError,
)
from raceops.iam.identity import CurrentIdentity


def test_role_permission_map_covers_every_role_and_is_deny_by_default() -> None:
    assert set(ROLE_PERMISSIONS) == set(Role)
    assert has_permission(Role.ADMINISTRATOR, Permission.MANAGE_MEMBERS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.MANAGE_MEMBERS) is False
    assert has_permission(Role.ENGINEER, Permission.WRITE_ANALYSIS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_OBSERVATIONS) is True
    assert has_permission(Role.DRIVER, Permission.WRITE_ANALYSIS) is False
    assert all(has_permission(role, Permission.READ_DRIVERS) for role in Role)
    assert has_permission(Role.ADMINISTRATOR, Permission.MANAGE_DRIVERS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.MANAGE_DRIVERS) is True
    assert has_permission(Role.ENGINEER, Permission.MANAGE_DRIVERS) is False
    assert has_permission(Role.MECHANIC, Permission.MANAGE_DRIVERS) is False
    assert has_permission(Role.DRIVER, Permission.MANAGE_DRIVERS) is False
    assert has_permission(Role.ADMINISTRATOR, Permission.READ_VEHICLES) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.READ_VEHICLES) is True
    assert has_permission(Role.ENGINEER, Permission.READ_VEHICLES) is True
    assert has_permission(Role.MECHANIC, Permission.READ_VEHICLES) is True
    assert has_permission(Role.DRIVER, Permission.READ_VEHICLES) is True
    assert has_permission(Role.ADMINISTRATOR, Permission.MANAGE_VEHICLES) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.MANAGE_VEHICLES) is True
    assert has_permission(Role.ENGINEER, Permission.MANAGE_VEHICLES) is False
    assert has_permission(Role.MECHANIC, Permission.MANAGE_VEHICLES) is False
    assert has_permission(Role.DRIVER, Permission.MANAGE_VEHICLES) is False
    assert all(has_permission(role, Permission.READ_TRACKS) for role in Role)
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_TRACKS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_TRACKS) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_TRACKS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_TRACKS) is False
    assert has_permission(Role.DRIVER, Permission.WRITE_TRACKS) is False
    assert has_permission(Role.ADMINISTRATOR, Permission.READ_EVENTS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.READ_EVENTS) is True
    assert has_permission(Role.ENGINEER, Permission.READ_EVENTS) is True
    assert has_permission(Role.MECHANIC, Permission.READ_EVENTS) is True
    assert has_permission(Role.DRIVER, Permission.READ_EVENTS) is True
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_EVENTS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_EVENTS) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_EVENTS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_EVENTS) is False
    assert has_permission(Role.DRIVER, Permission.WRITE_EVENTS) is False
    assert all(has_permission(role, Permission.READ_SESSIONS) for role in Role)
    assert all(has_permission(role, Permission.READ_RESULTS) for role in Role)
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_RESULTS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_RESULTS) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_RESULTS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_RESULTS) is False
    assert has_permission(Role.DRIVER, Permission.WRITE_RESULTS) is False
    assert all(has_permission(role, Permission.READ_CONDITIONS) for role in Role)
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_CONDITIONS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_CONDITIONS) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_CONDITIONS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_CONDITIONS) is True
    assert has_permission(Role.DRIVER, Permission.WRITE_CONDITIONS) is False
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_SESSIONS) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_SESSIONS) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_SESSIONS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_SESSIONS) is False
    assert has_permission(Role.DRIVER, Permission.WRITE_SESSIONS) is False
    assert all(has_permission(role, Permission.READ_DRIVER_FEEDBACK) for role in Role)
    assert (
        has_permission(Role.ADMINISTRATOR, Permission.CREATE_DRIVER_FEEDBACK) is False
    )
    assert all(
        has_permission(role, Permission.CREATE_DRIVER_FEEDBACK)
        for role in (Role.TEAM_MANAGER, Role.ENGINEER, Role.MECHANIC, Role.DRIVER)
    )
    assert has_permission(Role.ENGINEER, Permission.UPDATE_DRIVER_FEEDBACK) is True
    assert has_permission(Role.DRIVER, Permission.UPDATE_DRIVER_FEEDBACK) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.UPDATE_DRIVER_FEEDBACK) is False
    assert has_permission(Role.MECHANIC, Permission.UPDATE_DRIVER_FEEDBACK) is False
    assert all(has_permission(role, Permission.READ_OBSERVATIONS) for role in Role)
    assert all(
        has_permission(role, Permission.READ_ANALYSIS_SUMMARIES) for role in Role
    )
    assert all(has_permission(role, Permission.READ_PRIORITIES) for role in Role)
    assert all(has_permission(role, Permission.READ_ACTIONS) for role in Role)
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_PRIORITIES) is True
    assert has_permission(Role.ENGINEER, Permission.WRITE_PRIORITIES) is True
    assert has_permission(Role.ENGINEER, Permission.UPDATE_PRIORITIES) is True
    assert has_permission(Role.TEAM_MANAGER, Permission.UPDATE_PRIORITIES) is False
    assert has_permission(Role.MECHANIC, Permission.CREATE_ACTIONS) is True
    assert has_permission(Role.DRIVER, Permission.CREATE_ACTIONS) is False
    assert has_permission(Role.ENGINEER, Permission.WRITE_OBSERVATIONS) is True
    assert has_permission(Role.MECHANIC, Permission.WRITE_OBSERVATIONS) is True
    assert has_permission(Role.ADMINISTRATOR, Permission.WRITE_OBSERVATIONS) is False
    assert has_permission(Role.TEAM_MANAGER, Permission.WRITE_OBSERVATIONS) is False
    assert has_permission(Role.DRIVER, Permission.WRITE_OBSERVATIONS) is False


@pytest.mark.parametrize(
    ("role", "allowed"),
    [
        (Role.ADMINISTRATOR, False),
        (Role.TEAM_MANAGER, False),
        (Role.ENGINEER, True),
        (Role.MECHANIC, False),
        (Role.DRIVER, False),
    ],
)
def test_engineering_confidential_is_not_granted_by_hierarchy(
    role: Role,
    allowed: bool,
) -> None:
    actor = _identity(role)

    assert (
        is_visible_to_actor(
            actor,
            resource_team_id=actor.team_id,
            visibility=Visibility.ENGINEERING_CONFIDENTIAL,
        )
        is allowed
    )


def test_mechanic_requires_explicit_engineering_authorization() -> None:
    mechanic = _identity(Role.MECHANIC)

    assert (
        is_visible_to_actor(
            mechanic,
            resource_team_id=mechanic.team_id,
            visibility=Visibility.ENGINEERING_CONFIDENTIAL,
            mechanic_explicitly_authorized=True,
        )
        is True
    )


def test_driver_requires_relationship_even_for_team_visibility() -> None:
    driver = _identity(Role.DRIVER)

    assert (
        is_visible_to_actor(
            driver,
            resource_team_id=driver.team_id,
            visibility=Visibility.TEAM,
        )
        is False
    )
    assert (
        is_visible_to_actor(
            driver,
            resource_team_id=driver.team_id,
            visibility=Visibility.TEAM,
            is_related=True,
        )
        is True
    )


def test_role_restricted_accepts_only_declared_role_or_related_recipient() -> None:
    manager = _identity(Role.TEAM_MANAGER)
    driver = _identity(Role.DRIVER, team_id=manager.team_id)
    allowed_roles = frozenset({Role.TEAM_MANAGER, Role.ENGINEER})

    assert (
        is_visible_to_actor(
            manager,
            resource_team_id=manager.team_id,
            visibility=Visibility.ROLE_RESTRICTED,
            allowed_roles=allowed_roles,
        )
        is True
    )
    assert (
        is_visible_to_actor(
            driver,
            resource_team_id=driver.team_id,
            visibility=Visibility.ROLE_RESTRICTED,
            allowed_roles=allowed_roles,
        )
        is False
    )
    assert (
        is_visible_to_actor(
            driver,
            resource_team_id=driver.team_id,
            visibility=Visibility.ROLE_RESTRICTED,
            allowed_roles=allowed_roles,
            is_related=True,
        )
        is True
    )


def test_cross_team_scope_and_visibility_share_not_found_outcome() -> None:
    actor = _identity(Role.ENGINEER)
    other_team_id = uuid4()

    assert (
        is_visible_to_actor(
            actor,
            resource_team_id=other_team_id,
            visibility=Visibility.TEAM,
        )
        is False
    )
    with pytest.raises(ResourceNotFoundError):
        enforce_team_scope(actor, other_team_id)
    with pytest.raises(ResourceNotFoundError):
        enforce_visibility(
            actor,
            resource_team_id=other_team_id,
            visibility=Visibility.TEAM,
        )


def test_permission_failure_is_distinct_from_hidden_resource() -> None:
    driver = _identity(Role.DRIVER)

    with pytest.raises(InsufficientPermissionsError):
        enforce_permission(driver, Permission.MANAGE_MEMBERS)
    enforce_permission(driver, Permission.CREATE_DRIVER_FEEDBACK)
    enforce_team_scope(driver, driver.team_id)


def _identity(role: Role, *, team_id: UUID | None = None) -> CurrentIdentity:
    return CurrentIdentity(
        user_id=uuid4(),
        email=f"{role.value.lower()}@example.com",
        membership_id=uuid4(),
        team_id=team_id or uuid4(),
        team_name="Authorization Test Team",
        role=role,
    )
