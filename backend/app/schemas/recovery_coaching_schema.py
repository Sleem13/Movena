"""Validated contracts for bounded recovery and lifestyle coaching."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


CoachingDomain = Literal[
    "mobility_routine", "sleep_routine", "activity", "stress_management",
    "participation", "adherence", "social_support",
]
BarrierCategory = Literal[
    "none", "time", "symptoms", "fatigue", "confidence", "environment",
    "support", "access", "other",
]


class CoachingGoalCreate(BaseModel):
    domain: CoachingDomain
    title: str = Field(min_length=3, max_length=120)
    specific_action: str = Field(min_length=5, max_length=600)
    measurement: str = Field(min_length=3, max_length=160)
    why_important: str = Field(min_length=3, max_length=600)
    target_date: date
    confidence: int = Field(ge=1, le=5)
    patient_agreed: Literal[True]
    scope_acknowledged: Literal[True]

    @field_validator("target_date")
    @classmethod
    def target_is_not_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Goal target date cannot be in the past.")
        return value


class CoachingGoalUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    status: Literal["proposed", "active", "paused", "completed"]


class CoachingCheckInCreate(BaseModel):
    check_in_date: date
    energy: int = Field(ge=1, le=5)
    sleep_quality: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=5)
    recovery_confidence: int = Field(ge=1, le=5)
    activity_minutes: int = Field(default=0, ge=0, le=1440)
    barrier_category: BarrierCategory = "none"
    barrier_note: str | None = Field(default=None, max_length=600)
    symptoms_changed: bool = False
    urgent_concern: bool = False
    scope_acknowledged: Literal[True]

    @field_validator("check_in_date")
    @classmethod
    def check_in_is_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Check-in date cannot be in the future.")
        return value


class CoachingActionPlanCreate(BaseModel):
    goal_id: str = Field(min_length=36, max_length=36)
    action_step: str = Field(min_length=5, max_length=600)
    frequency: str = Field(min_length=3, max_length=120)
    support_needed: str | None = Field(default=None, max_length=600)
    review_date: date
    patient_agreed: Literal[True]

    @field_validator("review_date")
    @classmethod
    def review_is_not_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Action-plan review date cannot be in the past.")
        return value


class CoachingActionPlanUpdate(BaseModel):
    status: Literal["active", "completed", "paused", "cancelled"]
