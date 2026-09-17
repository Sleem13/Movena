from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.utils import timezone
from . import lifecycle, sessions
from .admin_service import MutationDenied
from .models import DataRightsRequest, IdentityEvent, IdentityOutbox
from .test_management import make_account
from rest_framework.test import APIClient


class LifecycleTests(TestCase):
    def setUp(self):
        self.patient = make_account('lifecycle-patient', 101, 'patient')
        self.admin = make_account('lifecycle-root', 102, 'super_admin', is_protected=True)

    def test_patient_request_is_owned_and_open_duplicate_is_idempotent(self):
        row, created = lifecycle.request(self.patient, 'deletion', 'Please remove my account')
        same, repeated = lifecycle.request(self.patient, 'deletion', 'changed text is ignored')
        self.assertTrue(created)
        self.assertFalse(repeated)
        self.assertEqual(row.pk, same.pk)
        self.assertEqual(DataRightsRequest.objects.count(), 1)
        self.assertNotIn(self.patient.email, str(IdentityEvent.objects.values().first()))

    def test_approved_deletion_suspends_and_revokes_but_does_not_erase(self):
        token = sessions.login(self.patient.username, 'كلمة-اختبار-482!')['access_token']
        row, _ = lifecycle.request(self.patient, 'deletion')
        before = timezone.now()
        reviewed = lifecycle.review(self.admin, row.pk, 'approve', 'Identity verified', erasure_delay_days=45)
        self.patient.refresh_from_db()
        self.assertEqual(reviewed.status, 'approved')
        self.assertGreaterEqual(reviewed.retention_until, before + timedelta(days=45))
        self.assertFalse(self.patient.is_active)
        self.assertEqual(self.patient.account_status, 'suspended')
        with self.assertRaises(ValueError): sessions.authenticate(token)
        self.assertTrue(DataRightsRequest.objects.filter(pk=row.pk).exists())
        self.assertEqual(IdentityOutbox.objects.filter(
            event_type='account.projection_requested', aggregate_id=self.patient.pk,
            published_at__isnull=True).count(), 1)
        with self.assertRaises(MutationDenied):
            lifecycle.review(self.admin, row.pk, 'approve', 'Replay review')

    def test_rejection_keeps_account_active_and_audit_failure_rolls_back(self):
        row, _ = lifecycle.request(self.patient, 'export')
        rejected = lifecycle.review(self.admin, row.pk, 'reject', 'Identity could not be verified')
        self.patient.refresh_from_db()
        self.assertEqual(rejected.status, 'rejected')
        self.assertTrue(self.patient.is_active)

        deletion, _ = lifecycle.request(self.patient, 'deletion')
        with patch('identity.lifecycle.event', side_effect=RuntimeError('synthetic audit failure')):
            with self.assertRaises(RuntimeError):
                lifecycle.review(self.admin, deletion.pk, 'approve', 'Identity verified')
        deletion.refresh_from_db(); self.patient.refresh_from_db()
        self.assertEqual(deletion.status, 'pending')
        self.assertTrue(self.patient.is_active)

    def test_non_patient_and_ordinary_admin_are_denied(self):
        therapist = make_account('lifecycle-therapist', 103, 'therapist')
        with self.assertRaises(MutationDenied): lifecycle.request(therapist, 'export')
        row, _ = lifecycle.request(self.patient, 'correction')
        with self.assertRaises(MutationDenied):
            lifecycle.review(therapist, row.pk, 'approve', 'Not authorized')

    @override_settings(ROOT_URLCONF='identity.urls', ACCOUNT_ERASURE_DELAY_DAYS=30)
    def test_http_patient_and_admin_contract(self):
        client = APIClient()
        patient_token = sessions.login(self.patient.username, 'كلمة-اختبار-482!')['access_token']
        client.credentials(HTTP_AUTHORIZATION='Bearer '+patient_token)
        created = client.post('/api/v2/patient/data-rights-requests',
            {'request_type':'deletion','details':'Close my account'}, format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(client.get('/api/v2/patient/data-rights-requests').json()[0]['status'], 'pending')
        admin_token = sessions.login(self.admin.username, 'كلمة-اختبار-482!')['access_token']
        client.credentials(HTTP_AUTHORIZATION='Bearer '+admin_token)
        queue = client.get('/api/v2/admin/platform/data-rights-requests')
        self.assertEqual(len(queue.json()), 1)
        self.assertEqual(queue.json()[0]['account_email'], self.patient.email)
        self.assertEqual(queue.json()[0]['account_id'], self.patient.pk)
        reviewed = client.patch('/api/v2/admin/platform/data-rights-requests/'+created.json()['request_id'],
            {'decision':'approve','reason':'Identity verified'}, format='json')
        self.assertEqual(reviewed.status_code, 200)
        self.assertIsNotNone(reviewed.json()['retention_until'])
