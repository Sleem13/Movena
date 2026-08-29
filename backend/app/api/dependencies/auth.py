from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth_schema import UserRole

bearer = HTTPBearer(auto_error=False)


class AuthError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code, self.error_code, self.message = status_code, error_code, message


def optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise AuthError(401, "TOKEN_EXPIRED", "Your session has expired. Please log in again.") from exc
    except jwt.PyJWTError as exc:
        raise AuthError(401, "INVALID_TOKEN", "The access token is invalid.") from exc
    user = db.scalar(select(User).where(User.user_id == payload["sub"]))
    if user is None:
        raise AuthError(401, "INVALID_TOKEN", "The access token is invalid.")
    if payload.get("ver", 0) != user.token_version:
        raise AuthError(401, "TOKEN_REVOKED", "This session is no longer valid. Please log in again.")
    if not user.is_active or user.account_status != "active":
        raise AuthError(403, "USER_INACTIVE", "This user account is inactive.")
    if get_settings().require_email_verification and not user.is_verified:
        raise AuthError(403, "EMAIL_NOT_VERIFIED", "Verify your email before accessing this resource.")
    return user

def get_current_user(user: User | None = Depends(optional_current_user)) -> User:
    if user is None:
        raise AuthError(401, "AUTH_REQUIRED", "Please log in to continue.")
    return user


def require_active_user(user: User = Depends(get_current_user)) -> User:
    return user


def require_any_role(roles: set[str | UserRole]) -> Callable:
    allowed = {role.value if isinstance(role, UserRole) else role for role in roles}
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != UserRole.super_admin.value and user.role not in allowed:
            raise AuthError(403, "INSUFFICIENT_ROLE", "You do not have permission to view this resource.")
        return user
    return dependency


def require_role(role: str | UserRole) -> Callable:
    return require_any_role({role})


require_admin = require_role(UserRole.admin)
require_super_admin = require_role(UserRole.super_admin)
require_therapist = require_any_role({UserRole.therapist, UserRole.admin})
require_patient_or_therapist = require_any_role({UserRole.patient, UserRole.therapist, UserRole.admin})


def analysis_current_user(user: User | None = Depends(optional_current_user)) -> User | None:
    if get_settings().require_auth_for_analysis and user is None:
        raise AuthError(401, "AUTH_REQUIRED", "Please log in to analyze a video.")
    return user
