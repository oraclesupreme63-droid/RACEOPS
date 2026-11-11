"""Persistence models for evidence in the Session learning loop."""

from typing import Final
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raceops.db.base import Base, TimestampMixin
from raceops.iam.authorization import Visibility
from raceops.learning.enums import (
    AnalysisEvidenceType,
    CauseClassification,
    ConfidenceLevel,
    HypothesisStatus,
)

VISIBILITY_LEVEL_ENUM_NAME: Final = "visibility_level"
ANALYSIS_EVIDENCE_TYPE_ENUM_NAME: Final = "analysis_evidence_type"
CAUSE_CLASSIFICATION_ENUM_NAME: Final = "cause_classification"
CONFIDENCE_LEVEL_ENUM_NAME: Final = "confidence_level"
HYPOTHESIS_STATUS_ENUM_NAME: Final = "hypothesis_status"


class Observation(TimestampMixin, Base):
    """A recorded fact, symptom, or behavior; never a confirmed cause."""

    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint(
            "session_id IS NOT NULL OR vehicle_id IS NOT NULL",
            name="has_session_or_vehicle",
        ),
        CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name="description_normalized",
        ),
        CheckConstraint(
            "category IS NULL OR (category = btrim(category) "
            "AND char_length(category) BETWEEN 1 AND 80)",
            name="category_normalized",
        ),
        ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_observations_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["vehicle_id", "team_id"],
            ["vehicles.vehicle_id", "vehicles.team_id"],
            name="fk_observations_vehicle_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "observation_id", "team_id", name="uq_observations_observation_team"
        ),
        Index("ix_observations_team_session", "team_id", "session_id"),
        Index("ix_observations_team_vehicle", "team_id", "vehicle_id"),
    )

    observation_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[UUID | None] = mapped_column(nullable=True)
    vehicle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    author_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ROLE_RESTRICTED,
        server_default=Visibility.ROLE_RESTRICTED.value,
    )


class SessionAnalysis(TimestampMixin, Base):
    """Engineering reasoning with a separately shareable summary."""

    __tablename__ = "session_analyses"
    __table_args__ = (
        CheckConstraint(
            "technical_detail = btrim(technical_detail) "
            "AND char_length(technical_detail) BETWEEN 1 AND 5000",
            name="technical_detail_normalized",
        ),
        CheckConstraint(
            "authorized_summary IS NULL OR "
            "(authorized_summary = btrim(authorized_summary) "
            "AND char_length(authorized_summary) BETWEEN 1 AND 2000)",
            name="authorized_summary_normalized",
        ),
        CheckConstraint(
            "visibility_level = 'ENGINEERING_CONFIDENTIAL'",
            name="engineering_confidential",
        ),
        ForeignKeyConstraint(
            ["session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_session_analyses_session_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "analysis_id", "team_id", name="uq_session_analyses_analysis_team"
        ),
        Index("ix_session_analyses_team_session", "team_id", "session_id"),
    )

    analysis_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.team_id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[UUID] = mapped_column(nullable=False)
    author_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    authorized_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    technical_detail: Mapped[str] = mapped_column(String(5000), nullable=False)
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ENGINEERING_CONFIDENTIAL,
        server_default=Visibility.ENGINEERING_CONFIDENTIAL.value,
    )
    evidence_refs: Mapped[list["AnalysisEvidenceReference"]] = relationship(
        back_populates="analysis",
        lazy="selectin",
        order_by=(
            "AnalysisEvidenceReference.evidence_type, "
            "AnalysisEvidenceReference.reference_id"
        ),
    )


class AnalysisEvidenceReference(TimestampMixin, Base):
    """Validated pointer to evidence that already belongs to the Session."""

    __tablename__ = "analysis_evidence_references"
    __table_args__ = (
        ForeignKeyConstraint(
            ["analysis_id", "team_id"],
            ["session_analyses.analysis_id", "session_analyses.team_id"],
            name="fk_analysis_evidence_analysis_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "analysis_id",
            "evidence_type",
            "reference_id",
            name="uq_analysis_evidence_reference",
        ),
        Index("ix_analysis_evidence_team_analysis", "team_id", "analysis_id"),
    )

    evidence_reference_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    analysis_id: Mapped[UUID] = mapped_column(nullable=False)
    evidence_type: Mapped[AnalysisEvidenceType] = mapped_column(
        Enum(AnalysisEvidenceType, name=ANALYSIS_EVIDENCE_TYPE_ENUM_NAME),
        nullable=False,
    )
    reference_id: Mapped[UUID] = mapped_column(nullable=False)
    analysis: Mapped[SessionAnalysis] = relationship(back_populates="evidence_refs")


class Hypothesis(TimestampMixin, Base):
    """Uncertain explanation proposed from one Session analysis."""

    __tablename__ = "hypotheses"
    __table_args__ = (
        CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name="description_normalized",
        ),
        CheckConstraint(
            "visibility_level = 'ENGINEERING_CONFIDENTIAL'",
            name="engineering_confidential",
        ),
        ForeignKeyConstraint(
            ["analysis_id", "team_id"],
            ["session_analyses.analysis_id", "session_analyses.team_id"],
            name="fk_hypotheses_analysis_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "hypothesis_id", "team_id", name="uq_hypotheses_hypothesis_team"
        ),
        Index("ix_hypotheses_team_analysis", "team_id", "analysis_id"),
    )

    hypothesis_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    analysis_id: Mapped[UUID] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    cause_classification: Mapped[CauseClassification] = mapped_column(
        Enum(CauseClassification, name=CAUSE_CLASSIFICATION_ENUM_NAME),
        nullable=False,
    )
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        Enum(ConfidenceLevel, name=CONFIDENCE_LEVEL_ENUM_NAME), nullable=False
    )
    status: Mapped[HypothesisStatus] = mapped_column(
        Enum(HypothesisStatus, name=HYPOTHESIS_STATUS_ENUM_NAME),
        nullable=False,
        default=HypothesisStatus.PROPOSED,
        server_default=HypothesisStatus.PROPOSED.value,
    )
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ENGINEERING_CONFIDENTIAL,
        server_default=Visibility.ENGINEERING_CONFIDENTIAL.value,
    )
