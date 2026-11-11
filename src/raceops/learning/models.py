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
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raceops.db.base import Base, TimestampMixin
from raceops.iam.authorization import Visibility
from raceops.iam.enums import Role
from raceops.learning.enums import (
    ActionStatus,
    ActionType,
    AnalysisEvidenceType,
    CauseClassification,
    ConfidenceLevel,
    HypothesisStatus,
    TargetIntent,
)

VISIBILITY_LEVEL_ENUM_NAME: Final = "visibility_level"
ANALYSIS_EVIDENCE_TYPE_ENUM_NAME: Final = "analysis_evidence_type"
CAUSE_CLASSIFICATION_ENUM_NAME: Final = "cause_classification"
CONFIDENCE_LEVEL_ENUM_NAME: Final = "confidence_level"
HYPOTHESIS_STATUS_ENUM_NAME: Final = "hypothesis_status"
TARGET_INTENT_ENUM_NAME: Final = "target_intent"
ACTION_TYPE_ENUM_NAME: Final = "action_type"
ACTION_STATUS_ENUM_NAME: Final = "action_status"
TEAM_ROLE_ENUM_NAME: Final = "team_role"


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


class Priority(TimestampMixin, Base):
    """Concrete focus for one recipient and a known or future Session."""

    __tablename__ = "priorities"
    __table_args__ = (
        CheckConstraint(
            "description = btrim(description) "
            "AND char_length(description) BETWEEN 1 AND 2000",
            name="description_normalized",
        ),
        CheckConstraint(
            "recipient_role IN ('DRIVER', 'ENGINEER', 'MECHANIC')",
            name="recipient_role_allowed",
        ),
        CheckConstraint(
            "(is_main AND rank BETWEEN 1 AND 3) OR (NOT is_main AND rank IS NULL)",
            name="main_rank_consistent",
        ),
        CheckConstraint(
            "(target_intent = 'NEXT_SESSION' "
            "AND target_session_id IS NULL "
            "AND target_scope_id = source_session_id) "
            "OR (target_intent = 'SPECIFIC_SESSION' "
            "AND target_session_id IS NOT NULL "
            "AND target_scope_id = target_session_id)",
            name="target_consistent",
        ),
        CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name="role_restricted",
        ),
        ForeignKeyConstraint(
            ["source_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_priorities_source_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["target_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_priorities_target_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["hypothesis_id", "team_id"],
            ["hypotheses.hypothesis_id", "hypotheses.team_id"],
            name="fk_priorities_hypothesis_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("priority_id", "team_id", name="uq_priorities_priority_team"),
        Index("ix_priorities_team_source", "team_id", "source_session_id"),
        Index("ix_priorities_team_target", "team_id", "target_scope_id"),
        Index(
            "uq_priorities_main_rank_scope",
            "team_id",
            "target_scope_id",
            "recipient_role",
            "recipient_user_id",
            "rank",
            unique=True,
            postgresql_where=text("is_main"),
            postgresql_nulls_not_distinct=True,
        ),
    )

    priority_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    source_session_id: Mapped[UUID] = mapped_column(nullable=False)
    target_session_id: Mapped[UUID | None] = mapped_column(nullable=True)
    target_scope_id: Mapped[UUID] = mapped_column(nullable=False)
    hypothesis_id: Mapped[UUID | None] = mapped_column(nullable=True)
    target_intent: Mapped[TargetIntent] = mapped_column(
        Enum(TargetIntent, name=TARGET_INTENT_ENUM_NAME), nullable=False
    )
    recipient_role: Mapped[Role] = mapped_column(
        Enum(Role, name=TEAM_ROLE_ENUM_NAME), nullable=False
    )
    recipient_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_main: Mapped[bool] = mapped_column(nullable=False, default=True)
    rank: Mapped[int | None] = mapped_column(nullable=True)
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ROLE_RESTRICTED,
        server_default=Visibility.ROLE_RESTRICTED.value,
    )


