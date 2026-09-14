"""Temporary, fixed-origin bridge; legacy remains the only domain writer."""
import httpx
import hashlib
import time
from uuid import uuid4
import jwt
from django.conf import settings
from rest_framework.exceptions import APIException


class UpstreamUnavailable(APIException):
    status_code = 503
    default_detail = "Movena is temporarily unavailable. Please try again."
    default_code = "upstream_unavailable"


def signed_assertion(subject, version, method, path, content=b""):
    if len(settings.INTERNAL_ASSERTION_SECRET) < 32:
        raise UpstreamUnavailable()
    now = int(time.time())
    return jwt.encode({'sub':subject, 'ver':version, 'iat':now, 'exp':now+20, 'jti':uuid4().hex,
        'iss':settings.INTERNAL_ASSERTION_ISSUER, 'aud':settings.INTERNAL_ASSERTION_AUDIENCE,
        'method':method.upper(), 'path':path,
        'body_sha256':hashlib.sha256(content or b'').hexdigest()},
        settings.INTERNAL_ASSERTION_SECRET, algorithm='HS256')


def request(method, path, *, token=None, principal=None, content=None, query="", content_type=None, idempotency_key=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif principal is not None:
        headers['Authorization'] = 'MovenaInternal '+signed_assertion(
            principal.account.pk, principal.account.token_version, method, path, content or b'')
    if content_type:
        headers["Content-Type"] = content_type
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    try:
        with httpx.Client(timeout=httpx.Timeout(300, connect=10), follow_redirects=False, trust_env=False) as client:
            return client.request(method, settings.LEGACY_API_URL + path + ("?" + query if query else ""),
                                  headers=headers, content=content)
    except httpx.HTTPError as exc:
        raise UpstreamUnavailable() from exc
