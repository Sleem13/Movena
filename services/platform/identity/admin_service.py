"""Platform-owned account mutations. These are not live-routed before cutover."""
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import Account, Consent
from .sessions import IdentityDenied, event, observed
from .outbox import request_account_projection, request_patient_profile

ROLE_PERMISSIONS = {
    'super_admin': ['*'],
    'admin': ['analysis:create', 'analysis:read:any', 'session:manage:any', 'patient:manage', 'dashboard:therapist'],
    'therapist': ['analysis:create', 'analysis:read:assigned', 'session:manage:assigned', 'patient:manage:assigned', 'dashboard:therapist'],
    'patient': ['analysis:create', 'analysis:read:own', 'session:manage:own'],
    'support': ['support:account-status', 'support:appointments:metadata'],
    'researcher_demo': ['analysis:create', 'analysis:read:own', 'session:manage:own'],
}
ACCOUNT_STATUSES = {'active', 'paused', 'suspended'}


class MutationDenied(IdentityDenied):
    pass


def require_super_admin(actor):
    if actor is None or actor.credential_owner != 'platform' or not actor.is_active or actor.account_status != 'active' or actor.role != 'super_admin':
        raise MutationDenied()


def target_for_change(actor, user_id):
    require_super_admin(actor)
    target = Account.objects.filter(pk=user_id).first()
    if target is None or target.credential_owner != 'platform' or target.is_protected or target.role == 'super_admin':
        raise MutationDenied()
    return target


def reason_value(reason):
    if not isinstance(reason, str) or not 3 <= len(reason.strip()) <= 500:
        raise MutationDenied()
    return reason.strip()


def change_status(actor, user_id, status, reason):
    target = target_for_change(actor, user_id)
    reason = reason_value(reason)
    if status not in ACCOUNT_STATUSES:
        raise MutationDenied()
    now = timezone.now()
    if target.account_status == status and target.is_active == (status == 'active'):
        with transaction.atomic():
            event(target, 'user.status_changed', now, actor_id=actor.pk,
                  metadata={'from': target.account_status, 'to': status, 'reason': reason})
        return target
    with transaction.atomic():
        changed = observed(target).update(account_status=status, is_active=status == 'active',
            token_version=F('token_version')+1, updated_at=now)
        if changed != 1:
            raise MutationDenied()
        event(target, 'user.status_changed', now, actor_id=actor.pk,
              metadata={'from': target.account_status, 'to': status, 'reason': reason})
        request_account_projection(target, revision=now)
    target.refresh_from_db()
    return target


def change_role(actor, user_id, role, reason):
    target = target_for_change(actor, user_id)
    reason = reason_value(reason)
    if role not in ROLE_PERMISSIONS or role == 'super_admin':
        raise MutationDenied()
    if target.role == role:
        with transaction.atomic():
            event(target, 'user.role_changed', timezone.now(), actor_id=actor.pk,
                  metadata={'from': target.role, 'to': role, 'reason': reason})
            if role == 'patient':
                request_patient_profile(target)
        return target
    now = timezone.now()
    import json
    permissions = json.dumps(ROLE_PERMISSIONS[role], separators=(',', ':'))
    with transaction.atomic():
        changed = observed(target).update(role=role, permissions_json=permissions,
            token_version=F('token_version')+1, updated_at=now)
        if changed != 1:
            raise MutationDenied()
        event(target, 'user.role_changed', now, actor_id=actor.pk,
              metadata={'from': target.role, 'to': role, 'reason': reason})
        if role == 'patient':
            request_patient_profile(target)
        request_account_projection(target, revision=now)
    target.refresh_from_db()
    return target


def admin_reset_password(actor, user_id, password, reason):
    target = target_for_change(actor, user_id)
    reason = reason_value(reason)
    try:
        valid = isinstance(password, str) and 8 <= len(password) <= 128 and len(password.encode('utf-8')) <= 72
    except UnicodeError:
        valid = False
    if not valid:
        raise MutationDenied()
    now = timezone.now()
    replacement = make_password(password)
    with transaction.atomic():
        changed = observed(target).update(password_hash=replacement,
            token_version=F('token_version')+1, reset_password_token_hash=None,
            reset_password_expires=None, reset_password_sent_at=None, updated_at=now)
        if changed != 1:
            raise MutationDenied()
        event(target, 'user.password_reset', now, actor_id=actor.pk,
              metadata={'reason': reason, 'existing_sessions_revoked': True})
        request_account_projection(target, revision=now)
    target.refresh_from_db()
    return target


def policy_value(allowed_versions, consent_type):
    value=allowed_versions.get(consent_type)
    return (value.get('version'),value.get('url')) if isinstance(value,dict) else (value,None)


def set_consent(account, consent_type, accepted, version, *, allowed_versions):
    approved_version, policy_url = policy_value(allowed_versions, consent_type)
    if (account is None or account.credential_owner != 'platform' or account.role != 'patient'
        or not account.is_active or account.account_status != 'active' or type(accepted) is not bool
        or not isinstance(consent_type, str) or not isinstance(version, str)
        or approved_version != version):
        raise MutationDenied()
    now = timezone.now()
    with transaction.atomic():
        row = Consent.objects.filter(account=account, consent_type=consent_type, version=version).order_by('-legacy_id').first()
        if row is None:
            row = Consent.objects.create(legacy_id=None, account=account,
                consent_type=consent_type, accepted=accepted,
                accepted_at=now if accepted else None, version=version, policy_url=policy_url)
        elif row.accepted != accepted:
            row.accepted = accepted
            row.accepted_at = now if accepted else None
            row.save(update_fields=['accepted', 'accepted_at'])
        event(account, 'consent.updated', now, actor_id=account.pk,
              metadata={'consent_type': consent_type, 'version': version, 'accepted': accepted})
    return row
