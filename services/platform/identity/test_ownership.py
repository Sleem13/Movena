import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase, override_settings
from .importer import import_snapshot, SnapshotError
from .models import Account, IdentityEvent, IdentityOutbox
from .ownership import transfer_snapshot
from .projection import publish_pending
from .sessions import login
from .tests import account_values, write_source


class OwnershipTransferTests(TestCase):
    @override_settings(IDENTITY_TRANSFER_CONFIRMATION='transfer-confirmation-'+'x'*32)
    def test_snapshot_bound_dry_run_and_atomic_execution(self):
        with TemporaryDirectory() as directory:
            source=Path(directory)/'source.sqlite3'
            user_id=str(uuid4())
            values=account_values(user_id=user_id,legacy_id=71,username='transfer.patient',
                email='transfer@example.test',verification_token_hash=None,reset_password_token_hash=None)
            write_source(source,accounts=[values],consents=[])
            import_snapshot(source,persist=True)
            dry=transfer_snapshot(source)
            self.assertFalse(dry['executed'])
            self.assertEqual(Account.objects.get().credential_owner,'legacy')
            with self.assertRaises(SnapshotError):
                transfer_snapshot(source,execute=True,confirmation='wrong')
            result=transfer_snapshot(source,execute=True,confirmation='transfer-confirmation-'+'x'*32)
            account=Account.objects.get()
            self.assertTrue(result['executed'])
            self.assertEqual(account.credential_owner,'platform')
            self.assertEqual(account.token_version,values['token_version']+1)
            self.assertTrue(login(account.username,'كلمة-اختبار-482!'))
            intent=IdentityOutbox.objects.get(event_type='account.ownership_transfer_requested')
            self.assertEqual(intent.payload['source_sha256'],result['source_sha256'])
            rendered=json.dumps(result)+str(IdentityEvent.objects.values().first())
            self.assertNotIn(values['password_hash'],rendered)
            self.assertNotIn(values['email'],rendered)

    @patch('identity.projection.transfer_legacy_owner')
    def test_transfer_intent_uses_dedicated_publisher(self, send):
        account=Account.objects.create(**account_values(user_id=str(uuid4())),credential_owner='platform')
        IdentityOutbox.objects.create(event_type='account.ownership_transfer_requested',aggregate_id=account.pk,
            payload={'user_id':account.pk,'revision':'r','source_sha256':'a'*64},created_at=account.updated_at)
        self.assertEqual(publish_pending()['published'],1)
        send.assert_called_once_with(account)

    @override_settings(IDENTITY_TRANSFER_CONFIRMATION='transfer-confirmation-'+'x'*32,
                       IDENTITY_MODE='transition')
    def test_execution_is_denied_after_transition_routing_is_enabled(self):
        with TemporaryDirectory() as directory:
            source=Path(directory)/'source.sqlite3'
            write_source(source,accounts=[account_values(user_id=str(uuid4()))],consents=[])
            import_snapshot(source,persist=True)
            with self.assertRaises(SnapshotError):
                transfer_snapshot(source,execute=True,confirmation='transfer-confirmation-'+'x'*32)
            self.assertEqual(Account.objects.get().credential_owner,'legacy')
