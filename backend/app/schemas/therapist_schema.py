"""Therapist dashboard contracts."""

from pydantic import BaseModel, Field

from app.schemas.patient_schema import DetectedIssueTrend
from app.schemas.session_schema import SessionSummary


PROTOTYPE_WARNING = (
    "Privacy notice: only process patient information with appropriate authorization "
    "and consent, and follow applicable privacy and retention policies."
)


class TherapistDashboardSummary(BaseModel):
    total_patients: int
    total_sessions: int
    recent_sessions: list[SessionSummary] = Field(default_factory=list)
    low_confidence_sessions: int
    common_detected_issues: list[DetectedIssueTrend] = Field(default_factory=list)
    sessions_by_exercise: dict[str, int] = Field(default_factory=dict)
    low_confidence_sessions_by_exercise: dict[str, int] = Field(default_factory=dict)
    prototype_warning: str = PROTOTYPE_WARNING
