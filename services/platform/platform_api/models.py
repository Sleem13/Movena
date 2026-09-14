from django.db import models


class SubmissionReceipt(models.Model):
    """Only v2 request receipts are owned here. No raw media or credentials."""
    owner_id = models.CharField(max_length=128)
    key = models.CharField(max_length=128)
    scope = models.CharField(max_length=255)
    fingerprint = models.CharField(max_length=64)
    state = models.CharField(max_length=16, default='pending')
    status_code = models.PositiveSmallIntegerField(null=True)
    response = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner_id', 'key', 'scope'], name='unique_owned_submission')]


class AnalysisJobRecord(models.Model):
    """Replacement-owned lifecycle record while processing remains in the adapter."""
    job_id = models.CharField(primary_key=True, max_length=36)
    owner_id = models.CharField(max_length=36, db_index=True)
    exercise_id = models.CharField(max_length=64)
    status = models.CharField(max_length=24, db_index=True)
    outcome = models.CharField(max_length=24, null=True)
    stage = models.CharField(max_length=64)
    progress = models.PositiveSmallIntegerField()
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=0)
    cancel_requested = models.BooleanField(default=False)
    error_code = models.CharField(max_length=128, null=True)
    message = models.TextField(null=True)
    http_status = models.PositiveSmallIntegerField(null=True)
    result = models.JSONField(null=True)
    engine_version = models.CharField(max_length=128, null=True)
    model_version = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    last_synced_at = models.DateTimeField(auto_now=True)
