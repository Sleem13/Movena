"""Reserve before dispatch. Ambiguous upstream outcomes never dispatch twice."""
import hashlib
import re
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException
from .models import SubmissionReceipt


class SubmissionConflict(APIException):
    status_code = 409
    default_code = 'submission_conflict'
    default_detail = 'This submission is still being resolved. Retry with the same request key.'


def reserve(owner, key, scope, fingerprint):
    if not key or not re.fullmatch(r'[a-zA-Z0-9_-]{8,128}', key):
        error = SubmissionConflict('A stable Idempotency-Key is required for this submission.')
        error.status_code = 400
        raise error
    try:
        with transaction.atomic():
            row = SubmissionReceipt.objects.create(owner_id=owner, key=key, scope=scope, fingerprint=fingerprint)
        return row, False
    except IntegrityError:
        row = SubmissionReceipt.objects.get(owner_id=owner, key=key, scope=scope)
        if row.fingerprint != fingerprint:
            raise SubmissionConflict('This request key was already used for a different submission.')
        if row.state != 'completed':
            raise SubmissionConflict()
        return row, True


def fingerprint_upload(request, query):
    """Hash actual file bytes, not randomized multipart boundary bytes."""
    digest = hashlib.sha256(query.encode())
    for name in sorted(request.FILES):
        upload = request.FILES[name]
        digest.update(name.encode())
        digest.update(upload.name.encode())
        for chunk in upload.chunks():
            digest.update(chunk)
        upload.seek(0)
    if not request.FILES:
        digest.update(request.body)
    return digest.hexdigest()
