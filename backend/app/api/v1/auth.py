from uuid import uuid4

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.authorization import permissions_json_for_role
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.db.models import AuditLog, User, utc_now
from app.schemas.auth_schema import (
    AuthMessageResponse, CurrentUserResponse, EmailRequest, PasswordResetRequest,
    TokenRequest, TokenResponse, UserLoginRequest, UserRegisterRequest, UserRole, UserSummary,
)
from app.schemas.error_schema import ErrorResponse
from app.services.auth_token_service import (
    consume_password_reset_token, consume_verification_token, cooldown_active,
    is_expired, issue_password_reset_token, issue_verification_token, token_hash,
)
from app.services.email_service import EmailDeliveryError, send_password_reset_email, send_verification_email

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
    if db.scalar(select(User).where(func.lower(User.username) == data.username)):
        return auth_error("USERNAME_ALREADY_REGISTERED", "An account with this username already exists.", 409)
    settings = get_settings()
    assigned_role = data.role.value
    user = User(
        user_id=str(uuid4()), username=data.username, email=email, password_hash=get_password_hash(data.password),
        full_name=data.full_name, role=assigned_role,
        permissions_json=permissions_json_for_role(assigned_role),
        is_verified=not settings.require_email_verification,
        email_verified_at=utc_now() if not settings.require_email_verification else None,
    )
    if not settings.require_email_verification:
        db.add(user); db.commit(); db.refresh(user)
        return UserSummary.model_validate(user)
    verification_token = issue_verification_token(user)
    db.add(user); db.commit(); db.refresh(user)
    try:
        send_verification_email(user.email, verification_token)
    except EmailDeliveryError:
        user.verification_sent_at = None
        db.commit()
        return auth_error("EMAIL_DELIVERY_FAILED", "Your account was created, but the verification email could not be delivered. Please use resend verification.", 503)
    return UserSummary.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    identifier = data.email.lower().strip()
    user = db.scalar(select(User).where(or_(func.lower(User.email) == identifier, func.lower(User.username) == identifier)))
    if user is None or not verify_password(data.password, user.password_hash):
        return auth_error("INVALID_CREDENTIALS", "Username/email or password is incorrect.", 401)
    if not user.is_active or user.account_status != "active":
        code = {"paused": "ACCOUNT_PAUSED", "suspended": "ACCOUNT_SUSPENDED"}.get(user.account_status, "USER_INACTIVE")
        return auth_error(code, "This user account is not active. Contact the super administrator.", 403)
    settings = get_settings()
    if settings.require_email_verification and not user.is_verified:
        return auth_error("EMAIL_NOT_VERIFIED", "Verify your email before logging in.", 403)
    return TokenResponse(access_token=create_access_token(user.user_id, user.role, token_version=user.token_version),
                         expires_in=settings.access_token_expire_minutes * 60,
                         user=UserSummary.model_validate(user))


@router.get("/me", response_model=CurrentUserResponse)
def me(user: User = Depends(get_current_user)):
    return CurrentUserResponse.model_validate(user)


@router.post("/logout")
def logout(_user: User = Depends(get_current_user)):
    return {"status": "success", "message": "Token removed client-side. Server-side revocation is not yet implemented."}


@router.post("/verify-email", response_model=AuthMessageResponse)
def verify_email(data: TokenRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.verification_token_hash == token_hash(data.token)))
    if user is None or is_expired(user.verification_token_expires):
        return auth_error("INVALID_OR_EXPIRED_TOKEN", "This verification link is invalid or has expired.", 400)
    consume_verification_token(user)
    db.add(AuditLog(actor_user_id=user.user_id, action="user.email_verified", resource_type="user", resource_id=user.user_id))
    db.commit()
    return AuthMessageResponse(message="Email verified. You can now log in.")


@router.post("/resend-verification", response_model=AuthMessageResponse)
def resend_verification(data: EmailRequest, db: Session = Depends(get_db)):
    if not get_settings().require_email_verification:
        return AuthMessageResponse(message="Email verification is temporarily disabled. Contact a super administrator for account support.")
    generic = AuthMessageResponse(message="If an unverified account exists, a verification email has been sent.")
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None or user.is_verified or cooldown_active(user.verification_sent_at):
        return generic
    verification_token = issue_verification_token(user)
    db.commit()
    try:
        send_verification_email(user.email, verification_token)
    except EmailDeliveryError:
        user.verification_sent_at = None
        db.commit()
        return auth_error("EMAIL_DELIVERY_FAILED", "The verification email could not be delivered. Please try again later.", 503)
    return generic


@router.post("/forgot-password", response_model=AuthMessageResponse)
def forgot_password(data: EmailRequest, db: Session = Depends(get_db)):
    generic = AuthMessageResponse(message="If an eligible account exists, a password reset email has been sent.")
    user = db.scalar(select(User).where(User.email == data.email))
    verification_required = get_settings().require_email_verification
    if (
        user is None
        or (verification_required and not user.is_verified)
        or not user.is_active
        or cooldown_active(user.reset_password_sent_at)
    ):
        return generic
    reset_token = issue_password_reset_token(user)
    db.commit()
    try:
        send_password_reset_email(user.email, reset_token)
    except EmailDeliveryError:
        user.reset_password_sent_at = None
        db.commit()
        return auth_error("EMAIL_DELIVERY_FAILED", "The password reset email could not be delivered. Please try again later.", 503)
    return generic


@router.post("/reset-password", response_model=AuthMessageResponse)
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.reset_password_token_hash == token_hash(data.token)))
    if user is None or is_expired(user.reset_password_expires):
        return auth_error("INVALID_OR_EXPIRED_TOKEN", "This password reset link is invalid or has expired.", 400)
    user.password_hash = get_password_hash(data.new_password)
    user.token_version += 1
    consume_password_reset_token(user)
    db.add(AuditLog(
        actor_user_id=user.user_id, action="user.password_recovered",
        resource_type="user", resource_id=user.user_id,
        metadata_json='{"existing_sessions_revoked":true}',
    ))
    db.commit()
    return AuthMessageResponse(message="Password updated. You can now log in with the new password.")
