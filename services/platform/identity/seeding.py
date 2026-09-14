"""Explicit protected-root provisioning outside public and administrator APIs."""
import json
from uuid import uuid4
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from .admin_service import ROLE_PERMISSIONS
from .models import Account
from .outbox import request_account_projection
from .provisioning import ProvisioningDenied, email_value, password_value, text, username_value
from .sessions import event, observed


def seed_protected_superadmin(email, username, full_name, password, *, reset=False):
    email = email_value(email)
    username = username_value(username)
    full_name = text(full_name, 1, 120)
    password = password_value(password)
    if type(reset) is not bool:
        raise ProvisioningDenied()
    matches = list(Account.objects.filter(Q(email__iexact=email) | Q(username__iexact=username))[:2])
    if len(matches) > 1:
        raise ProvisioningDenied()
    existing = matches[0] if matches else None
    if existing is not None:
        if (existing.email.lower() != email or (existing.username or '').lower() != username
            or existing.credential_owner != 'platform' or existing.role != 'super_admin'
            or not existing.is_protected):
            raise ProvisioningDenied()
        if not reset:
            return existing, False
    now = timezone.now()
    with transaction.atomic():
        if existing is None:
            account = Account.objects.create(user_id=str(uuid4()), legacy_id=None,
                username=username, email=email, full_name=full_name,
                password_hash=make_password(password), role='super_admin',
                permissions_json=json.dumps(ROLE_PERMISSIONS['super_admin'], separators=(',', ':')),
                is_active=True, is_verified=True, account_status='active', is_protected=True,
                token_version=0, email_verified_at=now, created_at=now, updated_at=now,
                credential_owner='platform')
            action = 'superadmin.seeded'
        else:
            changed = observed(existing).update(password_hash=make_password(password), full_name=full_name,
                is_active=True, is_verified=True, account_status='active',
                token_version=F('token_version')+1, updated_at=now)
            if changed != 1:
                raise ProvisioningDenied()
            account = existing
            action = 'superadmin.seed_reset'
        event(account, action, now, actor_id=account.pk,
              metadata={'existing_sessions_revoked': existing is not None})
        request_account_projection(account, revision=now)
    account.refresh_from_db()
    return account, True
