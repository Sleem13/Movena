from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    therapist = "therapist"
    patient = "patient"
    researcher_demo = "researcher_demo"


class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=12, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)
    role: UserRole = UserRole.researcher_demo

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return value


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserSummary(BaseModel):
    user_id: str
    email: str
    full_name: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool
    account_status: str = "active"
    is_protected: bool = False

    model_config = {"from_attributes": True}


class CurrentUserResponse(UserSummary):
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSummary


class ConsentStatus(BaseModel):
    consent_type: str
    accepted: bool
    version: str
    notes: str | None = None
