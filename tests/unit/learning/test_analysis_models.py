"""Unit contracts for evidence-backed analyses and uncertain hypotheses."""

from typing import cast
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import Table

from raceops.db.base import Base
from raceops.iam.authorization import Visibility
from raceops.learning.enums import HypothesisStatus
from raceops.learning.models import Hypothesis, SessionAnalysis
from raceops.learning.schemas import (
    HypothesisCreateRequest,
    HypothesisUpdateRequest,
    SessionAnalysisCreateRequest,
    SessionAnalysisUpdateRequest,
)

REFERENCE_ID = UUID("b170451b-c54d-4365-b5d0-38f1d47dce4a")


def test_analysis_and_hypothesis_tables_preserve_confidentiality() -> None:
    analysis_table = cast(Table, SessionAnalysis.__table__)
    hypothesis_table = cast(Table, Hypothesis.__table__)
    analysis_constraints = {
        cast(str | None, constraint.name) for constraint in analysis_table.constraints
    }
    hypothesis_constraints = {
        cast(str | None, constraint.name) for constraint in hypothesis_table.constraints
    }

    assert Base.metadata.tables["session_analyses"] is analysis_table
    assert Base.metadata.tables["hypotheses"] is hypothesis_table
    assert "ck_session_analyses_engineering_confidential" in analysis_constraints
    assert "fk_session_analyses_session_team" in analysis_constraints
    assert "ck_hypotheses_engineering_confidential" in hypothesis_constraints
    assert "fk_hypotheses_analysis_team" in hypothesis_constraints


def test_analysis_requires_unique_evidence_and_normalizes_text() -> None:
    payload = SessionAnalysisCreateRequest.model_validate(
        {
            "technical_detail": "  Rear instability follows brake release.  ",
            "authorized_summary": "  Working to improve rear stability.  ",
            "evidence": [
                {"evidence_type": "OBSERVATION", "reference_id": REFERENCE_ID}
            ],
        }
    )

    assert payload.technical_detail == "Rear instability follows brake release."
    assert payload.authorized_summary == "Working to improve rear stability."
    assert "visibility_level" not in SessionAnalysisCreateRequest.model_fields
    with pytest.raises(ValidationError):
        SessionAnalysisCreateRequest.model_validate(
            {"technical_detail": "Unsupported", "evidence": []}
        )
    with pytest.raises(ValidationError):
        SessionAnalysisCreateRequest.model_validate(
            {
                "technical_detail": "Duplicate",
                "evidence": [
                    {
                        "evidence_type": "OBSERVATION",
                        "reference_id": REFERENCE_ID,
                    },
                    {
                        "evidence_type": "OBSERVATION",
                        "reference_id": REFERENCE_ID,
                    },
                ],
            }
        )


def test_hypothesis_status_and_visibility_are_server_controlled() -> None:
    payload = HypothesisCreateRequest.model_validate(
        {
            "description": "  Brake release may amplify instability.  ",
            "cause_classification": "DRIVER_TECHNIQUE",
            "confidence": "MEDIUM",
        }
    )

    assert payload.description == "Brake release may amplify instability."
    assert HypothesisStatus.PROPOSED.value == "PROPOSED"
    assert Visibility.ENGINEERING_CONFIDENTIAL.value == "ENGINEERING_CONFIDENTIAL"
    assert "status" not in HypothesisCreateRequest.model_fields
    assert "visibility_level" not in HypothesisCreateRequest.model_fields
    with pytest.raises(ValidationError):
        HypothesisCreateRequest.model_validate(
            {
                "description": "Premature conclusion",
                "cause_classification": "UNKNOWN",
                "confidence": "LOW",
                "status": "SUPPORTED",
            }
        )
    with pytest.raises(ValidationError):
        HypothesisUpdateRequest.model_validate({"status": "SUPPORTED"})


def test_updates_cannot_replace_evidence_or_clear_required_detail() -> None:
    with pytest.raises(ValidationError):
        SessionAnalysisUpdateRequest.model_validate(
            {"evidence": [{"evidence_type": "LAP", "reference_id": REFERENCE_ID}]}
        )
    with pytest.raises(ValidationError):
        SessionAnalysisUpdateRequest(technical_detail=None)
