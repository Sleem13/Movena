from django.utils import timezone
from .models import IdentityOutbox


def request_patient_profile(account):
    row,_ = IdentityOutbox.objects.get_or_create(event_type='patient_profile.requested',
        aggregate_id=account.pk, defaults={'payload':{'user_id':account.pk},'created_at':timezone.now()})
    return row


def request_account_projection(account, *, revision=None):
    """Record latest-state intent without placing account attributes in the outbox."""
    revision = revision or account.updated_at
    row, _ = IdentityOutbox.objects.update_or_create(
        event_type='account.projection_requested', aggregate_id=account.pk,
        defaults={'payload': {'user_id': account.pk, 'revision': revision.isoformat()},
                  'created_at': timezone.now(), 'published_at': None, 'attempts': 0})
    return row


def request_ownership_transfer(account, *, revision, source_sha256):
    row, _ = IdentityOutbox.objects.update_or_create(
        event_type='account.ownership_transfer_requested', aggregate_id=account.pk,
        defaults={'payload': {'user_id':account.pk, 'revision':revision.isoformat(),
                              'source_sha256':source_sha256},
                  'created_at':timezone.now(), 'published_at':None, 'attempts':0})
    return row
