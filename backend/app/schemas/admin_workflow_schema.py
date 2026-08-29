"""De-identified contracts for the Super Admin operations workflow."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


WorkflowStatus = Literal["on_track", "attention"]
WorkflowPriority = Literal["high", "medium", "low"]


class WorkflowMetrics(BaseModel):
    users: int = 0
    patients: int = 0
    active_assignments: int = 0
    appointments: int = 0
    paid_orders: int = 0


class WorkflowStage(BaseModel):
    key: str
    total: int = 0
    attention_count: int = 0
    status: WorkflowStatus = "on_track"


class WorkflowAttentionItem(BaseModel):
    id: str
    type: str
    subject_ref: str
    owner: str
    age_seconds: int = Field(ge=0)
    priority: WorkflowPriority
    action_url: str


class WorkflowAuditItem(BaseModel):
    id: int
    actor_ref: str
    action: str
    resource_type: str
    resource_ref: str
    created_at: datetime


class WorkflowToday(BaseModel):
    date: str
    timezone: str = "Africa/Cairo"
    appointments: int = 0


class WorkflowPaymentExceptions(BaseModel):
    pending_orders: int = 0
    failed_payments: int = 0
    pending_refunds: int = 0


class WorkflowPrivacyRequests(BaseModel):
    pending: int = 0
    export: int = 0
    correction: int = 0
    deletion: int = 0


class AdminWorkflowResponse(BaseModel):
    generated_at: datetime
    timezone: str = "Africa/Cairo"
    metrics: WorkflowMetrics
    stages: list[WorkflowStage]
    attention_queue: list[WorkflowAttentionItem]
    today: WorkflowToday
    payment_exceptions: WorkflowPaymentExceptions
    privacy_requests: WorkflowPrivacyRequests
    recent_audit: list[WorkflowAuditItem]
