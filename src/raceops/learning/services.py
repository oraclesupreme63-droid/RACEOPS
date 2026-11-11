"""Transactional services for visible, non-causal Observations."""

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import and_, exists, false, func, or_, select, true
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.iam.errors import InsufficientPermissionsError, ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.learning.enums import (
    AnalysisEvidenceType,
    CauseClassification,
    ConfidenceLevel,
)
from raceops.learning.models import (
    AnalysisEvidenceReference,
    Hypothesis,
    Observation,
    SessionAnalysis,
)
from raceops.operations.models import Driver
from raceops.operations.vehicles import get_vehicle
from raceops.sessions.models import (
    ConditionSnapshot,
    DriverFeedback,
    Lap,
    RaceSession,
    Sector,
)
from raceops.sessions.services import get_race_session


def create_observation(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
    description: str,
    category: str | None,
    visibility_level: Visibility,
) -> Observation:
    """Create evidence after validating context and confidentiality authority."""
    _validate_visibility_writer(actor, visibility_level)
    _require_targets(session, actor, session_id=session_id, vehicle_id=vehicle_id)
    observation = Observation(
        team_id=actor.team_id,
        session_id=session_id,
        vehicle_id=vehicle_id,
        author_user_id=actor.user_id,
        description=description,
        category=category,
        visibility_level=visibility_level,
    )
    session.add(observation)
    session.commit()
    session.refresh(observation)
    return observation


