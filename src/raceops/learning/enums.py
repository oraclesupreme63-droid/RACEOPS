"""Controlled vocabulary for evidence-based engineering analysis."""

from enum import StrEnum


class AnalysisEvidenceType(StrEnum):
    """Kinds of existing Session evidence an analysis can reference."""

    DRIVER_FEEDBACK = "DRIVER_FEEDBACK"
    LAP = "LAP"
    SECTOR = "SECTOR"
    CONDITION = "CONDITION"
    OBSERVATION = "OBSERVATION"


class CauseClassification(StrEnum):
    """Broad suspected-cause groups; none asserts proven causation."""

    DRIVER_TECHNIQUE = "DRIVER_TECHNIQUE"
    VEHICLE_SETUP = "VEHICLE_SETUP"
    MECHANICAL = "MECHANICAL"
    TIRES = "TIRES"
    TRACK_ENVIRONMENT = "TRACK_ENVIRONMENT"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(StrEnum):
    """Explicit uncertainty attached to an engineering hypothesis."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HypothesisStatus(StrEnum):
    """Lifecycle states; evaluation transitions belong to Block 8.11."""

    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
