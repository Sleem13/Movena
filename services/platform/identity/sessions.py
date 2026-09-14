"""Platform-owned sessions and recovery. Not yet routed as the live identity API.

Single-use imported recovery tokens retain their existing SHA-256 representation.
All mutations condition on credential ownership and the observed account version.
"""
from datetime import timedelta
import hashlib
import json
import re
import secrets
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from .models import Account, AccessSession, IdentityEvent
from .outbox import request_account_projection
from .passwords import verify_password

SESSION_PATTERN = re.compile(r'mv2_[A-Za-z0-9_-]{64}')


class IdentityDenied(ValueError):
    def __init__(self):
        super().__init__('Identity request is unavailable or no longer valid.')


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def profile(account):
    try:
        permissions = json.loads(account.permissions_json)
    except (ValueError, TypeError):
        permissions = []
    return {name: getattr(account, name) for name in (
        'user_id', 'username', 'email', 'full_name', 'role', 'is_active', 'is_verified',
        'account_status', 'is_protected', 'created_at',
    )} | {'permissions': permissions if isinstance(permissions, list) else []}


def eligible(account, require_verified):
    return account is not None and account.credential_owner == 'platform' and account.is_active and account.account_status == 'active' and (account.is_verified or not require_verified)


def observed(account):
    return Account.objects.filter(pk=account.pk, credential_owner='platform',
        password_hash=account.password_hash, token_version=account.token_version,
        is_active=account.is_active, account_status=account.account_status,
        is_verified=account.is_verified, role=account.role)


def event(account, action, now, *, actor_id=None, metadata=None):
    IdentityEvent.objects.create(account=account, actor_id=actor_id, action=action,
        created_at=now, metadata=metadata or {})


def login(identifier, password, *, require_verified=True, lifetime_seconds=3600):
    if not isinstance(identifier, str) or len(identifier) > 320 or not isinstance(password, str) or len(password) > 128 or type(lifetime_seconds) is not int or not 1 <= lifetime_seconds <= 86400:
        raise IdentityDenied()
    try:
        password.encode('utf-8')
    except UnicodeError:
        raise IdentityDenied() from None
    identifier = identifier.strip().lower()
    # An ambiguous email/username collision must never select an arbitrary account.
    candidates = list(Account.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier))[:2])
    account = candidates[0] if len(candidates) == 1 else None
    if account is None:
        make_password(password)  # Avoid a cheap missing-account path for the future endpoint.
        raise IdentityDenied()
    if not eligible(account, require_verified) or not verify_password(password, account.password_hash):
        raise IdentityDenied()
    now = timezone.now()
    replacement = make_password(password) if account.password_hash.startswith('$2') else account.password_hash
    token = 'mv2_' + secrets.token_urlsafe(48)
    with transaction.atomic():
        if observed(account).update(password_hash=replacement, updated_at=now) != 1:
            raise IdentityDenied()
        AccessSession.objects.create(token_digest=digest(token), account=account,
            token_version=account.token_version, created_at=now, expires_at=now+timedelta(seconds=lifetime_seconds))
        event(account, 'session.created', now)
    return {'access_token': token, 'token_type': 'bearer', 'expires_in': lifetime_seconds, 'user': profile(account)}


def authenticate(token, *, require_verified=True):
    if not isinstance(token, str) or not SESSION_PATTERN.fullmatch(token):
        raise IdentityDenied()
    session = AccessSession.objects.select_related('account').filter(token_digest=digest(token), expires_at__gt=timezone.now()).first()
    if session is None or not eligible(session.account, require_verified) or session.token_version != session.account.token_version:
        raise IdentityDenied()
    return session.account


def logout(token, *, require_verified=True):
    account = authenticate(token, require_verified=require_verified)
    revoke_all(account)


def revoke_all(account):
    """Revoke a freshly authenticated account, including a legacy-token principal."""
    now = timezone.now()
    with transaction.atomic():
        if observed(account).update(token_version=F('token_version')+1, updated_at=now) != 1:
            raise IdentityDenied()
        event(account, 'session.revoked_all', now)
        request_account_projection(account, revision=now)