def list_observations(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Observation], int]:
    """List only records visible to the actor before counting and paging."""
    filters: list[ColumnElement[bool]] = [
        Observation.team_id == actor.team_id,
        _observation_visibility_filter(actor),
    ]
    if session_id is not None:
        filters.append(Observation.session_id == session_id)
    if vehicle_id is not None:
        filters.append(Observation.vehicle_id == vehicle_id)
    total = session.scalar(
        select(func.count()).select_from(Observation).where(*filters)
    )
    statement = (
        select(Observation)
        .where(*filters)
        .order_by(Observation.created_at, Observation.observation_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_observation(
    session: Session,
    actor: CurrentIdentity,
    observation_id: UUID,
) -> Observation:
    """Read one visible record without disclosing why another is hidden."""
    observation = session.scalar(
        select(Observation).where(
            Observation.observation_id == observation_id,
            Observation.team_id == actor.team_id,
            _observation_visibility_filter(actor),
        )
    )
    if observation is None:
        raise ResourceNotFoundError
    return observation


def update_observation(
    session: Session,
    actor: CurrentIdentity,
    observation_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Observation:
    """Update visible evidence text without changing context or visibility."""
    observation = session.scalar(
        select(Observation)
        .where(
            Observation.observation_id == observation_id,
            Observation.team_id == actor.team_id,
            _observation_visibility_filter(actor),
        )
        .with_for_update()
    )
    if observation is None:
        raise ResourceNotFoundError
    for field, value in changes.items():
        setattr(observation, field, value)
    session.commit()
    session.refresh(observation)
    return observation


def _validate_visibility_writer(
    actor: CurrentIdentity,
    visibility_level: Visibility,
) -> None:
    if (
        visibility_level is Visibility.ENGINEERING_CONFIDENTIAL
        and actor.role is not Role.ENGINEER
    ):
        raise InsufficientPermissionsError


def _require_targets(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID | None,
    vehicle_id: UUID | None,
) -> None:
    if session_id is not None:
        get_race_session(session, actor, session_id)
    if vehicle_id is not None:
        get_vehicle(session, actor, vehicle_id)


def _observation_visibility_filter(actor: CurrentIdentity) -> ColumnElement[bool]:
    if actor.role is Role.ENGINEER:
        return true()
    if actor.role in {Role.TEAM_MANAGER, Role.MECHANIC}:
        return Observation.visibility_level.in_(
            (Visibility.TEAM, Visibility.ROLE_RESTRICTED)
        )
    if actor.role is Role.ADMINISTRATOR:
        return Observation.visibility_level == Visibility.TEAM
    if actor.role is Role.DRIVER:
        return and_(
            Observation.visibility_level == Visibility.TEAM,
            _driver_observation_relationship(actor),
        )
    return false()


def _driver_observation_relationship(actor: CurrentIdentity) -> ColumnElement[bool]:
    return exists().where(
        Driver.team_id == actor.team_id,
        Driver.user_id == actor.user_id,
        RaceSession.team_id == actor.team_id,
        RaceSession.driver_id == Driver.driver_id,
        or_(
            and_(
                Observation.session_id.is_not(None),
                RaceSession.session_id == Observation.session_id,
            ),
            and_(
                Observation.session_id.is_(None),
                Observation.vehicle_id.is_not(None),
                RaceSession.vehicle_id == Observation.vehicle_id,
            ),
        ),
    )


def create_session_analysis(
    session: Session,
    actor: CurrentIdentity,
    *,
    session_id: UUID,
    technical_detail: str,
    authorized_summary: str | None,
    evidence: list[tuple[AnalysisEvidenceType, UUID]],
) -> SessionAnalysis:
    """Persist confidential reasoning only after validating every evidence link."""
    race_session = get_race_session(session, actor, session_id)
    for evidence_type, reference_id in evidence:
        _require_session_evidence(
            session,
            actor,
            race_session,
            evidence_type=evidence_type,
            reference_id=reference_id,
        )
    analysis = SessionAnalysis(
        team_id=actor.team_id,
        session_id=session_id,
        author_user_id=actor.user_id,
        authorized_summary=authorized_summary,
        technical_detail=technical_detail,
    )
    analysis.evidence_refs = [
        AnalysisEvidenceReference(
            team_id=actor.team_id,
            evidence_type=evidence_type,
            reference_id=reference_id,
        )
        for evidence_type, reference_id in evidence
    ]
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def list_session_analyses(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
) -> list[SessionAnalysis]:
    """List complete analyses for Engineering after checking Session scope."""
    get_race_session(session, actor, session_id)
    statement = (
        select(SessionAnalysis)
        .where(
            SessionAnalysis.team_id == actor.team_id,
            SessionAnalysis.session_id == session_id,
        )
        .order_by(SessionAnalysis.created_at, SessionAnalysis.analysis_id)
    )
    return list(session.scalars(statement))


def get_session_analysis(
    session: Session,
    actor: CurrentIdentity,
    analysis_id: UUID,
    *,
    for_update: bool = False,
) -> SessionAnalysis:
    """Resolve one same-Team analysis without disclosing other records."""
    statement = select(SessionAnalysis).where(
        SessionAnalysis.analysis_id == analysis_id,
        SessionAnalysis.team_id == actor.team_id,
    )
    if for_update:
        statement = statement.with_for_update()
    analysis = session.scalar(statement)
    if analysis is None:
        raise ResourceNotFoundError
    return analysis


def update_session_analysis(
    session: Session,
    actor: CurrentIdentity,
    analysis_id: UUID,
    *,
    changes: Mapping[str, object],
) -> SessionAnalysis:
    """Revise technical reasoning or its separate authorized summary."""
    analysis = get_session_analysis(session, actor, analysis_id, for_update=True)
    for field, value in changes.items():
        setattr(analysis, field, value)
    session.commit()
    session.refresh(analysis)
    return analysis


def list_authorized_analysis_summaries(
    session: Session,
    actor: CurrentIdentity,
    session_id: UUID,
) -> list[SessionAnalysis]:
    """Return only deliberately shared text, never hidden records or counts."""
    get_race_session(session, actor, session_id)
    statement = (
        select(SessionAnalysis)
        .where(
            SessionAnalysis.team_id == actor.team_id,
            SessionAnalysis.session_id == session_id,
            SessionAnalysis.authorized_summary.is_not(None),
        )
        .order_by(SessionAnalysis.created_at, SessionAnalysis.analysis_id)
    )
    return list(session.scalars(statement))


def create_hypothesis(
    session: Session,
    actor: CurrentIdentity,
    analysis_id: UUID,
    *,
    description: str,
    cause_classification: CauseClassification,
    confidence: ConfidenceLevel,
) -> Hypothesis:
    """Create one Engineering-confidential hypothesis in PROPOSED state."""
    analysis = get_session_analysis(session, actor, analysis_id)
    hypothesis = Hypothesis(
        team_id=actor.team_id,
        analysis_id=analysis.analysis_id,
        description=description,
        cause_classification=cause_classification,
        confidence=confidence,
    )
    session.add(hypothesis)
    session.commit()
    session.refresh(hypothesis)
    return hypothesis


def list_hypotheses(
    session: Session,
    actor: CurrentIdentity,
    analysis_id: UUID,
) -> list[Hypothesis]:
    """List technical hypotheses only after resolving their parent analysis."""
    get_session_analysis(session, actor, analysis_id)
    statement = (
        select(Hypothesis)
        .where(
            Hypothesis.team_id == actor.team_id,
            Hypothesis.analysis_id == analysis_id,
        )
        .order_by(Hypothesis.created_at, Hypothesis.hypothesis_id)
    )
    return list(session.scalars(statement))


def get_hypothesis(
    session: Session,
    actor: CurrentIdentity,
    hypothesis_id: UUID,
    *,
    for_update: bool = False,
) -> Hypothesis:
    """Resolve one Engineering hypothesis within the selected Team."""
    statement = select(Hypothesis).where(
        Hypothesis.hypothesis_id == hypothesis_id,
        Hypothesis.team_id == actor.team_id,
    )
    if for_update:
        statement = statement.with_for_update()
    hypothesis = session.scalar(statement)
    if hypothesis is None:
        raise ResourceNotFoundError
    return hypothesis


def update_hypothesis(
    session: Session,
    actor: CurrentIdentity,
    hypothesis_id: UUID,
    *,
    changes: Mapping[str, object],
) -> Hypothesis:
    """Revise a proposal without accepting an unsupported status transition."""
    hypothesis = get_hypothesis(session, actor, hypothesis_id, for_update=True)
    for field, value in changes.items():
        setattr(hypothesis, field, value)
    session.commit()
    session.refresh(hypothesis)
    return hypothesis


def _require_session_evidence(
    session: Session,
    actor: CurrentIdentity,
    race_session: RaceSession,
    *,
    evidence_type: AnalysisEvidenceType,
    reference_id: UUID,
) -> None:
    """Ensure a polymorphic reference is real and belongs to this Session."""
    if evidence_type is AnalysisEvidenceType.DRIVER_FEEDBACK:
        found = session.scalar(
            select(DriverFeedback.feedback_id).where(
                DriverFeedback.feedback_id == reference_id,
                DriverFeedback.team_id == actor.team_id,
                DriverFeedback.session_id == race_session.session_id,
            )
        )
    elif evidence_type is AnalysisEvidenceType.LAP:
        found = session.scalar(
            select(Lap.lap_id).where(
                Lap.lap_id == reference_id,
                Lap.team_id == actor.team_id,
                Lap.session_id == race_session.session_id,
            )
        )
    elif evidence_type is AnalysisEvidenceType.SECTOR:
        found = session.scalar(
            select(Sector.sector_id)
            .join(
                Lap,
                and_(
                    Lap.lap_id == Sector.lap_id,
                    Lap.team_id == Sector.team_id,
                ),
            )
            .where(
                Sector.sector_id == reference_id,
                Sector.team_id == actor.team_id,
                Lap.session_id == race_session.session_id,
            )
        )
    elif evidence_type is AnalysisEvidenceType.CONDITION:
        found = session.scalar(
            select(ConditionSnapshot.condition_id).where(
                ConditionSnapshot.condition_id == reference_id,
                ConditionSnapshot.team_id == actor.team_id,
                ConditionSnapshot.session_id == race_session.session_id,
            )
        )
    elif evidence_type is AnalysisEvidenceType.OBSERVATION:
        observation = session.scalar(
            select(Observation).where(
                Observation.observation_id == reference_id,
                Observation.team_id == actor.team_id,
            )
        )
        found = None
        if observation is not None:
            if observation.session_id is not None:
                if observation.session_id == race_session.session_id:
                    found = observation.observation_id
            elif observation.vehicle_id == race_session.vehicle_id:
                found = observation.observation_id
    else:
        found = None
    if found is None:
        raise ResourceNotFoundError
