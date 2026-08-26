"""Super-administrator account management with immutable-account guards."""

from __future__ import annotations

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_super_admin
from app.core.security import get_password_hash
from app.core.authorization import permissions_json_for_role
from app.db.crud import to_summary
from app.db.database import get_db
from app.db.models import AnalysisSession, AuditLog, User, UserConsent, utc_now
from app.schemas.admin_schema import (
    AccountActionResponse,
    AccountRoleUpdate,
    AccountStatusUpdate,
    AdminPasswordReset,
    AdminUserCreate,
    ManagedUserDetail,
    ManagedUserSummary,
)
from app.schemas.auth_schema import UserRole
from app.schemas.error_schema import ErrorResponse

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["super-admin"],
    dependencies=[Depends(require_super_admin)],
)


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(error_code=code, message=message).model_dump())


def find_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def editable_target(db: Session, user_id: str) -> User | JSONResponse:
    target = find_user(db, user_id)
    if target is None:
        return error("USER_NOT_FOUND", "The requested user account was not found.", 404)
    if target.is_protected or target.role == UserRole.super_admin.value:
        return error("PROTECTED_ACCOUNT", "Protected super-administrator accounts cannot be modified.", 403)
    return target


def audit(db: Session, actor: User, action: str, target: User, metadata: dict) -> None:
    db.add(AuditLog(
        actor_user_id=actor.user_id,
        action=action,
        resource_type="user",
        resource_id=target.user_id,
        metadata_json=json.dumps(metadata, sort_keys=True),
    ))


def managed_summary(db: Session, user: User) -> ManagedUserSummary:
    session_count, last_session_at = db.execute(
        select(func.count(AnalysisSession.id), func.max(AnalysisSession.created_at)).where(
            or_(AnalysisSession.owner_user_id == user.user_id, AnalysisSession.created_by_user_id == user.user_id)
        )
    ).one()
    return ManagedUserSummary.model_validate({
        **user.__dict__,
        "session_count": session_count,
        "last_session_at": last_session_at,
    })


@router.get("", response_model=list[ManagedUserSummary])
def list_users(
    search: str | None = Query(default=None, max_length=120),
    role: UserRole | None = None,
    account_status: str | None = Query(default=None, pattern="^(active|paused|suspended)$"),
    db: Session = Depends(get_db),
):
    statement = select(User).order_by(User.created_at.desc())
    if search:
        term = f"%{search.strip().lower()}%"
        statement = statement.where(or_(func.lower(User.email).like(term), func.lower(User.username).like(term), func.lower(User.full_name).like(term)))
    if role:
        statement = statement.where(User.role == role.value)
    if account_status:
        statement = statement.where(User.account_status == account_status)
    return [managed_summary(db, user) for user in db.scalars(statement).all()]


@router.post("", response_model=ManagedUserSummary, status_code=status.HTTP_201_CREATED)
def create_user(data: AdminUserCreate, actor: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    if data.role == UserRole.super_admin:
        return error("ROLE_NOT_ALLOWED", "Additional super administrators must use protected provisioning.", 403)
    if db.scalar(select(User).where(func.lower(User.email) == data.email)):
        return error("EMAIL_ALREADY_REGISTERED", "An account with this email already exists.", 409)
    if db.scalar(select(User).where(func.lower(User.username) == data.username)):
        return error("USERNAME_ALREADY_REGISTERED", "An account with this username already exists.", 409)
    target = User(
        user_id=str(uuid4()),
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=get_password_hash(data.password),
        role=data.role.value,
        permissions_json=permissions_json_for_role(data.role.value),
        is_active=True,
        is_verified=True,
        email_verified_at=utc_now(),
        account_status="active",
    )
    db.add(target)
    audit(db, actor, "user.created", target, {"username": target.username, "email": target.email, "role": target.role})
    db.commit()
    db.refresh(target)
    return managed_summary(db, target)


@router.get("/{user_id}", response_model=ManagedUserDetail)
def user_detail(user_id: str, db: Session = Depends(get_db)):
    target = find_user(db, user_id)
    if target is None:
        return error("USER_NOT_FOUND", "The requested user account was not found.", 404)
    base = managed_summary(db, target).model_dump()
    sessions = db.scalars(
        select(AnalysisSession).where(
            or_(AnalysisSession.owner_user_id == user_id, AnalysisSession.created_by_user_id == user_id)
        ).order_by(AnalysisSession.created_at.desc()).limit(100)
    ).all()
    consents = db.scalars(select(UserConsent).where(UserConsent.user_id == user_id)).all()
    return ManagedUserDetail(
        **base,
        sessions=[to_summary(row) for row in sessions],
        consents=[{
            "consent_type": row.consent_type,
            "accepted": row.accepted,
            "accepted_at": row.accepted_at,
            "version": row.version,
            "notes": row.notes,
        } for row in consents],
    )


@router.patch("/{user_id}/status", response_model=AccountActionResponse)
def update_status(user_id: str, data: AccountStatusUpdate, actor: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    target = editable_target(db, user_id)
    if isinstance(target, JSONResponse):
        return target
    previous = target.account_status
    target.account_status = data.status.value
    target.is_active = data.status.value == "active"
    if previous != data.status.value:
        target.token_version += 1
    audit(db, actor, "user.status_changed", target, {"from": previous, "to": data.status.value, "reason": data.reason})
    db.commit()
    return AccountActionResponse(user_id=user_id, message=f"Account status changed to {data.status.value}.")


@router.patch("/{user_id}/role", response_model=AccountActionResponse)
def update_role(user_id: str, data: AccountRoleUpdate, actor: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    target = editable_target(db, user_id)
    if isinstance(target, JSONResponse):
        return target
    if data.role == UserRole.super_admin:
        return error("ROLE_NOT_ALLOWED", "Additional super administrators must be provisioned through the protected seed process.", 403)
    previous = target.role
    target.role = data.role.value
    target.permissions_json = permissions_json_for_role(target.role)
    if previous != target.role:
        target.token_version += 1
    audit(db, actor, "user.role_changed", target, {"from": previous, "to": target.role, "reason": data.reason})
    db.commit()
    return AccountActionResponse(user_id=user_id, message=f"Account role changed to {target.role}.")


@router.post("/{user_id}/password", response_model=AccountActionResponse)
def reset_password(user_id: str, data: AdminPasswordReset, actor: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    target = editable_target(db, user_id)
    if isinstance(target, JSONResponse):
        return target
    target.password_hash = get_password_hash(data.new_password)
    target.token_version += 1
    audit(db, actor, "user.password_reset", target, {"reason": data.reason})
    db.commit()
    return AccountActionResponse(user_id=user_id, message="Password changed and existing sessions revoked.")


@router.delete("/{user_id}", response_model=AccountActionResponse)
def delete_user(user_id: str, reason: str = Query(min_length=3, max_length=500), actor: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    target = editable_target(db, user_id)
    if isinstance(target, JSONResponse):
        return target
    email = target.email
    audit(db, actor, "user.deleted", target, {"email": email, "role": target.role, "reason": reason})
    db.flush()
    db.delete(target)
    db.commit()
    return AccountActionResponse(user_id=user_id, message="Account deleted. Historical analysis metadata was retained for audit continuity.")
