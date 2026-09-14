"""Verify one-use platform assertions and maintain read-only identity projections."""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from uuid import UUID

import jwt
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthError
from app.core.config import get_settings
from app.db.models import InternalPrincipalNonce, User


def _claims(token: str, method: str, path: str, body_sha256: str | None) -> dict:
    settings = get_settings()
    if not settings.internal_assertion_secret or len(settings.internal_assertion_secret) < 32:
        raise AuthError(401, "INTERNAL_AUTH_DISABLED", "Internal authentication is unavailable.")
    try:
        claims = jwt.decode(token, settings.internal_assertion_secret, algorithms=["HS256"],
                            issuer=settings.internal_assertion_issuer,
                            audience=settings.internal_assertion_audience,
                            options={"require": ["sub", "jti", "iat", "exp", "method", "path", "body_sha256"]},
                            leeway=2)
    except jwt.PyJWTError as exc:
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.") from exc
    if (not all(isinstance(claims.get(name), str) for name in ("sub", "jti", "method", "path", "body_sha256"))
        or not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", claims["jti"])
        or not re.fullmatch(r"[0-9a-f]{64}", claims["body_sha256"])
        or type(claims.get("iat")) is not int or type(claims.get("exp")) is not int
        or type(claims.get("ver")) is not int or claims["ver"] < 0):
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    if claims["method"] != method.upper() or claims["path"] != path or claims["body_sha256"] != (body_sha256 or hashlib.sha256(b"").hexdigest()):
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    if int(claims["exp"]) - int(claims["iat"]) > 30:
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    return claims


def _consume(db: Session, claims: dict) -> None:
    now = datetime.now(timezone.utc)
    db.execute(delete(InternalPrincipalNonce).where(InternalPrincipalNonce.expires_at < now))
    db.add(InternalPrincipalNonce(jti=str(claims["jti"]), subject=str(claims["sub"]),
                                  expires_at=datetime.fromtimestamp(int(claims["exp"]), timezone.utc), consumed_at=now))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AuthError(401, "INTERNAL_ASSERTION_REPLAYED", "Internal authentication failed.") from exc


def consume_user_assertion(db: Session, token: str, method: str, path: str, body_sha256: str | None) -> User:
    claims = _claims(token, method, path, body_sha256)
    if path.startswith("/api/v1/auth/") and path != "/api/v1/auth/me":
        raise AuthError(403, "IDENTITY_DOMAIN_ISOLATED", "Identity operations are managed by the replacement service.")
    if path == "/api/v1/admin/users" or path.startswith("/api/v1/admin/users/"):
        raise AuthError(403, "IDENTITY_DOMAIN_ISOLATED", "Identity operations are managed by the replacement service.")
    _consume(db, claims)
    user = db.scalar(select(User).where(User.user_id == claims["sub"], User.identity_owner == "platform"))
    if user is None or not user.is_active or user.account_status != "active" or user.token_version != claims.get("ver"):
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    return user


def consume_service_assertion(db: Session, token: str, method: str, path: str, body: bytes,
                              *, subject: str = "identity-projector") -> None:
    digest = hashlib.sha256(body).hexdigest()
    claims = _claims(token, method, path, digest)
    if claims["sub"] != subject:
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    _consume(db, claims)


def project_account(db: Session, payload: dict, *, allow_legacy_conversion=False,
                    expected_legacy_token_version=None, legacy_password_hash_sha256=None) -> User:
    required = {"user_id", "username", "email", "full_name", "role", "is_active", "is_verified",
                "account_status", "is_protected", "token_version", "permissions"}
    if set(payload) != required or not isinstance(payload["permissions"], list):
        raise ValueError("Invalid account projection")
    try:
        user_id = str(UUID(payload["user_id"]))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid account projection") from None
    if user_id != payload["user_id"] or payload["role"] not in {
        "super_admin", "admin", "therapist", "patient", "support", "researcher_demo"
    } or payload["account_status"] not in {"active", "paused", "suspended"}:
        raise ValueError("Invalid account projection")
    for field in ("is_active", "is_verified", "is_protected"):
        if type(payload[field]) is not bool:
            raise ValueError("Invalid account projection")
    if type(payload["token_version"]) is not int or payload["token_version"] < 0:
        raise ValueError("Invalid account projection")
    if (not isinstance(payload["email"], str) or not 3 <= len(payload["email"]) <= 320
        or "@" not in payload["email"] or any(not isinstance(item, str) for item in payload["permissions"])):
        raise ValueError("Invalid account projection")
    for field, maximum in (("username", 64), ("full_name", 120)):
        if payload[field] is not None and (not isinstance(payload[field], str) or len(payload[field]) > maximum):
            raise ValueError("Invalid account projection")
    user = db.scalar(select(User).where(User.user_id == payload["user_id"]))
    if user is not None and user.identity_owner != "platform":
        if (not allow_legacy_conversion or user.identity_owner != "legacy"
            or user.token_version != expected_legacy_token_version
            or not isinstance(legacy_password_hash_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", legacy_password_hash_sha256)
            or not hmac.compare_digest(
                hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest(),
                legacy_password_hash_sha256,
            )):
            raise ValueError("Projection collides with a legacy-owned account")
    if user is not None:
        if payload["token_version"] < user.token_version:
            raise ValueError("Stale account projection")
        current_authority = (user.role, user.is_active, user.account_status, user.is_protected, user.permissions_json)
        projected_authority = (payload["role"], payload["is_active"], payload["account_status"],
                               payload["is_protected"], json.dumps(payload["permissions"], separators=(",", ":"), sort_keys=True))
        if payload["token_version"] == user.token_version and current_authority != projected_authority:
            raise ValueError("Conflicting account projection")
        if user.is_verified and not payload["is_verified"]:
            raise ValueError("Stale account projection")
    if user is None:
        collision = db.scalar(select(User).where(func.lower(User.email) == payload["email"].lower()))
        if collision is not None:
            raise ValueError("Projection collides with an existing account")
        user = User(user_id=payload["user_id"], password_hash="!platform-owned", identity_owner="platform")
        db.add(user)
    for field in ("username", "email", "full_name", "role", "is_active", "is_verified", "account_status", "is_protected", "token_version"):
        setattr(user, field, payload[field])
    user.permissions_json = json.dumps(payload["permissions"], separators=(",", ":"), sort_keys=True)
    user.password_hash = "!platform-owned"
    user.identity_owner = "platform"
    try:
        db.flush()
        if user.role == "patient":
            from app.services.care_service import ensure_patient_profile
            ensure_patient_profile(db, user)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Projection violates account uniqueness") from exc
    db.refresh(user)
    return user
