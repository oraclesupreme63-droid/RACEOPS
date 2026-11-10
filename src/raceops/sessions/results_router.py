"""HTTP boundary for Lap, Sector, and simple Session metrics."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ApiProblemError, ProblemDefinition, ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.sessions.enums import LapClassification, LapSource
from raceops.sessions.errors import (
    LapNumberConflictError,
    ResultsLockedError,
    SectorOrderConflictError,
)
from raceops.sessions.result_schemas import (
    LapCreateRequest,
    LapPageResponse,
    LapResponse,
    LapUpdateRequest,
    ResultsSummaryResponse,
    SectorCreateRequest,
    SectorPageResponse,
    SectorResponse,
    SectorUpdateRequest,
)
from raceops.sessions.result_services import (
    create_lap,
    create_sector,
    get_lap,
    get_results_summary,
    get_sector,
    list_laps,
    list_sectors,
    update_lap,
    update_sector,
)

router = APIRouter()
read_results = require_permission(Permission.READ_RESULTS)
write_results = require_permission(Permission.WRITE_RESULTS)

RESULTS_LOCKED_PROBLEM = ProblemDefinition(
    "results-locked",
    "Results are locked",
    "results_locked",
    "Locked Session results cannot be changed.",
)
LAP_NUMBER_CONFLICT_PROBLEM = ProblemDefinition(
    "lap-number-conflict",
    "Lap number conflict",
    "lap_number_conflict",
    "The lap number is already used in this Session.",
)
SECTOR_ORDER_CONFLICT_PROBLEM = ProblemDefinition(
    "sector-order-conflict",
    "Sector order conflict",
    "sector_order_conflict",
    "The sector order is already used in this Lap.",
)
RESULT_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Result not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/sessions/{session_id}/laps",
    tags=["results"],
    response_model=LapResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**RESULT_COMMON_RESPONSES, 409: {"model": ProblemDetails}},
)
def create_lap_endpoint(
    session_id: UUID,
    payload: LapCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_results)],
) -> LapResponse:
    """Create one canonical Lap, optionally with Sectors, as one transaction."""
    try:
        lap = create_lap(
            session,
            actor,
            session_id,
            lap_number=payload.lap_number,
            duration_us=payload.duration_us,
            source=payload.source,
            classification=payload.classification,
            sectors=payload.sectors,
        )
    except ResultsLockedError as error:
        raise _results_locked() from error
    except LapNumberConflictError as error:
        raise _lap_number_conflict() from error
    return LapResponse.from_model(lap)


@router.get(
    "/sessions/{session_id}/laps",
    tags=["results"],
    response_model=LapPageResponse,
    responses=RESULT_COMMON_RESPONSES,
)
def list_laps_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_results)],
    classification: LapClassification | None = None,
    source: LapSource | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LapPageResponse:
    """List authorized Laps with explicit source and classification filters."""
    laps, total = list_laps(
        session,
        actor,
        session_id,
        classification=classification,
        source=source,
        limit=limit,
        offset=offset,
    )
    return LapPageResponse(
        items=[LapResponse.from_model(lap) for lap in laps],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/sessions/{session_id}/results-summary",
    tags=["results"],
    response_model=ResultsSummaryResponse,
    responses=RESULT_COMMON_RESPONSES,
)
def results_summary_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_results)],
) -> ResultsSummaryResponse:
    """Return reproducible metrics over VALID Laps only."""
    metrics = get_results_summary(session, actor, session_id)
    return ResultsSummaryResponse(
        session_id=session_id,
        total_laps=metrics.total_laps,
        eligible_laps=metrics.eligible_laps,
        excluded_laps=metrics.excluded_laps,
        best_lap_id=metrics.best_lap_id,
        best_lap_us=metrics.best_lap_us,
        average_lap_us=metrics.average_lap_us,
        consistency_us=metrics.consistency_us,
    )


@router.get(
    "/laps/{lap_id}",
    tags=["results"],
    response_model=LapResponse,
    responses=RESULT_COMMON_RESPONSES,
)
def get_lap_endpoint(
    lap_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_results)],
) -> LapResponse:
    """Read one authorized Lap."""
    return LapResponse.from_model(get_lap(session, actor, lap_id))


@router.patch(
    "/laps/{lap_id}",
    tags=["results"],
    response_model=LapResponse,
    responses={**RESULT_COMMON_RESPONSES, 409: {"model": ProblemDetails}},
)
def update_lap_endpoint(
    lap_id: UUID,
    payload: LapUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_results)],
) -> LapResponse:
    """Change timing metadata only while parent Session results remain open."""
    try:
        lap = update_lap(
            session,
            actor,
            lap_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except ResultsLockedError as error:
        raise _results_locked() from error
    except LapNumberConflictError as error:
        raise _lap_number_conflict() from error
    return LapResponse.from_model(lap)


@router.post(
    "/laps/{lap_id}/sectors",
    tags=["results"],
    response_model=SectorResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**RESULT_COMMON_RESPONSES, 409: {"model": ProblemDetails}},
)
def create_sector_endpoint(
    lap_id: UUID,
    payload: SectorCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_results)],
) -> SectorResponse:
    """Add one optional ordered Sector to an existing Lap."""
    try:
        sector = create_sector(
            session,
            actor,
            lap_id,
            sector_order=payload.sector_order,
            duration_us=payload.duration_us,
            status=payload.status,
        )
    except ResultsLockedError as error:
        raise _results_locked() from error
    except SectorOrderConflictError as error:
        raise _sector_order_conflict() from error
    return SectorResponse.from_model(sector)


@router.get(
    "/laps/{lap_id}/sectors",
    tags=["results"],
    response_model=SectorPageResponse,
    responses=RESULT_COMMON_RESPONSES,
)
def list_sectors_endpoint(
    lap_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_results)],
) -> SectorPageResponse:
    """List every optional Sector for one authorized Lap."""
    sectors = list_sectors(session, actor, lap_id)
    return SectorPageResponse(
        items=[SectorResponse.from_model(sector) for sector in sectors],
        total=len(sectors),
    )


@router.get(
    "/sectors/{sector_id}",
    tags=["results"],
    response_model=SectorResponse,
    responses=RESULT_COMMON_RESPONSES,
)
def get_sector_endpoint(
    sector_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_results)],
) -> SectorResponse:
    """Read one authorized Sector."""
    return SectorResponse.from_model(get_sector(session, actor, sector_id))


@router.patch(
    "/sectors/{sector_id}",
    tags=["results"],
    response_model=SectorResponse,
    responses={**RESULT_COMMON_RESPONSES, 409: {"model": ProblemDetails}},
)
def update_sector_endpoint(
    sector_id: UUID,
    payload: SectorUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_results)],
) -> SectorResponse:
    """Change one Sector only while parent Session results remain open."""
    try:
        sector = update_sector(
            session,
            actor,
            sector_id,
            changes=payload.model_dump(exclude_unset=True),
        )
    except ResultsLockedError as error:
        raise _results_locked() from error
    except SectorOrderConflictError as error:
        raise _sector_order_conflict() from error
    return SectorResponse.from_model(sector)


def _results_locked() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=RESULTS_LOCKED_PROBLEM)


def _lap_number_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=LAP_NUMBER_CONFLICT_PROBLEM)


def _sector_order_conflict() -> ApiProblemError:
    return ApiProblemError(status_code=409, definition=SECTOR_ORDER_CONFLICT_PROBLEM)
