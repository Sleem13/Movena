from pydantic import BaseModel, Field


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


class ErrorResponse(BaseModel):
    detail: str
