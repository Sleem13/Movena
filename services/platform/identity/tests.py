import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import bcrypt
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from .importer import import_snapshot, SnapshotError, fields_for, source_column
from .models import Account, Consent
from .passwords import verify_password, upgrade_password_after_transfer


def account_values(**changes):
    values = {field.attname: None for field in fields_for(Account)}
    values.update(user_id='fixture-user', legacy_id=7, username='مريض', email='fixture@example.test',
                  password_hash=bcrypt.hashpw('كلمة-اختبار-482!'.encode(), bcrypt.gensalt(rounds=4)).decode(),
                  role='patient', is_active=True, is_verified=True, account_status='active',
                  is_protected=False, token_version=9, permissions_json='["analysis:read:own"]',
                  verification_token_hash='a'*64, verification_token_expires=datetime(2026, 9, 20, tzinfo=timezone.utc),
                  reset_password_token_hash='b'*64, reset_password_expires=datetime(2026, 9, 21, tzinfo=timezone.utc),
                  created_at=datetime(2025, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc))
    values.update(changes)
    return values


def write_source(path, accounts=None, consents=None):
    accounts = accounts if accounts is not None else [account_values()]
    consents = consents if consents is not None else [dict(legacy_id=11, account_id='fixture-user',
        consent_type='privacy', accepted=False, accepted_at=None, version='fixture-v1', notes=None)]
    with closing(sqlite3.connect(path)) as db, db:
        for table, model, rows in [('users', Account, accounts), ('user_consents', Consent, consents)]:
            fields = fields_for(model)
            names = [source_column(field) for field in fields]
            db.execute(f'CREATE TABLE {table} (' + ','.join(f'"{name}"' for name in names) + ')')
            for values in rows:
                row = [values[field.attname] for field in fields]
                row = [v.isoformat() if isinstance(v, datetime) else v for v in row]
                db.execute(f'INSERT INTO {table} VALUES (' + ','.join('?' for _ in names) + ')', row)


class IdentityTests(TestCase):
    def test_bcrypt_unicode_boundaries_and_malformed_hashes(self):
        for password in ['كلمة-اختبار-482!', 'a'*72]:
            encoded = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4)).decode()
            self.assertTrue(verify_password(password, encoded))
            self.assertFalse(verify_password(password+'x', encoded))
            self.assertFalse(verify_password('incorrect', encoded))
        for value in [None, 'broken', '$2b$99$'+'a'*53, '$2x$04$'+'a'*53]:
            self.assertFalse(verify_password('password', value))
        self.assertFalse(verify_password('\ud800', '$2b$04$'+'a'*53))

    def test_upgrade_requires_transferred_ownership_and_keeps_identity(self):
        account = Account.objects.create(**account_values())
        with self.assertRaises(PermissionError):
            upgrade_password_after_transfer(account.pk, 'كلمة-اختبار-482!')
        original = account.password_hash
        Account.objects.filter(pk=account.pk).update(credential_owner='platform')
        self.assertFalse(upgrade_password_after_transfer(account.pk, 'wrong'))
        self.assertTrue(upgrade_password_after_transfer(account.pk, 'كلمة-اختبار-482!'))
        account.refresh_from_db()
        self.assertNotEqual(original, account.password_hash)
        self.assertTrue(account.password_hash.startswith('pbkdf2_sha256$'))
        self.assertTrue(verify_password('كلمة-اختبار-482!', account.password_hash))
        self.assertEqual(account.token_version, 9)
        self.assertEqual(account.permissions_json, '["analysis:read:own"]')

    def test_inactive_unverified_and_concurrent_reset_cannot_upgrade(self):
        account = Account.objects.create(**account_values(), credential_owner='platform')
        for values in [dict(is_active=False), dict(account_status='suspended'), dict(is_verified=False)]:
            Account.objects.filter(pk=account.pk).update(**values)
            self.assertFalse(upgrade_password_after_transfer(account.pk, 'كلمة-اختبار-482!'))
            Account.objects.filter(pk=account.pk).update(is_active=True, account_status='active', is_verified=True)
        reset_hash = make_password('new-fixture-password')
        def concurrent_reset(password):
            Account.objects.filter(pk=account.pk).update(password_hash=reset_hash, token_version=10)
            return make_password(password)
        with patch('identity.passwords.make_password', side_effect=concurrent_reset):
            self.assertFalse(upgrade_password_after_transfer(account.pk, 'كلمة-اختبار-482!'))
        account.refresh_from_db()
        self.assertEqual(account.password_hash, reset_hash)
        self.assertEqual(account.token_version, 10)

    def test_copy_import_preserves_all_values_and_repeat_is_noop(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)/'source.sqlite3'
            write_source(source)
            digest = hashlib.sha256(source.read_bytes()).digest()
            result = import_snapshot(source, persist=True)
            self.assertTrue(result['all_mapped_fields_equal'])
            self.assertEqual(result['inserted'], 2)
            self.assertEqual(import_snapshot(source, persist=True)['inserted'], 0)
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), digest)
            account = Account.objects.get()
            self.assertTrue(verify_password('كلمة-اختبار-482!', account.password_hash))
            self.assertEqual(account.username, 'مريض')
            self.assertEqual(account.credential_owner, 'legacy')
            self.assertFalse(Consent.objects.get().accepted)
            self.assertEqual(Consent.objects.get().account_id, account.pk)
            report = json.dumps(result)
            for secret in [account.username, account.email, account.password_hash, 'a'*64, 'b'*64]:
                self.assertNotIn(secret, report)

    def test_dry_run_leaves_no_rows_and_conflict_rolls_back_everything(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)/'source.sqlite3'
            write_source(source)
            self.assertFalse(import_snapshot(source)['persisted'])
            self.assertFalse(Account.objects.exists())
            self.assertFalse(Consent.objects.exists())
            Account.objects.create(**account_values(email='different@example.test'))
            with self.assertRaises(SnapshotError):
                import_snapshot(source, persist=True)
            self.assertEqual(Account.objects.get().email, 'different@example.test')
            self.assertFalse(Consent.objects.exists())

    def test_schema_drift_or_orphan_consent_blocks_even_dry_run(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)/'source.sqlite3'
            write_source(source)
            with closing(sqlite3.connect(source)) as db, db:
                db.execute("UPDATE user_consents SET user_id='missing'")
            with self.assertRaises(SnapshotError):
                import_snapshot(source)
            self.assertFalse(Account.objects.exists())
            with closing(sqlite3.connect(source)) as db, db:
                db.execute('ALTER TABLE users ADD COLUMN unknown_identity_field TEXT')
            with self.assertRaises(SnapshotError):
                import_snapshot(source)

    def test_duplicate_identity_failure_is_atomic_and_redacted(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)/'source.sqlite3'
            write_source(source, accounts=[account_values(), account_values(user_id='second', legacy_id=8)])
            with self.assertRaises(SnapshotError) as error:
                import_snapshot(source, persist=True)
            self.assertNotIn('fixture@example.test', str(error.exception))
            self.assertFalse(Account.objects.exists())
