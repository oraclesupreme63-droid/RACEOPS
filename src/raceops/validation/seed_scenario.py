"""Create local Phase 9 accounts and a frozen synthetic scenario."""

import argparse
import getpass
import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from raceops.core.config import Settings, get_settings
from raceops.core.logging import configure_logging
from raceops.db.session import build_engine, build_session_factory
from raceops.iam.credentials import hash_password
from raceops.iam.enums import Role
from raceops.iam.errors import PasswordPolicyError
from raceops.iam.models import Team, TeamMembership, User
from raceops.learning.models import Observation
from raceops.operations.enums import EventStatus
from raceops.operations.models import Driver, Event, Track, Vehicle
from raceops.sessions.enums import ResultsStatus, SessionStatus
from raceops.sessions.models import ConditionSnapshot, Lap, RaceSession, Sector
from raceops.validation.scenario import (
    SessionSeed,
    ValidationDatasetName,
    ValidationScenarioDefinition,
    load_validation_scenario,
)

logger = logging.getLogger("raceops.validation.seed")
_SCENARIO_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ROLE_LOCAL_PARTS = {
    Role.ADMINISTRATOR: "administrator",
    Role.TEAM_MANAGER: "team-manager",
    Role.ENGINEER: "engineer",
    Role.MECHANIC: "mechanic",
    Role.DRIVER: "driver",
}


class ValidationScenarioError(Exception):
    """Base error safe to report from the local operator command."""


class ValidationScenarioConflictError(ValidationScenarioError):
    """Raised when a scenario identifier already exists."""


@dataclass(frozen=True, slots=True)
class ScenarioAccount:
    """One local identity created for a validation Role."""

    role: Role
    email: str
    user_id: UUID
    membership_id: UUID


@dataclass(frozen=True, slots=True)
class ValidationScenarioResult:
    """Non-secret identifiers returned after an atomic seed."""

    version: str
    scenario_id: str
    team_id: UUID
    team_name: str
    source_session_id: UUID
    evaluation_session_id: UUID
    accounts: dict[Role, ScenarioAccount]


def seed_validation_scenario(
    session_factory: sessionmaker[Session],
    *,
    environment: str,
    scenario_id: str,
    password: str,
    definition: ValidationScenarioDefinition | None = None,
) -> ValidationScenarioResult:
    """Atomically create local-only identities and deliberately imperfect data."""
    if environment not in {"local", "test"}:
        raise ValidationScenarioError(
            "validation seeding is available only in local or test environments"
        )
    normalized_id = _normalize_scenario_id(scenario_id)
    scenario = definition or load_validation_scenario()
    account_emails = {
        role: f"{local_part}.{normalized_id}@raceops.local"
        for role, local_part in _ROLE_LOCAL_PARTS.items()
    }

    with session_factory() as session:
        existing_email = session.scalar(
            select(User.email).where(User.email.in_(account_emails.values())).limit(1)
        )
    if existing_email is not None:
        raise ValidationScenarioConflictError(
            f"scenario '{normalized_id}' already exists"
        )

    try:
        password_hash = hash_password(password)
    except PasswordPolicyError as error:
        raise ValidationScenarioError(str(error)) from error

    try:
        with session_factory() as session, session.begin():
            team = Team(name=f"{scenario.team_name} · {normalized_id}")
            session.add(team)
            session.flush()

            accounts = _create_accounts(
                session,
                team=team,
                emails=account_emails,
                password_hash=password_hash,
            )
            driver = Driver(
                team_id=team.team_id,
                user_id=accounts[Role.DRIVER].user_id,
                display_name=scenario.driver_name,
            )
            vehicle = Vehicle(
                team_id=team.team_id,
                identifier=scenario.vehicle_identifier,
            )
            track = Track(
                team_id=team.team_id,
                name=scenario.track_name,
                location=scenario.track_location,
            )
            session.add_all((driver, vehicle, track))
            session.flush()

            event = Event(
                team_id=team.team_id,
                track_id=track.track_id,
                name=scenario.event_name,
                starts_on=scenario.event_date,
                ends_on=scenario.event_end_date or scenario.event_date,
                description=scenario.event_description,
                status=EventStatus.COMPLETED,
            )
            session.add(event)
            session.flush()

            engineer_user_id = accounts[Role.ENGINEER].user_id
            source = _create_historical_session(
                session,
                team_id=team.team_id,
                event_id=event.event_id,
                driver_id=driver.driver_id,
                vehicle_id=vehicle.vehicle_id,
                locked_by_user_id=engineer_user_id,
                definition=scenario.source_session,
            )
            evaluation = _create_historical_session(
                session,
                team_id=team.team_id,
                event_id=event.event_id,
                driver_id=driver.driver_id,
                vehicle_id=vehicle.vehicle_id,
                locked_by_user_id=engineer_user_id,
                definition=scenario.evaluation_session,
            )
            session.add(
                Observation(
                    team_id=team.team_id,
                    session_id=source.session_id,
                    vehicle_id=vehicle.vehicle_id,
                    author_user_id=accounts[Role.MECHANIC].user_id,
                    description=scenario.seed_observation.description,
                    category=scenario.seed_observation.category,
                    visibility_level=scenario.seed_observation.visibility_level,
                )
            )
            session.flush()
            result = ValidationScenarioResult(
                version=scenario.version,
                scenario_id=normalized_id,
                team_id=team.team_id,
                team_name=team.name,
                source_session_id=source.session_id,
                evaluation_session_id=evaluation.session_id,
                accounts=accounts,
            )
    except IntegrityError as error:
        raise ValidationScenarioConflictError(
            f"scenario '{normalized_id}' conflicts with existing data"
        ) from error
    return result


