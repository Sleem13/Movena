"""Repair transition intents without changing identity ownership or account data."""
from django.db import transaction
from .models import Account, IdentityOutbox
from .outbox import request_account_projection, request_patient_profile


def transition_intents(*, persist=False):
    accounts = Account.objects.filter(credential_owner='platform').order_by('user_id')
    missing_projection = [row for row in accounts if not IdentityOutbox.objects.filter(
        event_type='account.projection_requested', aggregate_id=row.pk).exists()]
    patients = accounts.filter(role='patient')
    missing_profiles = [row for row in patients if not IdentityOutbox.objects.filter(
        event_type='patient_profile.requested', aggregate_id=row.pk).exists()]
    with transaction.atomic():
        if persist:
            for account in missing_projection:
                request_account_projection(account)
            for account in missing_profiles:
                request_patient_profile(account)
        else:
            transaction.set_rollback(True)
    return {'platform_accounts': accounts.count(), 'platform_patients': patients.count(),
        'missing_projection_intents': len(missing_projection),
        'missing_patient_profile_intents': len(missing_profiles), 'persisted': persist,
        'credential_ownership_changed': False}
