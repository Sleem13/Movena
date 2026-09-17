"""Push the current non-secret account projection through the private bridge."""
import json
import httpx
import hashlib
from django.conf import settings
from platform_api import upstream
from .models import Account
from .models import IdentityOutbox
from .sessions import profile


def payload(account):
    public = profile(account)
    return {name: public[name] for name in ('user_id','username','email','full_name','role','is_active',
        'is_verified','account_status','is_protected')} | {
        'token_version': account.token_version, 'permissions': public['permissions']}


def project(account):
    if account.credential_owner != 'platform':
        raise ValueError('Only platform-owned accounts may be projected')
    body = json.dumps(payload(account), sort_keys=True, separators=(',', ':')).encode()
    path = '/internal/v1/identity/accounts/'+account.pk
    token = upstream.signed_assertion('identity-projector', 0, 'PUT', path, body)
    # Keep this header construction local to avoid exposing a generic arbitrary-subject interface.
    with httpx.Client(timeout=10, follow_redirects=False, trust_env=False) as client:
        response = client.put(settings.LEGACY_API_URL+path, content=body,
            headers={'Authorization':'MovenaInternal '+token, 'Content-Type':'application/json', 'Accept':'application/json'})
    if response.status_code != 200:
        raise upstream.UpstreamUnavailable()
    return response.json()


def transfer_legacy_owner(account):
    if account.credential_owner != 'platform' or account.legacy_id is None or account.token_version < 1:
        raise ValueError('Account is not eligible for legacy ownership conversion')
    envelope = {'account':payload(account), 'expected_legacy_token_version':account.token_version-1,
        'legacy_password_hash_sha256':hashlib.sha256(account.password_hash.encode('utf-8')).hexdigest()}
    body=json.dumps(envelope,sort_keys=True,separators=(',',':')).encode()
    path='/internal/v1/identity/ownership-transfers/'+account.pk
    token=upstream.signed_assertion('identity-transfer',0,'PUT',path,body)
    with httpx.Client(timeout=10,follow_redirects=False,trust_env=False) as client:
        response=client.put(settings.LEGACY_API_URL+path,content=body,
            headers={'Authorization':'MovenaInternal '+token,'Content-Type':'application/json','Accept':'application/json'})
    if response.status_code != 200:
        raise upstream.UpstreamUnavailable()
    return response.json()


def publish_pending(*, limit=100):
    """Publish latest projections; a concurrent replacement stays pending."""
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('Invalid projection batch size')
    published = failed = 0
    rows = list(IdentityOutbox.objects.filter(event_type__in=[
        'account.projection_requested','account.ownership_transfer_requested'],
        published_at__isnull=True).order_by('created_at')[:limit])
    from django.db.models import F
    from django.utils import timezone
    for row in rows:
        expected = row.payload
        account = Account.objects.filter(pk=row.aggregate_id, credential_owner='platform').first()
        if account is None:
            IdentityOutbox.objects.filter(pk=row.pk, payload=expected, published_at__isnull=True).update(attempts=F('attempts')+1)
            failed += 1
            continue
        try:
            transfer_legacy_owner(account) if row.event_type == 'account.ownership_transfer_requested' else project(account)
        except Exception:
            IdentityOutbox.objects.filter(pk=row.pk, payload=expected, published_at__isnull=True).update(attempts=F('attempts')+1)
            failed += 1
            continue
        changed = IdentityOutbox.objects.filter(pk=row.pk, payload=expected,
            published_at__isnull=True).update(published_at=timezone.now(), attempts=F('attempts')+1)
        published += changed
    return {'selected': len(rows), 'published': published, 'failed': failed}
