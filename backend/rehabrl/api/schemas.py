"""Validated request models for the RehabRL API."""

from pydantic import BaseModel, Field


class TrainingRequest(BaseModel):
    episodes: int = Field(default=100, ge=1, le=1000)
    max_steps: int = Field(default=50, ge=5, le=100)
    learning_rate: float = Field(default=3e-4, gt=0, le=0.01)
    gamma: float = Field(default=0.96, ge=0.5, le=0.999)
    batch_size: int = Field(default=128, ge=16, le=512)
    use_mhealth: bool = False


class AssessmentRequest(BaseModel):
    injury_type: str = "ACL Tear"
    recovery_stage: int = Field(default=1, ge=0, le=4)
    injury_severity: float = Field(default=0.7, ge=0, le=1)
    pain_level: float = Field(default=0.5, ge=0, le=1)
    rom: float = Field(default=0.6, ge=0, le=1)
    strength: float = Field(default=0.55, ge=0, le=1)
    movement_quality: float = Field(default=0.55, ge=0, le=1)
    fatigue: float = Field(default=0.3, ge=0, le=1)
    adherence: float = Field(default=0.85, ge=0, le=1)


class SimulationRequest(BaseModel):
    injury_type: str = "ACL Tear"
    injury_severity: float = Field(default=0.7, ge=0, le=1)
    recovery_stage: int = Field(default=0, ge=0, le=4)
    sessions: int = Field(default=40, ge=5, le=100)
