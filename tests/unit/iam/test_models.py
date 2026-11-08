"""Unit contracts for IAM enums and SQLAlchemy metadata."""

from typing import cast

from sqlalchemy import (
    CheckConstraint,
    DefaultClause,
    Enum,
    ForeignKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)

from raceops.db.base import Base
from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.models import Team, TeamMembership, User


def test_identity_enums_have_stable_values() -> None:
    assert [status.value for status in IdentityStatus] == ["ACTIVE", "INACTIVE"]
    assert [role.value for role in Role] == [
        "ADMINISTRATOR",
        "TEAM_MANAGER",
        "ENGINEER",
        "MECHANIC",
        "DRIVER",
    ]


def test_identity_tables_are_registered_in_shared_metadata() -> None:
    assert {"teams", "users", "team_memberships"} <= set(Base.metadata.tables)
    assert Team.__table__ is Base.metadata.tables["teams"]
    assert User.__table__ is Base.metadata.tables["users"]
    assert TeamMembership.__table__ is Base.metadata.tables["team_memberships"]


def test_identity_columns_use_expected_types_and_defaults() -> None:
    team_table = cast(Table, Team.__table__)
    user_table = cast(Table, User.__table__)
    membership_table = cast(Table, TeamMembership.__table__)
    team_status = team_table.c.status
    user_status = user_table.c.status
    membership_status = membership_table.c.status
    membership_role = membership_table.c.role

    assert isinstance(team_status.type, Enum)
    assert team_status.type.enum_class is IdentityStatus
    assert cast(Enum, user_status.type).enum_class is IdentityStatus
    assert cast(Enum, membership_status.type).enum_class is IdentityStatus
    assert cast(Enum, membership_role.type).enum_class is Role
    assert isinstance(team_status.server_default, DefaultClause)
    assert str(team_status.server_default.arg) == "ACTIVE"
    assert cast(String, user_table.c.email.type).length == 254
    assert cast(String, user_table.c.password_hash.type).length == 512


def test_identity_constraints_preserve_normalization_and_membership_uniqueness() -> (
    None
):
    user_table = cast(Table, User.__table__)
    membership_table = cast(Table, TeamMembership.__table__)
    user_constraint_names = {
        constraint.name
        for constraint in user_table.constraints
        if isinstance(constraint, (CheckConstraint, UniqueConstraint))
    }
    membership_constraint_names = {
        constraint.name
        for constraint in membership_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert user_constraint_names == {
        "ck_users_email_normalized",
        "ck_users_password_hash_not_blank",
        "uq_users_email",
    }
    assert membership_constraint_names == {"uq_team_memberships_user_id"}
    assert {index.name for index in membership_table.indexes} == {
        "ix_team_memberships_team_id"
    }


def test_membership_foreign_keys_restrict_historical_deletion() -> None:
    membership_table = cast(Table, TeamMembership.__table__)
    foreign_keys = {
        tuple(constraint.column_keys): constraint
        for constraint in membership_table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }

    assert foreign_keys[("user_id",)].ondelete == "RESTRICT"
    assert foreign_keys[("team_id",)].ondelete == "RESTRICT"