def _create_accounts(
    session: Session,
    *,
    team: Team,
    emails: dict[Role, str],
    password_hash: str,
) -> dict[Role, ScenarioAccount]:
    accounts: dict[Role, ScenarioAccount] = {}
    for role in Role:
        user = User(email=emails[role], password_hash=password_hash)
        membership = TeamMembership(user=user, team=team, role=role)
        session.add(membership)
        session.flush()
        accounts[role] = ScenarioAccount(
            role=role,
            email=user.email,
            user_id=user.user_id,
            membership_id=membership.membership_id,
        )
    return accounts


def _create_historical_session(
    session: Session,
    *,
    team_id: UUID,
    event_id: UUID,
    driver_id: UUID,
    vehicle_id: UUID,
    locked_by_user_id: UUID,
    definition: SessionSeed,
) -> RaceSession:
    race_session = RaceSession(
        team_id=team_id,
        event_id=event_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        session_type=definition.session_type,
        scheduled_at=definition.scheduled_at,
        status=SessionStatus.COMPLETED,
        results_status=ResultsStatus.LOCKED,
        started_at=definition.started_at,
        ended_at=definition.ended_at,
        results_locked_by_user_id=locked_by_user_id,
        results_locked_at=definition.ended_at,
    )
    session.add(race_session)
    session.flush()
    conditions = definition.conditions
    session.add(
        ConditionSnapshot(
            team_id=team_id,
            session_id=race_session.session_id,
            ambient_temperature=conditions.ambient_temperature,
            ambient_temperature_unit=conditions.ambient_temperature_unit,
            track_temperature=conditions.track_temperature,
            track_temperature_unit=conditions.track_temperature_unit,
            weather=conditions.weather,
            track_condition=conditions.track_condition,
            source=conditions.source,
        )
    )
    for lap_definition in definition.laps:
        lap = Lap(
            team_id=team_id,
            session_id=race_session.session_id,
            lap_number=lap_definition.lap_number,
            duration_us=lap_definition.duration_us,
            source=lap_definition.source,
            classification=lap_definition.classification,
        )
        session.add(lap)
        session.flush()
        session.add_all(
            [
                Sector(
                    team_id=team_id,
                    lap_id=lap.lap_id,
                    sector_order=sector.sector_order,
                    duration_us=sector.duration_us,
                    status=sector.status,
                )
                for sector in lap_definition.sectors
            ]
        )
    return race_session


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the local operator command without accepting password arguments."""
    options = _build_parser().parse_args(arguments)
    settings = get_settings()
    configure_logging(level=settings.log_level, environment=settings.env)
    if settings.env == "production":
        logger.error(
            "validation seeding is disabled in production",
            extra={"event": "validation.seed_rejected"},
        )
        return 1

    try:
        password = _read_confirmed_password()
        result = _seed_from_settings(
            settings,
            options.scenario_id,
            password,
            dataset=options.dataset,
        )
    except ValidationScenarioError as error:
        logger.error(str(error), extra={"event": "validation.seed_rejected"})
        return 1
    except SQLAlchemyError:
        logger.exception(
            "validation scenario database operation failed",
            extra={"event": "validation.seed_failed"},
        )
        return 1

    print(_format_result(result))
    return 0


def _seed_from_settings(
    settings: Settings,
    scenario_id: str,
    password: str,
    *,
    dataset: ValidationDatasetName,
) -> ValidationScenarioResult:
    engine = build_engine(settings)
    try:
        return seed_validation_scenario(
            build_session_factory(engine),
            environment=settings.env,
            scenario_id=scenario_id,
            password=password,
            definition=load_validation_scenario(dataset),
        )
    finally:
        engine.dispose()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create local Role accounts and the frozen Phase 9 scenario."
    )
    parser.add_argument("--scenario-id", default="round-1")
    parser.add_argument(
        "--dataset",
        choices=("synthetic", "public-kristianstad-2025"),
        default="synthetic",
        help="Frozen dataset to create (default: synthetic).",
    )
    return parser


def _read_confirmed_password() -> str:
    password = getpass.getpass("Shared local validation password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValidationScenarioError("password confirmation does not match")
    return password


def _normalize_scenario_id(value: str) -> str:
    normalized = value.strip().lower()
    if (
        len(normalized) < 2
        or len(normalized) > 32
        or _SCENARIO_ID_PATTERN.fullmatch(normalized) is None
    ):
        raise ValidationScenarioError(
            "scenario id must use 2-32 lowercase letters, numbers or single hyphens"
        )
    return normalized


def _format_result(result: ValidationScenarioResult) -> str:
    lines = [
        "RaceOps validation scenario created",
        f"version: {result.version}",
        f"scenario: {result.scenario_id}",
        f"team: {result.team_name}",
        "accounts:",
    ]
    lines.extend(f"  {role.value}: {result.accounts[role].email}" for role in Role)
    lines.append("password: the shared value entered above was not printed")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
