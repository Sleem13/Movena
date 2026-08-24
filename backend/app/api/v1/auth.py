from uuid import uuid4

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth_schema import CurrentUserResponse, TokenResponse, UserLoginRequest, UserRegisterRequest, UserRole, UserSummary
from app.schemas.error_schema import ErrorResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def auth_error(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(error_code=code, message=message).model_dump())


@router.post("/register", response_model=UserSummary, status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    if data.role in {UserRole.super_admin, UserRole.admin, UserRole.therapist}:
        return auth_error("ROLE_NOT_ALLOWED", "Public registration cannot create privileged users.", 403)
    email = data.email.lower().strip()
    if db.scalar(select(User).where(User.email == email)):
        return auth_error("EMAIL_ALREADY_REGISTERED", "An account with this email already exists.", 409)
    user = User(user_id=str(uuid4()), email=email, password_hash=get_password_hash(data.password),
                full_name=data.full_name.strip() if data.full_name else None, role=data.role.value)
    db.add(user); db.commit(); db.refresh(user)
    return UserSummary.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower().strip()))
    if user is None or not verify_password(data.password, user.password_hash):
        return auth_error("INVALID_CREDENTIALS", "Username/email or password is incorrect.", 401)
    if not user.is_active or user.account_status != "active":
        code = {"paused": "ACCOUNT_PAUSED", "suspended": "ACCOUNT_SUSPENDED"}.get(user.account_status, "USER_INACTIVE")
        return auth_error(code, "This user account is not active. Contact the super administrator.", 403)
    settings = get_settings()
    return TokenResponse(access_token=create_access_token(user.user_id, user.role, token_version=user.token_version),
                         expires_in=settings.access_token_expire_minutes * 60,
                         user=UserSummary.model_validate(user))


@router.get("/me", response_model=CurrentUserResponse)
def me(user: User = Depends(get_current_user)):
    return CurrentUserResponse.model_validate(user)


@router.post("/logout")
def logout(_user: User = Depends(get_current_user)):
    return {"status": "success", "message": "Token removed client-side. Server-side revocation is not yet implemented."}
