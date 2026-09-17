from datetime import timedelta
from unittest.mock import patch
import jwt
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from .models import Account, AccessSession, IdentityEvent
from .tests import account_values
from . import sessions
from .legacy_sessions import authenticate_legacy

PASSWORD = 'كلمة-اختبار-482!'


class SessionTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(**account_values(), credential_owner='platform')

    def test_login_upgrades_hash_stores_only_digest_and_logout_revokes_all(self):
        first = sessions.login('مريض', PASSWORD)
        second = sessions.login('FIXTURE@EXAMPLE.TEST', PASSWORD)
        self.assertEqual(sessions.authenticate(first['access_token']).pk, self.account.pk)
        self.assertEqual(first['user']['permissions'], ['analysis:read:own'])
        self.assertNotIn('password_hash', first['user'])
        self.account.refresh_from_db()
        self.assertTrue(self.account.password_hash.startswith('pbkdf2_sha256$'))
        self.assertEqual(AccessSession.objects.count(), 2)
        self.assertFalse(AccessSession.objects.filter(token_digest=first['access_token']).exists())
        self.assertEqual(len(AccessSession.objects.first().token_digest), 64)
        sessions.logout(first['access_token'])
        for token in [first['access_token'], second['access_token']]:
            with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
        self.assertEqual(IdentityEvent.objects.filter(action='session.revoked_all').count(), 1)

    def test_expiry_suspension_verification_and_ownership_fail_closed(self):
        token = sessions.login('مريض', PASSWORD)['access_token']
        for values in [dict(is_active=False), dict(account_status='suspended'), dict(is_verified=False), dict(credential_owner='legacy')]:
            Account.objects.filter(pk=self.account.pk).update(**values)
            with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
            with self.assertRaises(sessions.IdentityDenied): sessions.login('مريض', PASSWORD)
            Account.objects.filter(pk=self.account.pk).update(is_active=True, account_status='active', is_verified=True, credential_owner='platform')
        AccessSession.objects.update(expires_at=timezone.now()-timedelta(seconds=1))
        with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
        for malformed in [None, 'mv2_invalid', 'other-token', 'mv2_'+'a'*65]:
            with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(malformed)

    def test_reset_token_is_single_use_and_revokes_existing_sessions(self):
        access = sessions.login('مريض', PASSWORD)['access_token']
        # Represents an unexpired link issued by the old service and imported.
        token = 'existing-imported-reset-token-'+'x'*32
        Account.objects.filter(pk=self.account.pk).update(reset_password_token_hash=sessions.digest(token), reset_password_expires=timezone.now()+timedelta(minutes=5))
        sessions.reset_password(token, 'replacement-482!')
        with self.assertRaises(sessions.IdentityDenied): sessions.reset_password(token, 'another-value')
        with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(access)
        with self.assertRaises(sessions.IdentityDenied): sessions.login('مريض', PASSWORD)
        self.assertTrue(sessions.login('مريض', 'replacement-482!')['access_token'])
        self.account.refresh_from_db()
        self.assertIsNone(self.account.reset_password_token_hash)
        self.assertEqual(self.account.token_version, 10)

    def test_recovery_cooldown_failure_and_newer_token_survives_old_failure(self):
        delivery = sessions.issue_recovery('fixture@example.test', 'reset')
        self.assertIsNotNone(delivery)
        self.assertIsNone(sessions.issue_recovery('fixture@example.test', 'reset'))
        self.assertIsNone(sessions.issue_recovery('absent@example.test', 'reset'))
        sessions.delivery_failed(self.account.pk, delivery['token'], 'reset')
        self.account.refresh_from_db()
        self.assertIsNone(self.account.reset_password_token_hash)
        self.assertIsNotNone(self.account.reset_password_sent_at)
        Account.objects.filter(pk=self.account.pk).update(reset_password_sent_at=timezone.now()-timedelta(minutes=2))
        newer = sessions.issue_recovery('fixture@example.test', 'reset')
        sessions.delivery_failed(self.account.pk, delivery['token'], 'reset')
        self.account.refresh_from_db()
        self.assertEqual(self.account.reset_password_token_hash, sessions.digest(newer['token']))
        events = str(list(IdentityEvent.objects.values()))
        self.assertNotIn(delivery['token'], events)
        self.assertNotIn(newer['token'], events)
        self.assertNotIn(self.account.email, events)

    def test_verification_and_reset_expiry_and_wrong_purpose(self):
        Account.objects.filter(pk=self.account.pk).update(is_verified=False)
        delivery = sessions.issue_recovery('fixture@example.test', 'verification')
        self.assertIsNone(sessions.issue_recovery('fixture@example.test', 'reset'))
        with self.assertRaises(sessions.IdentityDenied): sessions.reset_password(delivery['token'], 'new-password')
        sessions.verify_email(delivery['token'])
        with self.assertRaises(sessions.IdentityDenied): sessions.verify_email(delivery['token'])
        reset = sessions.issue_recovery('fixture@example.test', 'reset')
        Account.objects.filter(pk=self.account.pk).update(reset_password_expires=timezone.now()-timedelta(seconds=1))
        with self.assertRaises(sessions.IdentityDenied): sessions.reset_password(reset['token'], 'new-password')
        self.assertEqual(IdentityEvent.objects.filter(action='user.email_verified').count(), 1)

    def test_concurrent_reset_prevents_stale_login_and_event_failure_rolls_back(self):
        new_hash = make_password('replacement-482!')
        def race(password):
            Account.objects.filter(pk=self.account.pk).update(password_hash=new_hash, token_version=10)
            return make_password(password)
        with patch('identity.sessions.make_password', side_effect=race):
            with self.assertRaises(sessions.IdentityDenied): sessions.login('مريض', PASSWORD)
        self.assertFalse(AccessSession.objects.exists())
        token = 'fixture-reset-token-'+'x'*32
        Account.objects.filter(pk=self.account.pk).update(reset_password_token_hash=sessions.digest(token), reset_password_expires=timezone.now()+timedelta(minutes=5))
        with patch('identity.sessions.event', side_effect=RuntimeError('Synthetic audit failure')):
            with self.assertRaises(RuntimeError): sessions.reset_password(token, 'next-password')
        self.account.refresh_from_db()
        self.assertEqual(self.account.password_hash, new_hash)
        self.assertEqual(self.account.reset_password_token_hash, sessions.digest(token))

    def test_ambiguous_identifier_and_invalid_new_password_never_write(self):
        Account.objects.create(**account_values(user_id='other', legacy_id=8, username='other', email='FIXTURE@example.test',
            verification_token_hash=None, reset_password_token_hash=None), credential_owner='platform')
        with self.assertRaises(sessions.IdentityDenied): sessions.login('fixture@example.test', PASSWORD)
        self.assertIsNone(sessions.issue_recovery('fixture@example.test', 'reset'))
        for invalid in ['', 'short', 'ع'*37, '\ud800'*8]:
            with self.assertRaises(sessions.IdentityDenied): sessions.reset_password('x'*64, invalid)
        self.assertFalse(AccessSession.objects.exists())
        self.assertFalse(IdentityEvent.objects.exists())
        with self.assertRaises(sessions.IdentityDenied): sessions.login('absent@example.test', '\ud800')


class LegacySessionTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(**account_values(), credential_owner='platform')
        self.key = 'synthetic-key-for-unit-tests-only-'+'x'*32
        self.now = timezone.now()
        self.options = dict(key=self.key, algorithm='HS256', last_issued_at=self.now-timedelta(seconds=1), accept_until=self.now+timedelta(hours=1))

    def token(self, **values):
        claims = dict(sub=self.account.pk, iat=int((self.now-timedelta(seconds=3)).timestamp()), exp=int((self.now+timedelta(minutes=10)).timestamp()), ver=9, role='super_admin')
        return jwt.encode(claims | values, self.key, algorithm='HS256')

    def test_existing_signature_uses_current_role_and_revocation_version(self):
        token = self.token()
        current = authenticate_legacy(token, **self.options)
        self.assertEqual(current.role, 'patient')
        Account.objects.filter(pk=self.account.pk).update(token_version=10)
        with self.assertRaises(sessions.IdentityDenied): authenticate_legacy(token, **self.options)

    def test_expired_forged_new_issuer_and_wrong_algorithm_are_denied(self):
        tokens = [self.token(exp=int((self.now-timedelta(seconds=1)).timestamp())),
                  self.token(iat=int((self.now+timedelta(seconds=20)).timestamp())),
                  self.token(ver='9'), self.token(ver=True),
                  jwt.encode({'sub': self.account.pk, 'exp': int(self.now.timestamp())+600}, self.key, algorithm='HS256'),
                  jwt.encode({'sub': self.account.pk, 'iat': int(self.now.timestamp())-3, 'exp': int(self.now.timestamp())+600, 'ver': 9}, self.key, algorithm='HS512')]
        for token in tokens:
            with self.assertRaises(sessions.IdentityDenied): authenticate_legacy(token, **self.options)
        for options in [dict(key='wrong-key-'+'z'*40), dict(accept_until=self.now), dict(last_issued_at=self.now-timedelta(days=1)), dict(algorithm='none')]:
            with self.assertRaises(sessions.IdentityDenied): authenticate_legacy(self.token(), **(self.options | options))
