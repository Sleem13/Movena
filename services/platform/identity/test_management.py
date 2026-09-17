import json
from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from . import admin_service, sessions
from .models import Account, Consent, IdentityEvent
from .tests import account_values

PASSWORD = 'كلمة-اختبار-482!'


def make_account(user_id, legacy_id, role, **changes):
    values = account_values(user_id=user_id, legacy_id=legacy_id, username=user_id,
        email=user_id+'@example.test', role=role, verification_token_hash=None,
        reset_password_token_hash=None)
    values.update(credential_owner='platform')
    values.update(changes)
    return Account.objects.create(**values)


class ManagementTests(TestCase):
    def setUp(self):
        self.actor = make_account('root-admin', 20, 'super_admin', is_protected=True)
        self.target = make_account('target-user', 21, 'therapist')

    def test_status_role_and_password_revoke_sessions_and_record_actor(self):
        token = sessions.login(self.target.username, PASSWORD)['access_token']
        admin_service.change_status(self.actor, self.target.pk, 'paused', 'Requested leave')
        with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)
        admin_service.change_status(self.actor, self.target.pk, 'active', 'Returned to work')
        token = sessions.login(self.target.username, PASSWORD)['access_token']
        admin_service.change_role(self.actor, self.target.pk, 'patient', 'Care account conversion')
        with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
        self.target.refresh_from_db()
        self.assertEqual(json.loads(self.target.permissions_json), admin_service.ROLE_PERMISSIONS['patient'])
        token = sessions.login(self.target.username, PASSWORD)['access_token']
        admin_service.admin_reset_password(self.actor, self.target.pk, 'replacement-482!', 'Authorized recovery')
        with self.assertRaises(sessions.IdentityDenied): sessions.authenticate(token)
        self.assertTrue(sessions.login(self.target.username, 'replacement-482!'))
        events = list(IdentityEvent.objects.values('actor_id','action','metadata'))
        managed = [row for row in events if row['action'].startswith('user.')]
        self.assertTrue(all(row['actor_id'] == self.actor.pk for row in managed))
        self.assertEqual(IdentityEvent.objects.filter(action='user.status_changed').count(), 2)
        self.target.refresh_from_db()
        version=self.target.token_version
        admin_service.change_role(self.actor,self.target.pk,'patient','Confirmed current role')
        self.target.refresh_from_db()
        self.assertEqual(self.target.token_version,version)
        self.assertEqual(IdentityEvent.objects.filter(action='user.role_changed').count(),2)

    def test_protected_superadmin_legacy_and_nonadmin_targets_are_denied(self):
        legacy = make_account('legacy-user', 22, 'patient', credential_owner='legacy')
        ordinary = make_account('ordinary-admin', 23, 'admin')
        for actor, target in [(ordinary,self.target),(self.actor,self.actor),(self.actor,legacy)]:
            for operation, args in [(admin_service.change_status,('paused','reason value')),
                (admin_service.change_role,('patient','reason value')),
                (admin_service.admin_reset_password,('replacement-482!','reason value'))]:
                with self.assertRaises(admin_service.MutationDenied): operation(actor,target.pk,*args)
        self.assertFalse(IdentityEvent.objects.exists())

    def test_race_and_audit_failure_roll_back_management_change(self):
        def race(password):
            Account.objects.filter(pk=self.target.pk).update(token_version=100)
            return 'new-hash'
        with patch('identity.admin_service.make_password', side_effect=race):
            with self.assertRaises(admin_service.MutationDenied):
                admin_service.admin_reset_password(self.actor,self.target.pk,'replacement-482!','Authorized reset')
        self.target.refresh_from_db()
        self.assertEqual(self.target.token_version,100)
        original=self.target.account_status
        with patch('identity.admin_service.event',side_effect=RuntimeError('Synthetic audit failure')):
            with self.assertRaises(RuntimeError): admin_service.change_status(self.actor,self.target.pk,'paused','Requested leave')
        self.target.refresh_from_db()
        self.assertEqual(self.target.account_status,original)

    def test_consent_requires_current_approved_version_and_preserves_import_id(self):
        patient = make_account('patient-user',24,'patient')
        existing=Consent.objects.create(legacy_id=40,account=patient,consent_type='privacy',accepted=True,version='old')
        with self.assertRaises(admin_service.MutationDenied):
            admin_service.set_consent(patient,'privacy',True,'draft',allowed_versions={'privacy':'approved-v2'})
        row=admin_service.set_consent(patient,'privacy',True,'approved-v2',allowed_versions={'privacy':'approved-v2'})
        self.assertIsNone(row.legacy_id)
        self.assertEqual(Consent.objects.get(pk=existing.pk).legacy_id,40)
        same=admin_service.set_consent(patient,'privacy',False,'approved-v2',allowed_versions={'privacy':'approved-v2'})
        self.assertEqual(same.pk,row.pk)
        self.assertFalse(same.accepted)
        self.assertIsNone(same.accepted_at)
        self.assertEqual(IdentityEvent.objects.filter(action='consent.updated').count(),2)


@override_settings(ROOT_URLCONF='identity.urls', IDENTITY_CONSENT_VERSIONS={'privacy':'approved-v2'})
class ManagementContractTests(TestCase):
    def setUp(self):
        self.client=APIClient()
        self.actor=make_account('root-admin',30,'super_admin',is_protected=True)
        self.target=make_account('target-user',31,'therapist')

    def authorize(self, account, password=PASSWORD):
        token=sessions.login(account.username,password)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        return token

    def test_admin_http_mutations_use_current_authority_and_revoke_target(self):
        target_token=sessions.login(self.target.username,PASSWORD)['access_token']
        self.authorize(self.actor)
        response=self.client.patch('/api/v2/admin/users/'+self.target.pk+'/status',{'status':'paused','reason':'Requested leave'},format='json')
        self.assertEqual(response.status_code,200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+target_token)
        self.assertEqual(self.client.get('/api/v2/auth/me').status_code,401)
        self.authorize(self.actor)
        self.assertEqual(self.client.patch('/api/v2/admin/users/'+self.target.pk+'/role',{'role':'super_admin','reason':'Invalid escalation'},format='json').status_code,403)
        ordinary=make_account('ordinary',32,'admin')
        self.authorize(ordinary)
        self.assertEqual(self.client.patch('/api/v2/admin/users/'+self.target.pk+'/status',{'status':'active','reason':'Unauthorized action'},format='json').status_code,403)

    def test_patient_consent_http_contract_and_staff_denial(self):
        patient=make_account('patient-user',33,'patient')
        self.authorize(patient)
        body={'consent_type':'privacy','accepted':True,'version':'approved-v2'}
        self.assertEqual(self.client.post('/api/v2/patient/consents',body,format='json').status_code,200)
        self.assertEqual(self.client.get('/api/v2/patient/consents').json()[0]['version'],'approved-v2')
        body['version']='draft'
        self.assertEqual(self.client.post('/api/v2/patient/consents',body,format='json').status_code,403)
        self.authorize(self.target)
        body['version']='approved-v2'
        self.assertEqual(self.client.post('/api/v2/patient/consents',body,format='json').status_code,403)
        self.assertEqual(self.client.get('/api/v2/patient/consents').status_code,403)