class Action(TimestampMixin, Base):
    """Assigned work whose execution state never implies its outcome."""

    __tablename__ = "actions"
    __table_args__ = (
        CheckConstraint(
            "assignee_role IN ('DRIVER', 'ENGINEER', 'MECHANIC')",
            name="assignee_role_allowed",
        ),
        CheckConstraint(
            "(target_intent = 'NEXT_SESSION' "
            "AND target_session_id IS NULL "
            "AND target_scope_id = source_session_id) "
            "OR (target_intent = 'SPECIFIC_SESSION' "
            "AND target_session_id IS NOT NULL "
            "AND target_scope_id = target_session_id)",
            name="target_consistent",
        ),
        CheckConstraint(
            "hypothesis_id IS NOT NULL OR priority_id IS NOT NULL "
            "OR public_summary IS NOT NULL OR confidential_detail IS NOT NULL",
            name="has_motivation",
        ),
        CheckConstraint(
            "public_summary IS NULL OR (public_summary = btrim(public_summary) "
            "AND char_length(public_summary) BETWEEN 1 AND 2000)",
            name="public_summary_normalized",
        ),
        CheckConstraint(
            "confidential_detail IS NULL OR "
            "(confidential_detail = btrim(confidential_detail) "
            "AND char_length(confidential_detail) BETWEEN 1 AND 5000)",
            name="confidential_detail_normalized",
        ),
        CheckConstraint(
            "(status = 'CANCELLED' AND cancellation_reason IS NOT NULL) "
            "OR (status <> 'CANCELLED' AND cancellation_reason IS NULL)",
            name="cancellation_consistent",
        ),
        CheckConstraint(
            "cancellation_reason IS NULL OR "
            "(cancellation_reason = btrim(cancellation_reason) "
            "AND char_length(cancellation_reason) BETWEEN 1 AND 1000)",
            name="cancellation_reason_normalized",
        ),
        CheckConstraint(
            "visibility_level = 'ROLE_RESTRICTED'",
            name="role_restricted",
        ),
        ForeignKeyConstraint(
            ["source_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_actions_source_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["target_session_id", "team_id"],
            ["sessions.session_id", "sessions.team_id"],
            name="fk_actions_target_session_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["hypothesis_id", "team_id"],
            ["hypotheses.hypothesis_id", "hypotheses.team_id"],
            name="fk_actions_hypothesis_team",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["priority_id", "team_id"],
            ["priorities.priority_id", "priorities.team_id"],
            name="fk_actions_priority_team",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("action_id", "team_id", name="uq_actions_action_team"),
        Index("ix_actions_team_source", "team_id", "source_session_id"),
        Index("ix_actions_team_target", "team_id", "target_scope_id"),
        Index("ix_actions_team_assignee", "team_id", "assignee_user_id"),
    )

    action_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[UUID] = mapped_column(nullable=False)
    source_session_id: Mapped[UUID] = mapped_column(nullable=False)
    target_session_id: Mapped[UUID | None] = mapped_column(nullable=True)
    target_scope_id: Mapped[UUID] = mapped_column(nullable=False)
    hypothesis_id: Mapped[UUID | None] = mapped_column(nullable=True)
    priority_id: Mapped[UUID | None] = mapped_column(nullable=True)
    assignee_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True
    )
    assignee_role: Mapped[Role] = mapped_column(
        Enum(Role, name=TEAM_ROLE_ENUM_NAME), nullable=False
    )
    target_intent: Mapped[TargetIntent] = mapped_column(
        Enum(TargetIntent, name=TARGET_INTENT_ENUM_NAME), nullable=False
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name=ACTION_TYPE_ENUM_NAME), nullable=False
    )
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name=ACTION_STATUS_ENUM_NAME),
        nullable=False,
        default=ActionStatus.PROPOSED,
        server_default=ActionStatus.PROPOSED.value,
    )
    public_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    confidential_detail: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    visibility_level: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name=VISIBILITY_LEVEL_ENUM_NAME),
        nullable=False,
        default=Visibility.ROLE_RESTRICTED,
        server_default=Visibility.ROLE_RESTRICTED.value,
    )
