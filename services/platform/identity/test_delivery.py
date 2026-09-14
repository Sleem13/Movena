from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from .models import Account


POLICIES = {
    'terms': {'version':'terms-v1', 'url':'https://policies.example.test/terms'},
    'privacy': {'version':'privacy-v1', 'url':'https://policies.example.test/privacy'},
}


@override_settings(ROOT_URLCONF='identity.urls', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   DEFAULT_FROM_EMAIL='care@example.test', FRONTEND_URL='https://app.example.test',
                   IDENTITY_POLICIES=POLICIES, IDENTITY_REQUIRE_VERIFICATION=True)
class DeliveryContractTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.body = {'username':'new.patient', 'email':'new@example.test', 'full_name':'New Patient',
            'password':'Patient-password-482!', 'role':'patient',
            'accepted_terms':True, 'accepted_privacy':True}

    def token_from_last_mail(self):
        url = mail.outbox[-1].body.split(': ', 1)[1].splitlines()[0]
        return parse_qs(urlparse(url).query)['token'][0]

    def test_registration_delivers_verification_then_generic_reset(self):
        created = self.client.post('/api/v2/auth/register', self.body, format='json')
        self.assertEqual(created.status_code, 201)
        self.assertFalse(created.json()['is_verified'])
        self.assertNotIn('token', str(created.json()).lower())
        self.assertEqual(len(mail.outbox), 1)
        token = self.token_from_last_mail()
        self.assertEqual(self.client.post('/api/v2/auth/verify-email', {'token':token}, format='json').status_code, 200)

        known = self.client.post('/api/v2/auth/forgot-password', {'email':self.body['email']}, format='json')
        unknown = self.client.post('/api/v2/auth/forgot-password', {'email':'absent@example.test'}, format='json')
        self.assertEqual((known.status_code, known.json()), (unknown.status_code, unknown.json()))
        self.assertEqual(len(mail.outbox), 2)
        reset = self.token_from_last_mail()
        changed = self.client.post('/api/v2/auth/reset-password',
            {'token':reset, 'new_password':'Replacement-password-593!'}, format='json')
        self.assertEqual(changed.status_code, 200)

    def test_resend_obeys_cooldown_without_revealing_account(self):
        self.client.post('/api/v2/auth/register', self.body, format='json')
        first_count = len(mail.outbox)
        known = self.client.post('/api/v2/auth/resend-verification', {'email':self.body['email']}, format='json')
        unknown = self.client.post('/api/v2/auth/resend-verification', {'email':'absent@example.test'}, format='json')
        self.assertEqual(known.json(), unknown.json())
        self.assertEqual(len(mail.outbox), first_count)
        Account.objects.filter(email=self.body['email']).update(
            verification_sent_at=timezone.now()-timedelta(minutes=2))
        self.client.post('/api/v2/auth/resend-verification', {'email':self.body['email']}, format='json')
        self.assertEqual(len(mail.outbox), first_count+1)

    @patch('identity.delivery.send_mail', side_effect=RuntimeError('synthetic transport failure'))
    def test_delivery_failure_clears_secret_and_returns_no_secret(self, _send):
        response = self.client.post('/api/v2/auth/register', self.body, format='json')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error_code'], 'EMAIL_DELIVERY_FAILED')
        account = Account.objects.get(email=self.body['email'])
        self.assertIsNone(account.verification_token_hash)
        self.assertNotIn(self.body['password'], str(response.json()))

    @override_settings(IDENTITY_POLICIES={})
    def test_registration_stays_closed_without_approved_policies(self):
        response = self.client.post('/api/v2/auth/register', self.body, format='json')
        self.assertEqual(response.status_code, 503)
        self.assertFalse(Account.objects.exists())
