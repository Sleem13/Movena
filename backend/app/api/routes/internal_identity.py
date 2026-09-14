"""Private identity projection endpoint; disabled until a shared secret is configured."""
import json
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthError, authorization_credentials
from app.db.database import get_db
from app.services.internal_principal_service import consume_service_assertion, project_account
from app.core.config import get_settings

router = APIRouter(prefix="/internal/v1/identity", tags=["internal"])
@router.put("/accounts/{user_id}")
async def put_account(user_id: str, request: Request,
                      credentials: HTTPAuthorizationCredentials | None = Depends(authorization_credentials),
                      db: Session = Depends(get_db)):
    body = await request.body()
    if credentials is None or credentials.scheme.lower() != "movenainternal":
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    consume_service_assertion(db, credentials.credentials, request.method, request.url.path, body)
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthError(422, "INVALID_PROJECTION", "The account projection is invalid.") from exc
    if payload.get("user_id") != user_id:
        raise AuthError(422, "INVALID_PROJECTION", "The account projection is invalid.")
    try:
        user = project_account(db, payload)
    except (TypeError, ValueError):
        raise AuthError(409, "PROJECTION_REJECTED", "The account projection was rejected.") from None
    return {"user_id": user.user_id, "identity_owner": user.identity_owner, "token_version": user.token_version}


@router.put("/ownership-transfers/{user_id}")
async def transfer_account(user_id: str, request: Request,
                           credentials: HTTPAuthorizationCredentials | None = Depends(authorization_credentials),
                           db: Session = Depends(get_db)):
    body = await request.body()
    if not get_settings().allow_identity_ownership_transfer:
        raise AuthError(403, "IDENTITY_TRANSFER_DISABLED", "Identity ownership transfer is disabled.")
    if credentials is None or credentials.scheme.lower() != "movenainternal":
        raise AuthError(401, "INVALID_INTERNAL_ASSERTION", "Internal authentication failed.")
    consume_service_assertion(db, credentials.credentials, request.method, request.url.path, body,
                              subject="identity-transfer")
    try:
        envelope = json.loads(body)
        payload = envelope["account"]
        if set(envelope) != {"account", "expected_legacy_token_version", "legacy_password_hash_sha256"}:
            raise ValueError()
        if payload.get("user_id") != user_id:
            raise ValueError()
        user = project_account(db, payload, allow_legacy_conversion=True,
            expected_legacy_token_version=envelope["expected_legacy_token_version"],
            legacy_password_hash_sha256=envelope["legacy_password_hash_sha256"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise AuthError(409, "IDENTITY_TRANSFER_REJECTED", "Identity ownership transfer was rejected.") from None
    return {"user_id":user.user_id, "identity_owner":user.identity_owner, "token_version":user.token_version}
