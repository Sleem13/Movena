from unittest.mock import patch
from django.test import TestCase
from . import provisioning, sessions, admin_service
from .models import Account, Consent, IdentityEvent, IdentityOutbox
from .test_management import make_account


VALUES={'username':'مستخدم_جديد','email':'new@example.test','full_name':'مستخدم تجريبي','password':'Secure-Only-482!'}
POLICIES={
    'terms':{'version':'approved-terms-v1','url':'https://policies.example.test/terms'},
    'privacy':{'version':'approved-privacy-v1','url':'https://policies.example.test/privacy'},
}


class ProvisioningTests(TestCase):
    def test_public_patient_is_unverified_with_policies_and_private_delivery(self):
        result=provisioning.create(VALUES,role='patient',policies=POLICIES,
            accepted_terms=True,accepted_privacy=True)
        account=result.account
        self.assertIsNone(account.legacy_id)
        self.assertFalse(account.is_verified)
        self.assertEqual(account.credential_owner,'platform')
        self.assertEqual(account.verification_token_hash,sessions.digest(result.verification_delivery['token']))
        self.assertNotEqual(account.verification_token_hash,result.verification_delivery['token'])
        self.assertEqual({row.consent_type for row in Consent.objects.all()},{'terms','privacy'})
        self.assertTrue(all(row.accepted and row.policy_url.startswith('https://') for row in Consent.objects.all()))
        outbox=IdentityOutbox.objects.get(event_type='patient_profile.requested')
        self.assertEqual(outbox.event_type,'patient_profile.requested')
        self.assertEqual(outbox.payload,{'user_id':account.pk})
        rendered=str(list(IdentityEvent.objects.values())+list(IdentityOutbox.objects.values()))
        for secret in [VALUES['password'],result.verification_delivery['token'],VALUES['email'],VALUES['full_name']]:
            self.assertNotIn(secret,rendered)

    def test_missing_or_unapproved_policy_and_privileged_public_role_fail(self):
        invalid=[({},True,True), (POLICIES,False,True),
            ({**POLICIES,'privacy':{'version':'draft','url':'http://example.test/privacy'}},True,True)]
        for policies,terms,privacy in invalid:
            with self.assertRaises(provisioning.ProvisioningDenied):
                provisioning.create(VALUES,role='patient',policies=policies,
                    accepted_terms=terms,accepted_privacy=privacy)
        for role in ['admin','therapist','support','researcher_demo','super_admin']:
            with self.assertRaises(provisioning.ProvisioningDenied):
                provisioning.create(VALUES,role=role,policies=POLICIES,accepted_terms=True,accepted_privacy=True)
        self.assertFalse(Account.objects.exists())

    def test_admin_creation_requires_current_superadmin_and_no_policy_acceptance(self):
        actor=make_account('root-admin',50,'super_admin',is_protected=True)
        result=provisioning.create(VALUES,role='therapist',actor=actor)
        self.assertTrue(result.account.is_verified)
        self.assertIsNone(result.verification_delivery)
        self.assertFalse(Consent.objects.exists())
        self.assertEqual(IdentityOutbox.objects.filter(
            event_type='account.projection_requested', aggregate_id=result.account.pk).count(), 1)
        ordinary=make_account('ordinary',51,'admin')
        with self.assertRaises(provisioning.ProvisioningDenied):
            provisioning.create({**VALUES,'email':'second@example.test','username':'second'},role='patient',actor=ordinary)

    def test_duplicate_and_audit_failure_are_atomic_and_redacted(self):
        provisioning.create(VALUES,role='patient',policies=POLICIES,accepted_terms=True,accepted_privacy=True)
        with self.assertRaises(provisioning.ProvisioningDenied) as failure:
            provisioning.create({**VALUES,'username':'another'},role='patient',policies=POLICIES,
                accepted_terms=True,accepted_privacy=True)
        self.assertNotIn(VALUES['email'],str(failure.exception))
        before=(Account.objects.count(),Consent.objects.count(),IdentityOutbox.objects.count())
        with patch('identity.provisioning.event',side_effect=RuntimeError('Synthetic audit failure')):
            with self.assertRaises(RuntimeError):
                provisioning.create({**VALUES,'email':'unique@example.test','username':'unique'},role='patient',
                    policies=POLICIES,accepted_terms=True,accepted_privacy=True)
        self.assertEqual((Account.objects.count(),Consent.objects.count(),IdentityOutbox.objects.count()),before)

    def test_patient_role_outbox_is_idempotent_for_replayed_role_change(self):
        actor=make_account('root-admin',60,'super_admin',is_protected=True)
        target=make_account('target-user',61,'therapist')
        admin_service.change_role(actor,target.pk,'patient','Convert to patient')
        target.refresh_from_db()
        admin_service.change_role(actor,target.pk,'patient','Confirm patient role')
        self.assertEqual(IdentityOutbox.objects.filter(aggregate_id=target.pk).count(),2)
        self.assertEqual(IdentityOutbox.objects.filter(
            event_type='account.projection_requested', aggregate_id=target.pk).count(),1)
