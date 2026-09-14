from django.db import models
from uuid import uuid4


class Account(models.Model):
    """Preserved identity record. Importing does not transfer credential ownership."""
    user_id = models.CharField(primary_key=True, max_length=36)
    legacy_id = models.BigIntegerField(null=True, unique=True)
    username = models.CharField(max_length=64, null=True, unique=True)
    email = models.CharField(max_length=320, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=120, null=True)
    role = models.CharField(max_length=32)
    is_active = models.BooleanField()
    is_verified = models.BooleanField()
    account_status = models.CharField(max_length=32)
    is_protected = models.BooleanField()
    token_version = models.IntegerField()
    permissions_json = models.TextField()
    email_verified_at = models.DateTimeField(null=True)
    verification_token_hash = models.CharField(max_length=64, null=True, unique=True)
    verification_token_expires = models.DateTimeField(null=True)
    verification_sent_at = models.DateTimeField(null=True)
    reset_password_token_hash = models.CharField(max_length=64, null=True, unique=True)
    reset_password_expires = models.DateTimeField(null=True)
    reset_password_sent_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    credential_owner = models.CharField(max_length=16, default='legacy')


class Consent(models.Model):
    legacy_id = models.BigIntegerField(null=True, unique=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, db_column='user_id')
    consent_type = models.CharField(max_length=64)
    accepted = models.BooleanField()
    accepted_at = models.DateTimeField(null=True)
    version = models.CharField(max_length=32)
    notes = models.TextField(null=True)
    policy_url = models.URLField(max_length=2048, null=True)


class AccessSession(models.Model):
    """Opaque session secrets are returned once; only their digests are retained."""
    token_digest = models.CharField(primary_key=True, max_length=64)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    token_version = models.IntegerField()
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField(db_index=True)


class IdentityEvent(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    actor_id = models.CharField(max_length=36, null=True)
    action = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    metadata = models.JSONField(default=dict)


class IdentityOutbox(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event_type = models.CharField(max_length=64)
    aggregate_id = models.CharField(max_length=36)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['event_type','aggregate_id'], name='unique_identity_domain_request')]


class DataRightsRequest(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    request_type = models.CharField(max_length=24)
    status = models.CharField(max_length=24, default='pending')
    details = models.TextField(null=True)
    requested_at = models.DateTimeField()
    reviewed_at = models.DateTimeField(null=True)
    reviewed_by_id = models.CharField(max_length=36, null=True)
    review_reason = models.TextField(null=True)
    retention_until = models.DateTimeField(null=True)
    downstream_status = models.JSONField(default=dict)
    completed_at = models.DateTimeField(null=True)
