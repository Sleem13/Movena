from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

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


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str = Field(max_length=320)
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or not all(character.isalnum() or character in "._-" for character in normalized):
            raise ValueError("Username may contain only letters, numbers, dots, hyphens, and underscores.")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("A valid email address is required.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return value.strip()


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
