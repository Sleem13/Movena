"""Legacy bcrypt is raw UTF-8, not Django's bcrypt_sha256 format."""
import re
import bcrypt
from django.contrib.auth.hashers import check_password, make_password
from .models import Account

LEGACY_BCRYPT = re.compile(r'\$2[aby]\$(0[4-9]|[12][0-9]|3[01])\$[./A-Za-z0-9]{53}')


def verify_password(password, encoded):
    if not isinstance(password, str) or not isinstance(encoded, str):
        return False
    try:
        raw = password.encode('utf-8')
        if encoded.startswith('$2'):
            # Match the installed legacy bcrypt 5 behavior: never truncate.
            return len(raw) <= 72 and bool(LEGACY_BCRYPT.fullmatch(encoded)) and bcrypt.checkpw(raw, encoded.encode('ascii'))
        return check_password(password, encoded)
    except (ValueError, TypeError, UnicodeError, AssertionError):
        return False


def upgrade_password_after_transfer(user_id, password, *, require_verified=True):
    """Future cutover hook, not a login endpoint. CAS protects concurrent resets.

    No importer or public API can change credential_owner to platform.
    A separate, rehearsed ownership transfer must precede use of this hook.
    """
    account = Account.objects.get(pk=user_id)
    if account.credential_owner != 'platform':
        raise PermissionError('Identity ownership has not transferred.')
    if not account.is_active or account.account_status != 'active' or (require_verified and not account.is_verified):
        return False
    if not verify_password(password, account.password_hash):
        return False
    replacement = make_password(password)
    return Account.objects.filter(
        pk=user_id, credential_owner='platform', password_hash=account.password_hash,
        token_version=account.token_version, is_active=True, account_status='active',
        is_verified=account.is_verified,
    ).update(password_hash=replacement) == 1
