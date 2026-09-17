import json
from unittest.mock import patch
import httpx
from django.test import TestCase
from rest_framework.test import APIClient
from .routing import allowed

USER = {"user_id": "patient-one", "role": "patient", "email": "example@example.test"}


class BridgeTests(TestCase):
    def test_data_rights_submission_replays_without_a_duplicate(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        path = '/api/v2/patient/data-rights-requests'
        body = {'request_type':'export','details':'Synthetic request'}
        created = {'request_id':'stable-request', **body, 'status':'pending', 'created_at':'2026-09-14T00:00:00Z'}
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200,json=USER), httpx.Response(201,json=created)]):
            self.assertEqual(self.client.post(path, body, format='json', HTTP_IDEMPOTENCY_KEY='privacy-retry-key').status_code, 201)
        with patch('platform_api.upstream.request', return_value=httpx.Response(200,json=USER)) as upstream:
            replay = self.client.post(path, body, format='json', HTTP_IDEMPOTENCY_KEY='privacy-retry-key')
            self.assertEqual(replay.json(), created)
            self.assertEqual(replay['X-Movena-Idempotency-Replayed'], 'true')
            self.assertEqual(upstream.call_count, 1)

    def test_note_replay_rechecks_current_appointment_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        path='/api/v2/therapist/appointments/visit-one/session-notes'
        body={'summary':'Synthetic note','patient_visible':False}
        created={**body,'note_id':'stable-note'}
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[]),httpx.Response(201,json=created)]):
            self.assertEqual(self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-retry-key').status_code,201)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[])]) as upstream:
            self.assertEqual(self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-retry-key').json(),created)
            self.assertEqual(upstream.call_count,2)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(403,json={})]):
            denied=self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-retry-key')
            self.assertEqual(denied.status_code,403)
            self.assertNotIn('summary',denied.json())

    def test_note_validation_and_unknown_outcome_never_repeat_upstream_write(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        path='/api/v2/therapist/appointments/visit-one/session-notes'
        with patch('platform_api.upstream.request',return_value=httpx.Response(200,json=USER)) as upstream:
            for body in [{'summary':'   '},{'summary':'text','patient_visible':'false'},{'summary':'text','recommendations':{}},[]]:
                self.assertEqual(self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-invalid').status_code,400)
            self.assertEqual(upstream.call_count,4)
        body={'summary':'Synthetic note'}
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[]),httpx.Response(503,json={})]):
            self.assertEqual(self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-unknown').status_code,503)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[])]) as upstream:
            self.assertEqual(self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='note-unknown').status_code,409)
            self.assertEqual(upstream.call_count,2)

    def test_history_paging_preserves_filters_nulls_and_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        body={'items':[{'session_id':'s','status':'rejected','total_reps':None}], 'total':41,'limit':20,'offset':40}
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=body)]) as upstream:
            response=self.client.get('/api/v2/sessions?limit=20&offset=40&status=rejected')
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json(),body)
            self.assertEqual(upstream.call_args.kwargs['query'],'limit=20&offset=40&status=rejected')
            self.assertEqual(upstream.call_args.kwargs['token'],'valid')
            self.assertEqual(response['Cache-Control'],'no-store')

    def test_new_multibyte_password_cannot_exceed_legacy_bcrypt_limit(self):
        with patch('platform_api.upstream.request') as upstream:
            for path,field in [('register','password'),('reset-password','new_password')]:
                response=self.client.post('/api/v2/auth/'+path,{field:'ع'*37},format='json')
                self.assertEqual(response.status_code,400)
                self.assertIn('72',response.json()['message'])
            upstream.assert_not_called()

    def test_plan_replay_is_stable_and_rechecks_patient_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        path='/api/v2/therapist/patients/p-one/exercise-plans'
        body={'title':'Test plan','items':[]}
        created={'plan_id':'preserved-id','title':'Test plan'}
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[]),httpx.Response(201,json=created)]):
            first=self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='plan-retry-key')
            self.assertEqual(first.status_code,201)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[])]) as upstream:
            repeat=self.client.post(path,{'items':[],'title':'Test plan'},format='json',HTTP_IDEMPOTENCY_KEY='plan-retry-key')
            self.assertEqual(repeat.json(),created)
            self.assertEqual(upstream.call_count,2)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(403,json={})]):
            denied=self.client.post(path,body,format='json',HTTP_IDEMPOTENCY_KEY='plan-retry-key')
            self.assertEqual(denied.status_code,403)
            self.assertNotIn('plan_id',denied.json())

    def test_uncertain_plan_publication_never_dispatches_a_second_version(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        path='/api/v2/therapist/patients/p-one/exercise-plans'
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[]),httpx.Response(503,json={})]):
            self.assertEqual(self.client.post(path,{},format='json',HTTP_IDEMPOTENCY_KEY='uncertain-plan').status_code,503)
        with patch('platform_api.upstream.request',side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=[])]) as upstream:
            self.assertEqual(self.client.post(path,{},format='json',HTTP_IDEMPOTENCY_KEY='uncertain-plan').status_code,409)
            self.assertEqual(upstream.call_count,2)

    def test_booking_requires_stable_retry_key_before_forwarding(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        with patch('platform_api.upstream.request', return_value=httpx.Response(200, json=USER)) as upstream:
            for key in ['', 'short', 'contains spaces!']:
                response = self.client.post('/api/v2/scheduling/appointments', {}, format='json', HTTP_IDEMPOTENCY_KEY=key)
                self.assertEqual(response.status_code, 400)
            self.assertEqual(upstream.call_count, 3)  # Authentication only.

    def test_availability_rejects_invalid_timezone_and_nonobject_body(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        with patch('platform_api.upstream.request', return_value=httpx.Response(200, json=USER)) as upstream:
            for body in [{'timezone_name': 'Unknown/Place'}, {'timezone_name': None}, []]:
                response = self.client.post('/api/v2/therapist/availability', body, format='json')
                self.assertEqual(response.status_code, 400)
            self.assertEqual(upstream.call_count, 3)

    def test_calendar_normalizes_legacy_utc_without_altering_aware_offsets(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        values = [{'starts_at':'2030-01-01T09:00:00','ends_at':'2030-01-01T12:30:00+03:00','model_version':None}]
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200,json=USER),httpx.Response(200,json=values)]):
            response = self.client.get('/api/v2/patient/appointments')
            self.assertEqual(response.json()[0]['starts_at'], '2030-01-01T09:00:00+00:00')
            self.assertEqual(response.json()[0]['ends_at'], values[0]['ends_at'])
            self.assertIsNone(response.json()[0]['model_version'])
        from .scheduling import normalize_timestamps
        self.assertEqual(normalize_timestamps({'slots': values})['slots'][0]['starts_at'], '2030-01-01T09:00:00+00:00')
        self.assertEqual(normalize_timestamps({'expires_at':'unavailable'}), {'expires_at':'unavailable'})

    def test_booking_conflict_preserves_error_and_idempotency_key(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200,json=USER),httpx.Response(409,json={'error_code':'APPOINTMENT_CONFLICT'})]) as upstream:
            response = self.client.post('/api/v2/scheduling/appointments', {}, format='json', HTTP_IDEMPOTENCY_KEY='stable-booking-key')
            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json()['error_code'], 'APPOINTMENT_CONFLICT')
            self.assertEqual(upstream.call_args.kwargs['idempotency_key'], 'stable-booking-key')

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_cannot_read_patient_records(self):
        with patch('platform_api.upstream.request') as upstream:
            self.assertEqual(self.client.get('/api/v2/patient/today').status_code, 401)
            upstream.assert_not_called()

    def test_login_does_not_require_existing_token(self):
        with patch('platform_api.upstream.request', return_value=httpx.Response(401, json={"error_code": "INVALID_CREDENTIALS"})) as upstream:
            response = self.client.post('/api/v2/auth/login', {"email": "nobody", "password": "bad"}, format='json')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(upstream.call_count, 1)

    def test_public_recovery_ignores_an_expired_session(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired-session')
        with patch('platform_api.upstream.request', return_value=httpx.Response(200,json={'status':'success','message':'Check your email'})) as upstream:
            response=self.client.post('/api/v2/auth/forgot-password',{'email':'fixture@example.test'},format='json')
            self.assertEqual(response.status_code,200)
            self.assertEqual(upstream.call_count,1)
            self.assertEqual(upstream.call_args.args[:2],('POST','/api/v1/auth/forgot-password'))
            self.assertIsNone(upstream.call_args.kwargs['token'])

    def test_revoked_token_cannot_reach_target(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer revoked')
        with patch('platform_api.upstream.request', return_value=httpx.Response(401, json={})) as upstream:
            self.assertEqual(self.client.get('/api/v2/patient/today').status_code, 401)
            self.assertEqual(upstream.call_count, 1)

    def test_object_denial_is_preserved(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200, json=USER), httpx.Response(403, json={"error_code": "PATIENT_ACCESS_DENIED"})]):
            response = self.client.get('/api/v2/therapist/patients/another-patient')
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()['error_code'], 'PATIENT_ACCESS_DENIED')

    def test_multipart_and_idempotency_are_unchanged(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        body = b'--boundary\r\nContent-Disposition: form-data; name="video"; filename="sample.mp4"\r\n\r\nexample\r\n--boundary--\r\n'
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200, json=USER), httpx.Response(202, json={"job_id": "j1", "status": "queued", "result": None})]) as upstream:
            response = self.client.generic('POST', '/api/v2/analysis-jobs/bodyweight_squat?save_session=true', body, content_type='multipart/form-data; boundary=boundary', HTTP_IDEMPOTENCY_KEY='stable-retry')
            self.assertEqual(response.status_code, 202)
            call = upstream.call_args.kwargs
            self.assertEqual(call['content'], body)
            self.assertEqual(call['idempotency_key'], 'stable-retry')
            self.assertEqual(call['query'], 'save_session=true')
            self.assertEqual(response.json()['engine_version'], 'legacy-v1')
            self.assertIsNone(response.json()['model_version'])

    def test_redirects_and_cookies_do_not_cross_boundary(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200, json=USER), httpx.Response(302, headers={'location': 'https://unexpected.test', 'set-cookie': 'secret=value'})]):
            response = self.client.get('/api/v2/patient/today')
            self.assertEqual(response.status_code, 502)
            self.assertNotIn('Set-Cookie', response.headers)

    def test_allowlist_rejects_path_traversal_callbacks_and_uninventoried_routes(self):
        for path in ['../auth/me', 'auth//me', 'auth/%2e%2e/me', 'auth/me?token=x', 'does-not-exist', 'checkout/webhook']:
            self.assertFalse(allowed('GET', path), path)
        self.assertTrue(allowed('GET', 'therapist/patients/patient-one'))
        self.assertTrue(allowed('GET', 'admin/platform/data-rights-requests'))
        self.assertTrue(allowed('PATCH', 'admin/platform/data-rights-requests/request-one'))
        self.assertFalse(allowed('DELETE', 'auth/login'))

    def test_health_is_not_claimed_as_upstream_readiness(self):
        response = self.client.get('/health')
        self.assertEqual(response.json()['migration_state'], 'legacy_authoritative')

    def test_retry_replays_receipt_without_creating_another_job(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        body = b'--boundary\r\nContent-Disposition: form-data; name="video"; filename="sample.mp4"\r\n\r\nexample\r\n--boundary--\r\n'
        with patch('platform_api.upstream.request', side_effect=[httpx.Response(200, json=USER), httpx.Response(202, json={'job_id': 'only-one', 'exercise_id':'bodyweight_squat', 'status':'queued', 'stage':'queued', 'progress':5, 'result':None}), httpx.Response(200, json=USER)]) as upstream:
            for boundary in ['first', 'second']:
                response = self.client.generic('POST', '/api/v2/analysis-jobs/bodyweight_squat', body.replace(b'boundary', boundary.encode()),
                    content_type=f'multipart/form-data; boundary={boundary}', HTTP_IDEMPOTENCY_KEY='same-upload-key')
                self.assertEqual(response.status_code, 202)
                self.assertEqual(response.json()['job_id'], 'only-one')
            self.assertEqual(upstream.call_count, 3)

    def test_ambiguous_receipt_fails_closed_and_changed_payload_conflicts(self):
        from .submissions import reserve, SubmissionConflict
        reserve('owner', 'stable-key', 'scope', 'first')
        for fingerprint in ['first', 'changed']:
            with self.assertRaises(SubmissionConflict): reserve('owner', 'stable-key', 'scope', fingerprint)

    def test_operational_outcomes_exclude_credentials_and_payloads(self):
        with self.assertLogs('movena.outcomes', level='INFO') as logs:
            response = self.client.get('/health?private=do-not-log-this', HTTP_AUTHORIZATION='Bearer never-log-token')
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Request-ID', response)
        record = logs.output[0]
        self.assertIn('duration_ms', record)
        self.assertNotIn('never-log-token', record)
        self.assertNotIn('do-not-log-this', record)
