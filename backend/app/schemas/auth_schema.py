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
    username: str = Field(min_length=3, max_length=64)
    email: str
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)
    role: UserRole = UserRole.researcher_demo

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return value

    @field_validator("username")
    @classmethod
    def valid_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or not all(character.isalnum() or character in "._-" for character in normalized):
            raise ValueError("Username may contain only letters, numbers, dots, hyphens, and underscores.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def valid_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Full name is required.")
        return normalized


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserSummary(BaseModel):
    user_id: str
    username: str | None = None
    email: str
    full_name: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool
    account_status: str = "active"
    is_protected: bool = False
    permissions: list[str] = Field(default_factory=list)

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


class EmailRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return value


class TokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)


class PasswordResetRequest(TokenRequest):
    new_password: str = Field(min_length=8, max_length=128)


class AuthMessageResponse(BaseModel):
    status: str = "success"
    message: str
