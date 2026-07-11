from pydantic import BaseModel, Field


class FrameAnalysis(BaseModel):
    frame_index: int
    timestamp_sec: float
    knee_angle: float
    hip_angle: float
    trunk_angle: float
    phase: str
    detected_issue: str | None = None


class AnalysisResponse(BaseModel):
    exercise: str = "bodyweight_squat"
    status: str = "success"
    total_reps: int = 0
    average_knee_angle: float = 0
    average_hip_angle: float = 0
    average_trunk_angle: float = 0
    movement_score: int = Field(default=0, ge=0, le=100)
    detected_issues: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    summary: str = ""
    limitations: list[str] = Field(default_factory=list)
    frame_analysis: list[FrameAnalysis] | None = None
    report_id: str | None = None
    report_url: str | None = None
    overlay_id: str | None = None
    overlay_url: str | None = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: list[str] = Field(default_factory=list)


SquatAnalysisResponse = AnalysisResponse
AnalysisErrorResponse = ErrorResponse
