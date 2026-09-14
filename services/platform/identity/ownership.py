"""Explicit snapshot-bound credential ownership transfer; never called by HTTP."""
from contextlib import closing
import hashlib
import hmac
import sqlite3
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .importer import SnapshotError, identity_lookup, read_rows
from .models import Account, Consent
from .outbox import request_ownership_transfer
from .sessions import event


def transfer_snapshot(path, *, execute=False, confirmation=None):
    source_path = Path(path).resolve()
    if not source_path.is_file():
        raise SnapshotError('Identity snapshot is not a file.')
    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    try:
        with closing(sqlite3.connect(source_path.as_uri()+'?mode=ro', uri=True)) as source:
            source.row_factory = sqlite3.Row
            if source.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise SnapshotError('Source integrity check failed.')
            if source.execute('PRAGMA foreign_key_check').fetchone() is not None:
                raise SnapshotError('Source relationship check failed.')
            accounts = read_rows(source, 'users', Account)
            consents = read_rows(source, 'user_consents', Consent)
        with transaction.atomic():
            locked = {row.pk:row for row in Account.objects.select_for_update().all()}
            if set(locked) != {row['user_id'] for row in accounts} or Consent.objects.count() != len(consents):
                raise SnapshotError('Target identity set differs from the reviewed snapshot.')
            for values in accounts:
                target = locked[values['user_id']]
                if target.credential_owner != 'legacy' or any(getattr(target, name) != value for name,value in values.items()):
                    raise SnapshotError('Target identity differs or ownership has already changed.')
            for values in consents:
                target = Consent.objects.filter(**identity_lookup(Consent, values)).first()
                if target is None or any(getattr(target, name) != value for name,value in values.items()):
                    raise SnapshotError('Target consent differs from the reviewed snapshot.')
            expected = getattr(settings, 'IDENTITY_TRANSFER_CONFIRMATION', '')
            if execute:
                if (getattr(settings, 'IDENTITY_MODE', 'legacy') != 'legacy' or len(expected) < 32
                    or not isinstance(confirmation, str) or not hmac.compare_digest(expected, confirmation)
                    or hashlib.sha256(source_path.read_bytes()).hexdigest() != source_sha256):
                    raise SnapshotError('Identity ownership transfer confirmation failed.')
                now = timezone.now()
                for target in locked.values():
                    previous_version = target.token_version
                    target.credential_owner = 'platform'
                    target.token_version = previous_version + 1
                    target.updated_at = now
                    target.save(update_fields=['credential_owner','token_version','updated_at'])
                    request_ownership_transfer(target, revision=now, source_sha256=source_sha256)
                    event(target, 'identity.ownership_transferred', now, actor_id=None,
                          metadata={'source_sha256':source_sha256, 'previous_token_version':previous_version})
            else:
                transaction.set_rollback(True)
        return {'verified':True, 'accounts':len(accounts), 'consents':len(consents),
            'source_sha256':source_sha256, 'executed':execute,
            'token_versions_incremented':len(accounts) if execute else 0,
            'ownership_after':'platform' if execute else 'legacy', 'source_opened_read_only':True}
    except SnapshotError:
        raise
    except Exception:
        raise SnapshotError('Identity ownership transfer failed; no partial transfer was committed.') from None
