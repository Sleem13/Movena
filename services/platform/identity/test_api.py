from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
import jwt
from .models import Account
from .tests import account_values
from . import sessions


@override_settings(ROOT_URLCONF='identity.urls')
class IdentityContractTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.account = Account.objects.create(**account_values(), credential_owner='platform')

    def test_login_me_logout_contract_and_no_legacy_fallback(self):
        with patch('platform_api.upstream.request') as upstream:
            result = self.client.post('/api/v2/auth/login', {'email':'مريض','password':'كلمة-اختبار-482!'}, format='json')
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result['Cache-Control'], 'no-store')
            self.assertEqual(result.json()['expires_in'], 3600)
            self.client.credentials(HTTP_AUTHORIZATION='Bearer '+result.json()['access_token'])
            me = self.client.get('/api/v2/auth/me')
            self.assertEqual(me.status_code, 200)
            self.assertEqual(me.json()['user_id'], self.account.pk)
            for hidden in ['password_hash','verification_token_hash','reset_password_token_hash','credential_owner']:
                self.assertNotIn(hidden, me.json())
            self.assertEqual(self.client.post('/api/v2/auth/logout').status_code, 200)
            self.assertEqual(self.client.get('/api/v2/auth/me').status_code, 401)
            upstream.assert_not_called()

    def test_recovery_ignores_stale_bearer_and_rejects_reuse(self):
        token = sessions.issue_recovery(self.account.email, 'reset')['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired')
        body = {'token':token, 'new_password':'replacement-482!'}
        self.assertEqual(self.client.post('/api/v2/auth/reset-password', body, format='json').status_code, 200)
        self.assertEqual(self.client.post('/api/v2/auth/reset-password', body, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/v2/auth/login', {'email':'مريض','password':'replacement-482!'}, format='json').status_code, 200)

    def test_staged_records_and_unconfigured_legacy_tokens_cannot_authenticate(self):
        Account.objects.filter(pk=self.account.pk).update(credential_owner='legacy')
        self.assertEqual(self.client.post('/api/v2/auth/login', {'email':'مريض','password':'كلمة-اختبار-482!'}, format='json').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer opaque-old-token')
        self.assertEqual(self.client.get('/api/v2/auth/me').status_code, 401)

    def test_old_jwt_and_new_session_share_revocation(self):
        now = timezone.now()
        key = 'synthetic-http-compatibility-key-'+'x'*32
        old = jwt.encode({'sub':self.account.pk,'role':'super_admin','ver':9,'iat':int(now.timestamp())-3,'exp':int(now.timestamp())+600}, key, algorithm='HS256')
        config = dict(key=key, algorithm='HS256', last_issued_at=now-timedelta(seconds=1), accept_until=now+timedelta(minutes=10))
        new = sessions.login('مريض', 'كلمة-اختبار-482!')['access_token']
        with override_settings(IDENTITY_LEGACY_VALIDATION=config):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer '+old)
            self.assertEqual(self.client.get('/api/v2/auth/me').json()['role'], 'patient')
            self.assertEqual(self.client.post('/api/v2/auth/logout').status_code, 200)
            for token in [old,new]:
                self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
                self.assertEqual(self.client.get('/api/v2/auth/me').status_code, 401)
