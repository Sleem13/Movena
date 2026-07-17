"""Therapist dashboard development-prototype contracts."""

from pydantic import BaseModel, Field

from app.schemas.patient_schema import DetectedIssueTrend
from app.schemas.session_schema import SessionSummary


PROTOTYPE_WARNING = (
    "Therapist dashboard is a prototype. Do not use with real patient data without "
    "authentication, consent, and privacy review."
)


class TherapistDashboardSummary(BaseModel):
    total_patients: int
    total_sessions: int
    recent_sessions: list[SessionSummary] = Field(default_factory=list)
    low_confidence_sessions: int
    common_detected_issues: list[DetectedIssueTrend] = Field(default_factory=list)
    sessions_by_exercise: dict[str, int] = Field(default_factory=dict)
    prototype_warning: str = PROTOTYPE_WARNING
