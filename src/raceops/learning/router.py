"""HTTP boundary for technical Observations."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from raceops.api.dependencies import get_db_session, require_permission
from raceops.api.errors import ProblemDetails
from raceops.iam.authorization import Permission
from raceops.iam.identity import CurrentIdentity
from raceops.learning.schemas import (
    AuthorizedAnalysisSummaryResponse,
    HypothesisCreateRequest,
    HypothesisResponse,
    HypothesisUpdateRequest,
    ObservationCreateRequest,
    ObservationPageResponse,
    ObservationResponse,
    ObservationUpdateRequest,
    SessionAnalysisCreateRequest,
    SessionAnalysisResponse,
    SessionAnalysisUpdateRequest,
)
from raceops.learning.services import (
    create_hypothesis,
    create_observation,
    create_session_analysis,
    get_hypothesis,
    get_observation,
    get_session_analysis,
    list_authorized_analysis_summaries,
    list_hypotheses,
    list_observations,
    list_session_analyses,
    update_hypothesis,
    update_observation,
    update_session_analysis,
)

logger = logging.getLogger("raceops.learning")
router = APIRouter()

read_observations = require_permission(Permission.READ_OBSERVATIONS)
write_observations = require_permission(Permission.WRITE_OBSERVATIONS)
read_analysis_summaries = require_permission(Permission.READ_ANALYSIS_SUMMARIES)
write_analysis = require_permission(Permission.WRITE_ANALYSIS)

LEARNING_COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetails, "description": "Invalid access token."},
    403: {"model": ProblemDetails, "description": "Insufficient permission."},
    404: {"model": ProblemDetails, "description": "Resource not found."},
    422: {"model": ProblemDetails, "description": "Invalid request."},
}


@router.post(
    "/observations",
    tags=["observations"],
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses=LEARNING_COMMON_RESPONSES,
)
def create_observation_endpoint(
    payload: ObservationCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_observations)],
) -> ObservationResponse:
    """Record evidence without introducing any causal assertion."""
    observation = create_observation(
        session,
        actor,
        session_id=payload.session_id,
        vehicle_id=payload.vehicle_id,
        description=payload.description,
        category=payload.category,
        visibility_level=payload.visibility_level,
    )
    logger.info(
        "observation created",
        extra={
            "event": "observation.created",
            "observation_id": str(observation.observation_id),
            "team_id": str(actor.team_id),
            "visibility_level": observation.visibility_level.value,
        },
    )
    return ObservationResponse.from_model(observation)


@router.get(
    "/observations",
    tags=["observations"],
    response_model=ObservationPageResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def list_observations_endpoint(
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_observations)],
    session_id: UUID | None = None,
    vehicle_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ObservationPageResponse:
    """Return a page after visibility filtering and optional context filters."""
    observations, total = list_observations(
        session,
        actor,
        session_id=session_id,
        vehicle_id=vehicle_id,
        limit=limit,
        offset=offset,
    )
    return ObservationPageResponse(
        items=[ObservationResponse.from_model(item) for item in observations],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/observations/{observation_id}",
    tags=["observations"],
    response_model=ObservationResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def get_observation_endpoint(
    observation_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_observations)],
) -> ObservationResponse:
    """Read one Observation only when its visibility permits it."""
    return ObservationResponse.from_model(
        get_observation(session, actor, observation_id)
    )


@router.patch(
    "/observations/{observation_id}",
    tags=["observations"],
    response_model=ObservationResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def update_observation_endpoint(
    observation_id: UUID,
    payload: ObservationUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_observations)],
) -> ObservationResponse:
    """Correct visible evidence text without changing protected metadata."""
    observation = update_observation(
        session,
        actor,
        observation_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return ObservationResponse.from_model(observation)


@router.post(
    "/sessions/{session_id}/analyses",
    tags=["analysis"],
    response_model=SessionAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    responses=LEARNING_COMMON_RESPONSES,
)
def create_session_analysis_endpoint(
    session_id: UUID,
    payload: SessionAnalysisCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> SessionAnalysisResponse:
    """Create evidence-backed reasoning visible in full only to Engineering."""
    analysis = create_session_analysis(
        session,
        actor,
        session_id=session_id,
        technical_detail=payload.technical_detail,
        authorized_summary=payload.authorized_summary,
        evidence=[(item.evidence_type, item.reference_id) for item in payload.evidence],
    )
    logger.info(
        "session analysis created",
        extra={
            "event": "analysis.created",
            "analysis_id": str(analysis.analysis_id),
            "session_id": str(session_id),
            "team_id": str(actor.team_id),
        },
    )
    return SessionAnalysisResponse.from_model(analysis)


@router.get(
    "/sessions/{session_id}/analyses",
    tags=["analysis"],
    response_model=list[SessionAnalysisResponse],
    responses=LEARNING_COMMON_RESPONSES,
)
def list_session_analyses_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> list[SessionAnalysisResponse]:
    """List full technical analyses for Engineering only."""
    return [
        SessionAnalysisResponse.from_model(item)
        for item in list_session_analyses(session, actor, session_id)
    ]


@router.get(
    "/sessions/{session_id}/analysis-summaries",
    tags=["analysis"],
    response_model=list[AuthorizedAnalysisSummaryResponse],
    responses=LEARNING_COMMON_RESPONSES,
)
def list_authorized_analysis_summaries_endpoint(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(read_analysis_summaries)],
) -> list[AuthorizedAnalysisSummaryResponse]:
    """Expose only deliberately shared text, without identifiers or counts."""
    analyses = list_authorized_analysis_summaries(session, actor, session_id)
    return [
        AuthorizedAnalysisSummaryResponse(
            authorized_summary=item.authorized_summary,
            updated_at=item.updated_at,
        )
        for item in analyses
        if item.authorized_summary is not None
    ]


@router.get(
    "/analyses/{analysis_id}",
    tags=["analysis"],
    response_model=SessionAnalysisResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def get_session_analysis_endpoint(
    analysis_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> SessionAnalysisResponse:
    """Read one full analysis only with Engineering authority."""
    return SessionAnalysisResponse.from_model(
        get_session_analysis(session, actor, analysis_id)
    )


@router.patch(
    "/analyses/{analysis_id}",
    tags=["analysis"],
    response_model=SessionAnalysisResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def update_session_analysis_endpoint(
    analysis_id: UUID,
    payload: SessionAnalysisUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> SessionAnalysisResponse:
    """Revise confidential reasoning or its independent shared summary."""
    analysis = update_session_analysis(
        session,
        actor,
        analysis_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return SessionAnalysisResponse.from_model(analysis)


@router.post(
    "/analyses/{analysis_id}/hypotheses",
    tags=["analysis"],
    response_model=HypothesisResponse,
    status_code=status.HTTP_201_CREATED,
    responses=LEARNING_COMMON_RESPONSES,
)
def create_hypothesis_endpoint(
    analysis_id: UUID,
    payload: HypothesisCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> HypothesisResponse:
    """Propose a confidential cause without presenting it as confirmed."""
    hypothesis = create_hypothesis(
        session,
        actor,
        analysis_id,
        description=payload.description,
        cause_classification=payload.cause_classification,
        confidence=payload.confidence,
    )
    return HypothesisResponse.from_model(hypothesis)


@router.get(
    "/analyses/{analysis_id}/hypotheses",
    tags=["analysis"],
    response_model=list[HypothesisResponse],
    responses=LEARNING_COMMON_RESPONSES,
)
def list_hypotheses_endpoint(
    analysis_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> list[HypothesisResponse]:
    """List Engineering hypotheses for one analysis."""
    return [
        HypothesisResponse.from_model(item)
        for item in list_hypotheses(session, actor, analysis_id)
    ]


@router.get(
    "/hypotheses/{hypothesis_id}",
    tags=["analysis"],
    response_model=HypothesisResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def get_hypothesis_endpoint(
    hypothesis_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> HypothesisResponse:
    """Read one confidential hypothesis."""
    return HypothesisResponse.from_model(get_hypothesis(session, actor, hypothesis_id))


@router.patch(
    "/hypotheses/{hypothesis_id}",
    tags=["analysis"],
    response_model=HypothesisResponse,
    responses=LEARNING_COMMON_RESPONSES,
)
def update_hypothesis_endpoint(
    hypothesis_id: UUID,
    payload: HypothesisUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    actor: Annotated[CurrentIdentity, Depends(write_analysis)],
) -> HypothesisResponse:
    """Revise a proposal while its evaluation status remains server-controlled."""
    hypothesis = update_hypothesis(
        session,
        actor,
        hypothesis_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return HypothesisResponse.from_model(hypothesis)
