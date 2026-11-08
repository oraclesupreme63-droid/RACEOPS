"""SQLAlchemy persistence models owned by the IAM module."""

from __future__ import annotations

from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raceops.db.base import Base, TimestampMixin
from raceops.iam.enums import IdentityStatus, Role

IDENTITY_STATUS_ENUM_NAME: Final = "identity_status"
TEAM_ROLE_ENUM_NAME: Final = "team_role"


class Team(TimestampMixin, Base):
    """Ownership boundary for RaceOps operational resources."""

    __tablename__ = "teams"
    __table_args__ = (
        CheckConstraint(
            "char_length(btrim(name)) > 0",
            name="name_not_blank",
        ),
    )

    team_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[IdentityStatus] = mapped_column(
        Enum(IdentityStatus, name=IDENTITY_STATUS_ENUM_NAME),
        nullable=False,
        default=IdentityStatus.ACTIVE,
        server_default=IdentityStatus.ACTIVE.value,
    )

    memberships: Mapped[list[TeamMembership]] = relationship(
        back_populates="team",
        passive_deletes=True,
    )


class User(TimestampMixin, Base):
    """Global authenticatable identity, distinct from a Driver profile."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email = lower(btrim(email)) AND char_length(email) BETWEEN 3 AND 254",
            name="email_normalized",
        ),
        CheckConstraint(
            "char_length(btrim(password_hash)) > 0",
            name="password_hash_not_blank",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[IdentityStatus] = mapped_column(
        Enum(IdentityStatus, name=IDENTITY_STATUS_ENUM_NAME),
        nullable=False,
        default=IdentityStatus.ACTIVE,
        server_default=IdentityStatus.ACTIVE.value,
    )

    memberships: Mapped[list[TeamMembership]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )


class TeamMembership(TimestampMixin, Base):
    """A user's role and access state within exactly one team."""

    __tablename__ = "team_memberships"
    __table_args__ = (UniqueConstraint("user_id", "team_id"),)

    membership_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role: Mapped[Role] = mapped_column(
        Enum(Role, name=TEAM_ROLE_ENUM_NAME),
        nullable=False,
    )
    status: Mapped[IdentityStatus] = mapped_column(
        Enum(IdentityStatus, name=IDENTITY_STATUS_ENUM_NAME),
        nullable=False,
        default=IdentityStatus.ACTIVE,
        server_default=IdentityStatus.ACTIVE.value,
    )

    user: Mapped[User] = relationship(back_populates="memberships")
    team: Mapped[Team] = relationship(back_populates="memberships")
