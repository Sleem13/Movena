"""Atomic identity snapshot import from a read-only SQLite backup.

No normalization, role recomputation, plaintext credentials or source writes.
Repeated identical imports are safe; changed snapshots require a new rehearsal DB.
"""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from contextlib import closing
from django.db import models, transaction
from .models import Account, Consent


class SnapshotError(ValueError):
    pass


def fields_for(model):
    return [field for field in model._meta.concrete_fields
            if field.name not in {'credential_owner', 'policy_url'} and not (field.primary_key and field.auto_created)]


def identity_lookup(model, values):
    return {'pk': values['user_id']} if model is Account else {'legacy_id': values['legacy_id']}


def source_column(field):
    return 'id' if field.name == 'legacy_id' else 'user_id' if field.name == 'account' else field.name


def convert(field, value):
    if value is None:
        if not field.null:
            raise SnapshotError('Required identity value is missing.')
        return None
    if isinstance(field, models.DateTimeField):
        parsed = datetime.fromisoformat(value)
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    if isinstance(field, models.BooleanField):
        if value not in (0, 1):
            raise SnapshotError('Invalid identity boolean.')
        return bool(value)
    if isinstance(field, models.IntegerField):
        if not isinstance(value, int):
            raise SnapshotError('Invalid identity integer.')
    elif not isinstance(value, str) or (field.max_length and len(value) > field.max_length):
        raise SnapshotError('Invalid identity text value.')
    return value


def read_rows(source, table, model):
    fields = fields_for(model)
    expected = {source_column(field) for field in fields}
    columns = {row['name'] for row in source.execute(f'PRAGMA table_info("{table}")')}
    if columns != expected:
        raise SnapshotError('Identity source schema differs from the reviewed mapping.')
    return [{field.attname: convert(field, row[source_column(field)]) for field in fields}
            for row in source.execute(f'SELECT * FROM "{table}"')]


def import_snapshot(path, *, persist=False):
    path = Path(path).resolve()
    if not path.is_file():
        raise SnapshotError('Identity snapshot is not a file.')
    try:
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as source:
            source.row_factory = sqlite3.Row
            source.execute('BEGIN')
            if source.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise SnapshotError('Source integrity check failed.')
            if source.execute('PRAGMA foreign_key_check').fetchone() is not None:
                raise SnapshotError('Source relationship check failed.')
            accounts = read_rows(source, 'users', Account)
            consents = read_rows(source, 'user_consents', Consent)
        identifiers = {row['user_id'] for row in accounts}
        if any(row['account_id'] not in identifiers for row in consents):
            raise SnapshotError('Consent references an absent identity.')
        with transaction.atomic():
            inserted = 0
            for model, rows in [(Account, accounts), (Consent, consents)]:
                for values in rows:
                    existing = model.objects.filter(**identity_lookup(model, values)).first()
                    if existing:
                        if any(getattr(existing, name) != value for name, value in values.items()):
                            raise SnapshotError('Target identity differs; use a new rehearsal database.')
                        if isinstance(existing, Account) and existing.credential_owner != 'legacy':
                            raise SnapshotError('Target identity ownership has already changed.')
                    else:
                        model.objects.create(**values)
                        inserted += 1
                if model.objects.count() != len(rows):
                    raise SnapshotError('Target contains identities outside this snapshot.')
                # Re-read persisted values before accepting; timestamps compare as UTC.
                for values in rows:
                    saved = model.objects.get(**identity_lookup(model, values))
                    if any(getattr(saved, name) != value for name, value in values.items()):
                        raise SnapshotError('Identity field verification failed.')
            if not persist:
                transaction.set_rollback(True)
        return {'verified': True, 'accounts': len(accounts), 'consents': len(consents),
                'inserted': inserted, 'persisted': persist, 'credential_owner': 'legacy',
                'source_opened_read_only': True, 'all_mapped_fields_equal': True,
                'live_authentication_changed': False}
    except SnapshotError:
        raise
    except Exception:
        # DB exceptions can contain row values (hashes, recovery tokens, PII).
        raise SnapshotError('Identity snapshot import failed; no partial import was committed.') from None
