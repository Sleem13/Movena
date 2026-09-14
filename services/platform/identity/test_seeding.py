from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from .models import AccessSession, Account, IdentityEvent, IdentityOutbox
from .provisioning import ProvisioningDenied
from .seeding import seed_protected_superadmin
from .sessions import authenticate, login
from .tests import account_values


class ProtectedSeedTests(TestCase):
    values = ('root@example.test', 'root.owner', 'Root Owner', 'Root-password-482!')

    def test_create_is_protected_idempotent_and_redacted(self):
        account, changed = seed_protected_superadmin(*self.values)
        self.assertTrue(changed and account.is_protected)
        self.assertEqual(account.role, 'super_admin')
        self.assertEqual(account.legacy_id, None)
        same, changed = seed_protected_superadmin(*self.values)
        self.assertFalse(changed)
        self.assertEqual(same.pk, account.pk)
        self.assertEqual(IdentityOutbox.objects.filter(
            event_type='account.projection_requested', aggregate_id=account.pk).count(), 1)
        rendered = str(list(IdentityEvent.objects.values()) + list(IdentityOutbox.objects.values()))
        self.assertNotIn(self.values[3], rendered)

    def test_reset_revokes_sessions_and_cannot_promote_existing_account(self):
        account, _ = seed_protected_superadmin(*self.values)
        token = login(self.values[1], self.values[3])['access_token']
        reset, changed = seed_protected_superadmin(*self.values[:-1], 'Replacement-root-593!', reset=True)
        self.assertTrue(changed)
        self.assertGreater(reset.token_version, account.token_version)
        with self.assertRaises(ValueError):
            authenticate(token)
        self.assertTrue(login(self.values[1], 'Replacement-root-593!'))

        Account.objects.create(**account_values(user_id='legacy-root', legacy_id=90,
            username='legacy.root', email='legacy@example.test', role='admin'), credential_owner='legacy')
        with self.assertRaises(ProvisioningDenied):
            seed_protected_superadmin('legacy@example.test', 'legacy.root', 'Legacy', 'Another-root-482!', reset=True)

    def test_command_requires_explicit_environment(self):
        with self.assertRaises(CommandError):
            call_command('seed_protected_superadmin')
