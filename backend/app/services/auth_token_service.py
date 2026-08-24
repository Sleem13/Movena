"""Opaque, hashed, expiring, single-use authentication action tokens."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import Settings, get_settings
from app.db.models import User


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _new_token() -> str:
    return secrets.token_urlsafe(48)


def issue_verification_token(user: User, settings: Settings | None = None) -> str:
    active = settings or get_settings()
    token = _new_token()
    now = utc_now()
    user.verification_token_hash = token_hash(token)
    user.verification_token_expires = now + timedelta(minutes=active.email_verification_expire_minutes)
    user.verification_sent_at = now
    return token


def consume_verification_token(user: User) -> None:
    user.is_verified = True
    user.email_verified_at = utc_now()
    user.verification_token_hash = None
    user.verification_token_expires = None
    user.verification_sent_at = None


def issue_password_reset_token(user: User, settings: Settings | None = None) -> str:
    active = settings or get_settings()
    token = _new_token()
    now = utc_now()
    user.reset_password_token_hash = token_hash(token)
    user.reset_password_expires = now + timedelta(minutes=active.password_reset_expire_minutes)
    user.reset_password_sent_at = now
    return token


def consume_password_reset_token(user: User) -> None:
    user.reset_password_token_hash = None
    user.reset_password_expires = None
    user.reset_password_sent_at = None


def is_expired(value: datetime | None) -> bool:
    if value is None:
        return True
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value <= utc_now()


def cooldown_active(sent_at: datetime | None, settings: Settings | None = None) -> bool:
    if sent_at is None:
        return False
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    active = settings or get_settings()
    return sent_at + timedelta(seconds=active.auth_email_resend_cooldown_seconds) > utc_now()
