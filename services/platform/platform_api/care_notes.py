"""Validate the additive visit-note surface before reserving a write receipt."""
import re
from rest_framework.exceptions import ValidationError


def validate_request(request, path):
    if request.method != 'POST' or not re.fullmatch(r'therapist/appointments/[^/]+/session-notes', path):
        return
    value = request.data
    if not isinstance(value, dict):
        raise ValidationError('A visit note must be an object.')
    summary = value.get('summary')
    recommendation = value.get('recommendations')
    if not isinstance(summary, str) or not summary.strip() or len(summary) > 10000:
        raise ValidationError('Enter a visit summary of 1–10000 characters.')
    if recommendation is not None and (not isinstance(recommendation, str) or len(recommendation) > 10000):
        raise ValidationError('Recommendations must contain at most 10000 characters.')
    if not isinstance(value.get('patient_visible', False), bool):
        raise ValidationError('Patient visibility must be an explicit boolean.')
