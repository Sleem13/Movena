"""Public API contracts for saved analysis-session metadata."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SessionMetricSchema(BaseModel):
    metric_name: str
    metric_value_float: float | None = None
    metric_value_text: str | None = None
    unit: str | None = None


class DetectedIssueSchema(BaseModel):
    issue_code: str
    severity: str | None = None
    message: str | None = None


class SessionCreate(BaseModel):
    exercise_id: str
    status: str
    source_filename: str | None = None


class SessionSummary(BaseModel):
    session_id: str
    exercise_id: str
    exercise_display_name: str
    status: str
    created_at: datetime
    total_reps: int | None = None
    movement_score: float | None = None
    analysis_confidence_level: str | None = None
    pose_quality_level: str | None = None
    detected_issues: list[str] = Field(default_factory=list)
    report_download_url: str | None = None
    overlay_preview_url: str | None = None


class SessionDetail(SessionSummary):
    error_code: str | None = None
    message: str | None = None
    updated_at: datetime
    source_filename: str | None = None
    video_duration_sec: float | None = None
    rep_count_confidence: float | None = None
    analysis_confidence_score: float | None = None
    pose_quality_score: float | None = None
    summary: str | None = None
    limitations: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, Any] | None = None
    input_validity: dict[str, Any] | None = None
    ml_prediction: dict[str, Any] | None = None
    report_id: str | None = None
    overlay_id: str | None = None
    overlay_download_url: str | None = None
    metrics: list[SessionMetricSchema] = Field(default_factory=list)
    issue_details: list[DetectedIssueSchema] = Field(default_factory=list)


class SessionListResponse(BaseModel):
    items: list[SessionSummary]
    total: int
    limit: int
    offset: int


class SessionDeleteResponse(BaseModel):
    status: str = "deleted"
    session_id: str
