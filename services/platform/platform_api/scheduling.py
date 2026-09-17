"""Compatibility boundary for scheduling; legacy remains the authoritative writer."""
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from rest_framework.exceptions import ValidationError


def validate_request(request, path):
    if request.method == 'POST' and path == 'scheduling/appointments':
        if not re.fullmatch(r'[A-Za-z0-9_-]{8,128}', request.headers.get('Idempotency-Key', '')):
            raise ValidationError({'detail': 'A stable Idempotency-Key is required to book an appointment.'})
    if request.method == 'POST' and path == 'therapist/availability':
        if not isinstance(request.data, dict):
            raise ValidationError({'detail': 'An availability object is required.'})
        name = request.data.get('timezone_name', 'Africa/Cairo')
        try:
            ZoneInfo(name)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            raise ValidationError({'detail': 'Choose a valid IANA timezone, such as Africa/Cairo or UTC.'})


def normalize_timestamps(data):
    """Legacy database timestamps are UTC. Never apply the server's local zone."""
    if isinstance(data, list):
        return [normalize_timestamps(row) for row in data]
    if not isinstance(data, dict):
        return data
    result = dict(data)
    for key in ['starts_at', 'ends_at', 'expires_at']:
        if isinstance(result.get(key), str):
            try:
                value = datetime.fromisoformat(result[key].replace('Z', '+00:00'))
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                result[key] = value.isoformat()
            except ValueError:
                pass  # Preserve unavailable/invalid source values; do not invent a time.
    if isinstance(result.get('slots'), list):
        result['slots'] = normalize_timestamps(result['slots'])
    return result


def is_calendar_path(path):
    return path.startswith('scheduling/') or path in {'patient/appointments', 'therapist/appointments', 'admin/appointments'}
