"""Transactional account provisioning; public routing remains disabled."""
import json
import secrets
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urlparse
from uuid import uuid4
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.utils import timezone
from .admin_service import ROLE_PERMISSIONS, MutationDenied, require_super_admin
from .models import Account, Consent
from .outbox import request_account_projection, request_patient_profile
from .sessions import digest, event


class ProvisioningDenied(ValueError):
    pass


@dataclass(frozen=True)
class Provisioned:
    account: Account
    verification_delivery: dict | None


def text(value, minimum, maximum):
    if not isinstance(value, str):
        raise ProvisioningDenied()
    value=value.strip()
    if not minimum <= len(value) <= maximum:
        raise ProvisioningDenied()
    return value


def username_value(value):
    value=text(value,3,64).lower()
    if not all(character.isalnum() or character in '._-' for character in value):
        raise ProvisioningDenied()
    return value


def email_value(value):
    value=text(value,3,320).lower()
    if '@' not in value or value.startswith('@') or value.endswith('@'):
        raise ProvisioningDenied()
    return value


def password_value(value):
    if not isinstance(value,str) or not 8 <= len(value) <= 128:
        raise ProvisioningDenied()
    try:
        if len(value.encode('utf-8')) > 72:
            raise ProvisioningDenied()
    except UnicodeError:
        raise ProvisioningDenied() from None
    return value


def policy(value):
    if not isinstance(value,dict):
        raise ProvisioningDenied()
    version=text(value.get('version'),1,32)
    url=text(value.get('url'),8,2048)
    parsed=urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ProvisioningDenied()
    return version,url


def create(values, *, role, actor=None, policies=None, accepted_terms=False, accepted_privacy=False,
           verification_lifetime_seconds=86400):
    if role not in ROLE_PERMISSIONS or role == 'super_admin':
        raise ProvisioningDenied()
    if actor is None:
        if role != 'patient' or not accepted_terms or not accepted_privacy:
            raise ProvisioningDenied()
        terms=policy((policies or {}).get('terms'))
        privacy=policy((policies or {}).get('privacy'))
    else:
        try:
            require_super_admin(actor)
        except MutationDenied:
            raise ProvisioningDenied() from None
        terms=privacy=None
    username=username_value(values.get('username'))
    email=email_value(values.get('email'))
    full_name=text(values.get('full_name'),1,120)
    password=password_value(values.get('password'))
    now=timezone.now()
    if type(verification_lifetime_seconds) is not int or not 60 <= verification_lifetime_seconds <= 172800:
        raise ProvisioningDenied()
    verification_token = secrets.token_urlsafe(48) if actor is None else None
    try:
        with transaction.atomic():
            account=Account.objects.create(user_id=str(uuid4()), legacy_id=None,
                username=username,email=email,full_name=full_name,password_hash=make_password(password),
                role=role,permissions_json=json.dumps(ROLE_PERMISSIONS[role],separators=(',',':')),
                is_active=True,is_verified=actor is not None,account_status='active',is_protected=False,
                token_version=0,email_verified_at=now if actor is not None else None,
                verification_token_hash=digest(verification_token) if verification_token else None,
                verification_token_expires=now+timedelta(seconds=verification_lifetime_seconds) if verification_token else None,
                verification_sent_at=now if verification_token else None,
                created_at=now,updated_at=now,credential_owner='platform')
            if terms:
                for consent_type,(version,url) in [('terms',terms),('privacy',privacy)]:
                    Consent.objects.create(account=account,consent_type=consent_type,accepted=True,
                        accepted_at=now,version=version,policy_url=url)
            if role == 'patient':
                request_patient_profile(account)
            request_account_projection(account, revision=now)
            event(account,'user.created',now,actor_id=actor.pk if actor else account.pk,
                  metadata={'role':role,'source':'administrator' if actor else 'public'})
        delivery = {'user_id':account.pk,'email':account.email,'token':verification_token,
                    'purpose':'verification'} if verification_token else None
        return Provisioned(account,delivery)
    except (IntegrityError, ValueError, TypeError):
        raise ProvisioningDenied() from None
