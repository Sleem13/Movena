"""Patient profile, exercise-plan, and progress contracts."""

from datetime import datetime
from typing import Literal

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


class ExerciseBaselineComparison(BaseModel):
    exercise_id: str
    session_count: int
    scored_session_count: int
    baseline_session_id: str | None = None
    baseline_date: datetime | None = None
    baseline_movement_score: float | None = None
    baseline_total_reps: int | None = None
    latest_session_id: str | None = None
    latest_date: datetime | None = None
    latest_movement_score: float | None = None
    latest_total_reps: int | None = None
    score_delta: float | None = None
    reps_delta: int | None = None
    has_comparison: bool = False


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
    exercise_comparisons: list[ExerciseBaselineComparison] = Field(default_factory=list)
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


class ExercisePlanItemCreate(BaseModel):
    exercise_id: str = Field(min_length=1, max_length=64)
    sets: int = Field(ge=1, le=20)
    reps: int = Field(ge=1, le=100)
    days_per_week: int = Field(ge=1, le=7)
    instructions: str | None = Field(default=None, max_length=1000)
    duration_minutes: int | None = Field(default=None, ge=1, le=240)
    rest_interval_seconds: int | None = Field(default=None, ge=0, le=3600)
    tempo: str | None = Field(default=None, max_length=64)
    precautions: str | None = Field(default=None, max_length=1000)
    target_rom_degrees: float | None = Field(default=None, ge=0, le=360)
    target_score: float | None = Field(default=None, ge=0, le=100)
    schedule_days: list[int] = Field(default_factory=list, max_length=7)
    requested_media_upload: bool = False
    requires_ai_analysis: bool = False

    @field_validator("schedule_days")
    @classmethod
    def valid_schedule_days(cls, value: list[int]) -> list[int]:
        if any(day < 0 or day > 6 for day in value):
            raise ValueError("Schedule days must use Monday=0 through Sunday=6.")
        return sorted(set(value))


class ExercisePlanItemDetail(ExercisePlanItemCreate):
    item_id: str
    sort_order: int
    status: Literal["active", "replaced", "completed"] = "active"


class ExercisePlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)
    start_date: datetime | None = None
    end_date: datetime | None = None
    items: list[ExercisePlanItemCreate] = Field(min_length=1, max_length=20)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Plan title cannot be blank.")
        return value.strip()


class ExercisePlanStatusUpdate(BaseModel):
    status: Literal["active", "paused", "completed"]


class ExercisePlanDetail(BaseModel):
    created_by_name: str | None = None
    plan_id: str
    patient_id: str
    created_by_user_id: str | None = None
    title: str
    notes: str | None = None
    status: Literal["active", "paused", "completed"]
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    items: list[ExercisePlanItemDetail] = Field(default_factory=list)
