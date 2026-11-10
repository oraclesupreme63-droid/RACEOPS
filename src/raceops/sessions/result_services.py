"""Transactional services for canonical Lap and optional Sector results."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isqrt
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.enums import (
    LapClassification,
    LapSource,
    ResultsStatus,
    SectorStatus,
)
from raceops.sessions.errors import (
    LapNumberConflictError,
    ResultsLockedError,
    SectorOrderConflictError,
)
from raceops.sessions.models import Lap, RaceSession, Sector
from raceops.sessions.result_schemas import SectorCreateRequest
from raceops.sessions.services import get_race_session


@dataclass(frozen=True, slots=True)
class LapMetrics:
    """Integer microsecond metrics over eligible Laps only."""

    total_laps: int
    eligible_laps: int
    excluded_laps: int
    best_lap_id: UUID | None
    best_lap_us: int | None
    average_lap_us: int | None
    consistency_us: int | None


def create_lap(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    lap_number: int,
    duration_us: int,
    source: LapSource,
    classification: LapClassification,
    sectors: Sequence[SectorCreateRequest],
) -> Lap:
    """Create a Lap and its initial Sectors atomically while results are open."""
    _require_open_results_for_update(session, actor.team_id, session_id)
    lap = Lap(
        team_id=actor.team_id,
        session_id=session_id,
        lap_number=lap_number,
        duration_us=duration_us,
        source=source,
        classification=classification,
    )
    try:
        session.add(lap)
        session.flush()
        session.add_all(
            [
                Sector(
                    team_id=actor.team_id,
                    lap_id=lap.lap_id,
                    sector_order=item.sector_order,
                    duration_us=item.duration_us,
                    status=item.status,
                )
                for item in sectors
            ]
        )
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise LapNumberConflictError from error
    session.refresh(lap)
    return lap


def list_laps(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
    *,
    classification: LapClassification | None,
    source: LapSource | None,
    limit: int,
    offset: int,
) -> tuple[list[Lap], int]:
    """List authorized Laps in stable numerical order."""
    get_race_session(session, actor, session_id)
    filters = [Lap.team_id == actor.team_id, Lap.session_id == session_id]
    if classification is not None:
        filters.append(Lap.classification == classification)
    if source is not None:
        filters.append(Lap.source == source)
    total = session.scalar(select(func.count()).select_from(Lap).where(*filters))
    statement = (
        select(Lap)
        .where(*filters)
        .order_by(Lap.lap_number, Lap.lap_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_lap(session: Session, actor: CurrentIdentity, lap_id: UUID) -> Lap:
    """Read one Lap without exposing cross-Team or unrelated Driver data."""
    lap = session.scalar(
        select(Lap).where(Lap.lap_id == lap_id, Lap.team_id == actor.team_id)
    )
    if lap is None:
        raise ResourceNotFoundError
    get_race_session(session, actor, lap.session_id)
    return lap


def update_lap(
    session: Session,
    actor: CurrentIdentity,
    lap_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Lap:
    """Update a Lap after serializing against the Session results lock."""
    existing = _find_lap(session, actor.team_id, lap_id)
    _require_open_results_for_update(session, actor.team_id, existing.session_id)
    lap = session.scalar(
        select(Lap)
        .where(Lap.lap_id == lap_id, Lap.team_id == actor.team_id)
        .with_for_update()
    )
    if lap is None:
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(lap, field, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise LapNumberConflictError from error
    session.refresh(lap)
    return lap


def create_sector(
    session: Session,
    actor: CurrentIdentity,
    lap_id: UUID,
    *,
    sector_order: int,
    duration_us: int,
    status: SectorStatus,
) -> Sector:
    """Append one optional Sector while the parent results remain open."""
    lap = _find_lap(session, actor.team_id, lap_id)
    _require_open_results_for_update(session, actor.team_id, lap.session_id)
    sector = Sector(
        team_id=actor.team_id,
        lap_id=lap_id,
        sector_order=sector_order,
        duration_us=duration_us,
        status=status,
    )
    session.add(sector)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise SectorOrderConflictError from error
    session.refresh(sector)
    return sector


def list_sectors(
    session: Session,
    actor: CurrentIdentity,
    lap_id: UUID,
) -> list[Sector]:
    """List authorized Sectors in their explicit variable order."""
    get_lap(session, actor, lap_id)
    return list(
        session.scalars(
            select(Sector)
            .where(Sector.lap_id == lap_id, Sector.team_id == actor.team_id)
            .order_by(Sector.sector_order, Sector.sector_id)
        )
    )


def get_sector(
    session: Session,
    actor: CurrentIdentity,
    sector_id: UUID,
) -> Sector:
    """Read one Sector through its authorized parent Lap."""
    sector = _find_sector(session, actor.team_id, sector_id)
    get_lap(session, actor, sector.lap_id)
    return sector


def update_sector(
    session: Session,
    actor: CurrentIdentity,
    sector_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Sector:
    """Update one Sector after serializing against the results lock."""
    existing = _find_sector(session, actor.team_id, sector_id)
    lap = _find_lap(session, actor.team_id, existing.lap_id)
    _require_open_results_for_update(session, actor.team_id, lap.session_id)
    sector = session.scalar(
        select(Sector)
        .where(
            Sector.sector_id == sector_id,
            Sector.team_id == actor.team_id,
        )
        .with_for_update()
    )
    if sector is None:
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(sector, field, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise SectorOrderConflictError from error
    session.refresh(sector)
    return sector


def get_results_summary(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
) -> LapMetrics:
    """Calculate simple metrics for an authorized Session."""
    get_race_session(session, actor, session_id)
    laps = list(
        session.scalars(
            select(Lap)
            .where(Lap.team_id == actor.team_id, Lap.session_id == session_id)
            .order_by(Lap.lap_number, Lap.lap_id)
        )
    )
    return calculate_lap_metrics(laps)


def calculate_lap_metrics(laps: Sequence[Lap]) -> LapMetrics:
    """Compute eligible best, rounded mean, and population deviation."""
    eligible = [lap for lap in laps if lap.is_eligible]
    total_laps = len(laps)
    if not eligible:
        return LapMetrics(total_laps, 0, total_laps, None, None, None, None)

    best = min(eligible, key=lambda lap: (lap.duration_us, lap.lap_number))
    durations = [lap.duration_us for lap in eligible]
    count = len(durations)
    total_duration = sum(durations)
    average_us = (total_duration + count // 2) // count
    consistency_us = _population_standard_deviation_us(durations)
    return LapMetrics(
        total_laps=total_laps,
        eligible_laps=count,
        excluded_laps=total_laps - count,
        best_lap_id=best.lap_id,
        best_lap_us=best.duration_us,
        average_lap_us=average_us,
        consistency_us=consistency_us,
    )


def _population_standard_deviation_us(durations: Sequence[int]) -> int | None:
    if len(durations) < 2:
        return None
    count = len(durations)
    squared_numerator = (
        count * sum(value * value for value in durations) - sum(durations) ** 2
    )
    floor_value = isqrt(squared_numerator) // count
    midpoint_squared = count * count * (2 * floor_value + 1) ** 2
    if 4 * squared_numerator >= midpoint_squared:
        return floor_value + 1
    return floor_value


def _require_open_results_for_update(
    session: Session,
    team_id: UUID,
    session_id: UUID,
) -> RaceSession:
    race_session = session.scalar(
        select(RaceSession)
        .where(
            RaceSession.session_id == session_id,
            RaceSession.team_id == team_id,
        )
        .with_for_update()
    )
    if race_session is None:
        raise ResourceNotFoundError
    if race_session.results_status is ResultsStatus.LOCKED:
        session.rollback()
        raise ResultsLockedError
    return race_session


def _find_lap(session: Session, team_id: UUID, lap_id: UUID) -> Lap:
    lap = session.scalar(
        select(Lap).where(Lap.lap_id == lap_id, Lap.team_id == team_id)
    )
    if lap is None:
        raise ResourceNotFoundError
    return lap


def _find_sector(session: Session, team_id: UUID, sector_id: UUID) -> Sector:
    sector = session.scalar(
        select(Sector).where(
            Sector.sector_id == sector_id,
            Sector.team_id == team_id,
        )
    )
    if sector is None:
        raise ResourceNotFoundError
    return sector
