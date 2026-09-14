from datetime import timedelta
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .admin_service import MutationDenied, require_super_admin, reason_value
from .models import Account, DataRightsRequest
from .outbox import request_account_projection
from .sessions import eligible, event, observed

TYPES = {'export', 'correction', 'deletion'}
OPEN = {'pending', 'approved'}


def request(account, request_type, details=None):
    if not eligible(account, True) or account.role != 'patient' or request_type not in TYPES:
        raise MutationDenied()
    if details is not None and (not isinstance(details, str) or len(details.strip()) > 2000):
        raise MutationDenied()
    with transaction.atomic():
        locked = Account.objects.select_for_update().get(pk=account.pk)
        existing = DataRightsRequest.objects.filter(account=locked, request_type=request_type,
            status__in=OPEN).order_by('-requested_at').first()
        if existing:
            return existing, False
        now = timezone.now()
        row = DataRightsRequest.objects.create(account=locked, request_type=request_type,
            details=details.strip() if details and details.strip() else None,
            status='pending', requested_at=now)
        event(locked, 'data_rights.requested', now, actor_id=locked.pk,
              metadata={'request_id':str(row.pk), 'request_type':request_type})
    return row, True


def review(actor, request_id, decision, reason, *, erasure_delay_days=30):
    require_super_admin(actor); reason = reason_value(reason)
    if decision not in {'approve', 'reject'} or type(erasure_delay_days) is not int or not 1 <= erasure_delay_days <= 3650:
        raise MutationDenied()
    now = timezone.now()
    with transaction.atomic():
        row = DataRightsRequest.objects.select_related('account').select_for_update().filter(pk=request_id).first()
        if row is None or row.status != 'pending' or row.account.is_protected:
            raise MutationDenied()
        row.status = 'approved' if decision == 'approve' else 'rejected'
        row.reviewed_at, row.reviewed_by_id, row.review_reason = now, actor.pk, reason
        fields = ['status','reviewed_at','reviewed_by_id','review_reason']
        if decision == 'approve' and row.request_type == 'deletion':
            row.retention_until = now + timedelta(days=erasure_delay_days); fields.append('retention_until')
            if observed(row.account).update(is_active=False, account_status='suspended',
                    token_version=F('token_version')+1, updated_at=now) != 1:
                raise MutationDenied()
            request_account_projection(row.account, revision=now)
        row.save(update_fields=fields)
        event(row.account, 'data_rights.reviewed', now, actor_id=actor.pk,
              metadata={'request_id':str(row.pk), 'request_type':row.request_type, 'decision':decision})
    row.refresh_from_db(); return row


def serialize(row):
    return {'request_id':str(row.pk), 'request_type':row.request_type, 'status':row.status,
        'details':row.details, 'created_at':row.requested_at, 'completed_at':row.completed_at,
        'reviewed_at':row.reviewed_at, 'retention_until':row.retention_until}
