from django.test import TestCase
from .backfill import transition_intents
from .models import IdentityOutbox
from .test_management import make_account


class TransitionBackfillTests(TestCase):
    def test_dry_run_and_additive_repeat(self):
        patient = make_account('backfill-patient', 201, 'patient')
        make_account('backfill-therapist', 202, 'therapist')
        make_account('backfill-legacy', 203, 'patient', credential_owner='legacy')
        dry = transition_intents()
        self.assertEqual(dry['platform_accounts'], 2)
        self.assertEqual(dry['missing_projection_intents'], 2)
        self.assertEqual(dry['missing_patient_profile_intents'], 1)
        self.assertFalse(IdentityOutbox.objects.exists())
        applied = transition_intents(persist=True)
        self.assertTrue(applied['persisted'])
        self.assertEqual(IdentityOutbox.objects.count(), 3)
        repeated = transition_intents(persist=True)
        self.assertEqual(repeated['missing_projection_intents'], 0)
        self.assertEqual(repeated['missing_patient_profile_intents'], 0)
        self.assertEqual(IdentityOutbox.objects.filter(aggregate_id=patient.pk).count(), 2)
        self.assertFalse(repeated['credential_ownership_changed'])