def recovery_token(value):
    if not isinstance(value, str) or not 32 <= len(value) <= 512:
        raise IdentityDenied()
    try:
        return digest(value)
    except UnicodeError:
        raise IdentityDenied() from None


def reset_password(token, new_password, *, require_verified=True):
    try:
        valid = isinstance(new_password, str) and 8 <= len(new_password) <= 128 and len(new_password.encode('utf-8')) <= 72
    except UnicodeError:
        valid = False
    if not valid:
        raise IdentityDenied()
    token_digest = recovery_token(token)
    account = Account.objects.filter(reset_password_token_hash=token_digest).first()
    if not eligible(account, require_verified):
        raise IdentityDenied()
    now = timezone.now()
    with transaction.atomic():
        changed = observed(account).filter(reset_password_token_hash=token_digest, reset_password_expires__gt=now).update(
            password_hash=make_password(new_password), token_version=F('token_version')+1,
            reset_password_token_hash=None, reset_password_expires=None, reset_password_sent_at=None, updated_at=now)
        if changed != 1:
            raise IdentityDenied()
        event(account, 'user.password_recovered', now)
        request_account_projection(account, revision=now)


def verify_email(token):
    token_digest = recovery_token(token)
    account = Account.objects.filter(verification_token_hash=token_digest).first()
    if not eligible(account, False):
        raise IdentityDenied()
    now = timezone.now()
    with transaction.atomic():
        changed = observed(account).filter(verification_token_hash=token_digest, verification_token_expires__gt=now).update(
            is_verified=True, email_verified_at=now, verification_token_hash=None,
            verification_token_expires=None, verification_sent_at=None, updated_at=now)
        if changed != 1:
            raise IdentityDenied()
        event(account, 'user.email_verified', now)
        request_account_projection(account, revision=now)


def issue_recovery(email, purpose, *, require_verified=True, cooldown_seconds=60, lifetime_seconds=3600):
    """Returns a secret only to the delivery adapter, never to a public response.

    None intentionally conflates absent, ineligible and throttled accounts.
    Caller must deliver privately and call delivery_failed on a delivery failure.
    """
    if purpose not in {'verification', 'reset'} or not isinstance(email, str) or not 60 <= lifetime_seconds <= 86400 or not 1 <= cooldown_seconds <= 3600:
        raise IdentityDenied()
    candidates = list(Account.objects.filter(email__iexact=email.strip())[:2])
    account = candidates[0] if len(candidates) == 1 else None
    if not eligible(account, require_verified if purpose == 'reset' else False) or (purpose == 'verification' and account.is_verified):
        return None
    prefix = 'verification' if purpose == 'verification' else 'reset_password'
    hash_field = prefix+'_token_hash'
    expiry_field = 'verification_token_expires' if purpose == 'verification' else 'reset_password_expires'
    sent_field = prefix+'_sent_at'
    now = timezone.now()
    token = secrets.token_urlsafe(48)
    with transaction.atomic():
        changed = observed(account).filter(Q(**{sent_field+'__isnull': True}) | Q(**{sent_field+'__lte': now-timedelta(seconds=cooldown_seconds)})).update(
            **{hash_field: digest(token), expiry_field: now+timedelta(seconds=lifetime_seconds), sent_field: now, 'updated_at': now})
        if changed != 1:
            return None
        event(account, 'recovery.'+purpose+'_issued', now)
    return {'user_id': account.pk, 'email': account.email, 'token': token, 'purpose': purpose}


def delivery_failed(user_id, token, purpose):
    if purpose not in {'verification', 'reset'}:
        raise IdentityDenied()
    prefix = 'verification' if purpose == 'verification' else 'reset_password'
    expiry_field = 'verification_token_expires' if purpose == 'verification' else 'reset_password_expires'
    # Do not erase a newer request's token. Retain cooldown against repeated sends.
    with transaction.atomic():
        changed = Account.objects.filter(pk=user_id, credential_owner='platform', **{prefix+'_token_hash': recovery_token(token)}).update(
            **{prefix+'_token_hash': None, expiry_field: None})
        if changed:
            IdentityEvent.objects.create(account_id=user_id, action='recovery.delivery_failed', created_at=timezone.now())
