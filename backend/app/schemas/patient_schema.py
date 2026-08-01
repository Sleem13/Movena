"""Development-only patient profile and progress contracts."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.session_schema import SessionSummary


class PatientCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    age_group: str | None = None
    sex: str | None = None
    clinical_group: str | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("display_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Display name cannot be blank.")
        return value.strip()


class PatientUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    age_group: str | None = None
    sex: str | None = None
    clinical_group: str | None = None
    notes: str | None = Field(default=None, max_length=1000)


class DetectedIssueTrend(BaseModel):
    issue_code: str
    count: int


class PatientProgressSummary(BaseModel):
    patient_id: str
    total_sessions: int = 0
    sessions_by_exercise: dict[str, int] = Field(default_factory=dict)
    average_movement_score: float | None = None
    average_analysis_confidence: float | None = None
    movement_score_observation_count: int = 0
    analysis_confidence_observation_count: int = 0
    latest_session_date: datetime | None = None
    detected_issue_counts: list[DetectedIssueTrend] = Field(default_factory=list)
    low_confidence_session_count: int = 0
    metric_provenance: list[str] = Field(default_factory=list)


class PatientSummary(BaseModel):
    patient_id: str
    display_name: str
    age_group: str | None = None
    sex: str | None = None
    clinical_group: str | None = None
    created_at: datetime
    updated_at: datetime
    session_count: int = 0
    latest_session_date: datetime | None = None


class PatientDetail(PatientSummary):
    notes: str | None = None
    progress: PatientProgressSummary
    prototype_warning: str


PatientSessionSummary = SessionSummary
