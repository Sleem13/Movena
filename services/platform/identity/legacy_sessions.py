"""Retired-issuer JWT validation for a future bounded identity transition.

Signing key and algorithm are supplied by reviewed server configuration, never
by JWT headers. No live key is loaded here and no new legacy JWTs are minted.
"""
from datetime import datetime
import jwt
from django.utils import timezone
from .models import Account
from .sessions import IdentityDenied, eligible


def authenticate_legacy(token, *, key, algorithm, last_issued_at, accept_until, require_verified=True):
    now = timezone.now()
    if (not isinstance(token, str) or len(token) > 8192 or not isinstance(key, str) or len(key.encode()) < 32
        or algorithm not in {'HS256', 'HS384', 'HS512'}
        or not isinstance(last_issued_at, datetime) or not isinstance(accept_until, datetime)
        or last_issued_at.tzinfo is None or accept_until.tzinfo is None
        or last_issued_at > now or accept_until <= now or accept_until <= last_issued_at):
        raise IdentityDenied()
    try:
        claims = jwt.decode(token, key, algorithms=[algorithm], options={'require': ['sub', 'exp', 'iat']})
        version = claims.get('ver', 0)
        if type(version) is not int or version < 0 or type(claims['iat']) is not int or claims['iat'] > last_issued_at.timestamp():
            raise IdentityDenied()
        account = Account.objects.filter(pk=claims['sub']).first()
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise IdentityDenied() from None
    if not eligible(account, require_verified) or version != account.token_version:
        raise IdentityDenied()
    # Current account role/permissions win; a signed old role is not authority.
    return account
