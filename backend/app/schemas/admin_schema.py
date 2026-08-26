from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.auth_schema import UserRole, UserSummary
from app.schemas.session_schema import SessionSummary


class AccountStatus(str, Enum):
    active = "active"
    paused = "paused"
    suspended = "suspended"


class ManagedUserSummary(UserSummary):
    created_at: datetime
    updated_at: datetime
    session_count: int = 0
    last_session_at: datetime | None = None


class ManagedUserDetail(ManagedUserSummary):
    sessions: list[SessionSummary] = Field(default_factory=list)
    consents: list[dict] = Field(default_factory=list)


class AccountStatusUpdate(BaseModel):
    status: AccountStatus
    reason: str = Field(min_length=3, max_length=500)


class AccountRoleUpdate(BaseModel):
    role: UserRole
    reason: str = Field(min_length=3, max_length=500)


class AdminPasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
    reason: str = Field(min_length=3, max_length=500)


class AccountActionResponse(BaseModel):
    status: str = "success"
    user_id: str
    message: str
