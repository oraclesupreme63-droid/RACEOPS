"""Application services for team-scoped Driver management."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.iam.enums import IdentityStatus, Role
from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.iam.models import TeamMembership, User
from raceops.operations.enums import DriverStatus
from raceops.operations.errors import DriverUserConflictError
from raceops.operations.models import Driver


def create_driver(
    session: Session,
    actor: CurrentIdentity,
    *,
    display_name: str,
    user_id: UUID | None,
) -> Driver:
    """Create one Driver owned by the actor's selected Team."""
    if user_id is not None:
        _require_linkable_user(session, team_id=actor.team_id, user_id=user_id)
        _require_user_not_linked(session, team_id=actor.team_id, user_id=user_id)

    driver = Driver(
        team_id=actor.team_id,
        user_id=user_id,
        display_name=display_name,
    )
    session.add(driver)
    _commit_driver(session, driver)
    return driver


def list_drivers(
    session: Session,
    actor: CurrentIdentity,
    *,
    status: DriverStatus | None,
    limit: int,
    offset: int,
) -> tuple[list[Driver], int]:
    """List only Drivers visible inside the actor's authorized scope."""
    filters = [Driver.team_id == actor.team_id]
    if actor.role is Role.DRIVER:
        filters.append(Driver.user_id == actor.user_id)
    if status is not None:
        filters.append(Driver.status == status)

    total = session.scalar(select(func.count()).select_from(Driver).where(*filters))
    statement = (
        select(Driver)
        .where(*filters)
        .order_by(Driver.created_at, Driver.driver_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_driver(
    session: Session,
    actor: CurrentIdentity,
    driver_id: UUID,
) -> Driver:
    """Read one Driver, applying Team and Driver relationship filtering."""
    filters = [
        Driver.driver_id == driver_id,
        Driver.team_id == actor.team_id,
    ]
    if actor.role is Role.DRIVER:
        filters.append(Driver.user_id == actor.user_id)

    driver = session.scalar(select(Driver).where(*filters))
    if driver is None:
        raise ResourceNotFoundError
    return driver


def update_driver(
    session: Session,
    actor: CurrentIdentity,
    driver_id: UUID,
    *,
    change_display_name: bool,
    display_name: str | None,
    change_user_id: bool,
    user_id: UUID | None,
) -> Driver:
    """Update permitted Driver fields while preserving Team ownership."""
    driver = _get_driver_for_update(session, actor.team_id, driver_id)

    if change_display_name:
        if display_name is None:
            raise ValueError("display_name is required when changed")
        driver.display_name = display_name

    if change_user_id:
        if user_id is not None and user_id != driver.user_id:
            _require_linkable_user(session, team_id=actor.team_id, user_id=user_id)
            _require_user_not_linked(
                session,
                team_id=actor.team_id,
                user_id=user_id,
                excluding_driver_id=driver.driver_id,
            )
        driver.user_id = user_id

    _commit_driver(session, driver)
    return driver


def set_driver_status(
    session: Session,
    actor: CurrentIdentity,
    driver_id: UUID,
    status: DriverStatus,
) -> Driver:
    """Apply an explicit, idempotent Driver activation state."""
    driver = _get_driver_for_update(session, actor.team_id, driver_id)
    driver.status = status
    _commit_driver(session, driver)
    return driver


def _get_driver_for_update(
    session: Session,
    team_id: UUID,
    driver_id: UUID,
) -> Driver:
    driver = session.scalar(
        select(Driver)
        .where(
            Driver.driver_id == driver_id,
            Driver.team_id == team_id,
        )
        .with_for_update()
    )
    if driver is None:
        raise ResourceNotFoundError
    return driver


def _require_linkable_user(
    session: Session,
    *,
    team_id: UUID,
    user_id: UUID,
) -> None:
    membership_id = session.scalar(
        select(TeamMembership.membership_id)
        .join(User, TeamMembership.user_id == User.user_id)
        .where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
            TeamMembership.status == IdentityStatus.ACTIVE,
            User.status == IdentityStatus.ACTIVE,
        )
    )
    if membership_id is None:
        raise DriverUserConflictError


def _require_user_not_linked(
    session: Session,
    *,
    team_id: UUID,
    user_id: UUID,
    excluding_driver_id: UUID | None = None,
) -> None:
    filters = [
        Driver.team_id == team_id,
        Driver.user_id == user_id,
    ]
    if excluding_driver_id is not None:
        filters.append(Driver.driver_id != excluding_driver_id)
    if session.scalar(select(Driver.driver_id).where(*filters)) is not None:
        raise DriverUserConflictError


def _commit_driver(session: Session, driver: Driver) -> None:
    try:
        session.commit()
        session.refresh(driver)
    except IntegrityError as error:
        session.rollback()
        raise DriverUserConflictError from error
