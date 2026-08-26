"""API contracts for durable background analysis jobs."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AnalysisJobStatus = Literal["queued", "running", "completed", "failed", "cancelled"]


class AnalysisJobResponse(BaseModel):
    job_id: str
    exercise_id: str
    status: AnalysisJobStatus
    stage: str
    progress: int = Field(ge=0, le=100)
    attempts: int
    max_attempts: int
    cancel_requested: bool = False
    error_code: str | None = None
    message: str | None = None
    http_status: int | None = None
    result: dict[str, Any] | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AnalysisJobCancelResponse(BaseModel):
    job_id: str
    status: AnalysisJobStatus
    message: str
