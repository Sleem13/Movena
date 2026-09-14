"""Input guards for legacy identity. No credential ownership transfer."""
from rest_framework.exceptions import ValidationError


def validate_request(request, path):
    if request.method != 'POST' or path not in {'auth/register', 'auth/reset-password'}:
        return
    if not isinstance(request.data, dict):
        raise ValidationError({'detail': 'An account request object is required.'})
    password = request.data.get('password' if path == 'auth/register' else 'new_password')
    # Legacy bcrypt accepts at most 72 UTF-8 bytes. Never truncate new secrets.
    if isinstance(password, str) and len(password.encode('utf-8')) > 72:
        raise ValidationError({'detail': 'The password must be at most 72 UTF-8 bytes.'})
