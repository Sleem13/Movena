from datetime import datetime, timedelta, timezone
import logging

import bcrypt
import jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str, role: str, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    if settings.secret_key == "change-me-in-production":
        logger.warning("Default development SECRET_KEY is active; do not use it in production.")
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "role": role, "iat": now, "exp": expiry}, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm], options={"require": ["sub", "exp"]})
