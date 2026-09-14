from types import SimpleNamespace
from django.test import TestCase
from rest_framework.test import APIClient
from .analysis_jobs import capture, owned_or_absent
from .models import AnalysisJobRecord


class AnalysisJobRecordTests(TestCase):
    def test_lifecycle_sync_preserves_owner_and_distinct_outcomes(self):
        queued={'job_id':'00000000-0000-4000-8000-000000000111','exercise_id':'bodyweight_squat',
            'status':'queued','stage':'queued','progress':5,'attempts':0,'max_attempts':2,
            'cancel_requested':False,'result':None,'engine_version':'legacy-v1','model_version':None}
        capture('patient-one','analysis-jobs/bodyweight_squat',queued)
        row=AnalysisJobRecord.objects.get(); self.assertIsNone(row.outcome)
        completed={**queued,'status':'completed','stage':'completed','progress':100,
            'result':{'status':'rejected','total_reps':None},'model_version':'model-1'}
        capture('patient-one','analysis-jobs/'+queued['job_id'],completed)
        row.refresh_from_db()
        self.assertEqual((row.status,row.outcome),('completed','rejected'))
        self.assertIsNone(row.result['total_reps'])
        self.assertEqual(row.model_version,'model-1')
        capture('patient-one','analysis-jobs/'+queued['job_id']+'/cancel',{
            'job_id':queued['job_id'],'status':'cancelled','message':'Cancellation requested.'})
        row.refresh_from_db()
        self.assertEqual(row.exercise_id,'bodyweight_squat')
        self.assertEqual(row.model_version,'model-1')
        self.assertEqual(row.progress,100)
        with self.assertRaises(ValueError):
            capture('another-owner','analysis-jobs/'+queued['job_id'],completed)

    def test_local_ownership_hides_known_foreign_job(self):
        data={'job_id':'00000000-0000-4000-8000-000000000222','exercise_id':'balance',
            'status':'running','stage':'pose','progress':40}
        capture('patient-one','analysis-jobs/balance',data)
        self.assertTrue(owned_or_absent(data['job_id'],SimpleNamespace(user_id='patient-one',role='patient')))
        self.assertFalse(owned_or_absent(data['job_id'],SimpleNamespace(user_id='patient-two',role='patient')))
        self.assertTrue(owned_or_absent(data['job_id'],SimpleNamespace(user_id='root',role='super_admin')))
        self.assertTrue(owned_or_absent('absent',SimpleNamespace(user_id='patient-two',role='patient')))

    def test_active_list_is_owner_scoped_and_excludes_terminal_jobs(self):
        base={'exercise_id':'balance','stage':'pose','progress':40}
        capture('patient-one','analysis-jobs/balance',{
            **base,'job_id':'00000000-0000-4000-8000-000000000301','status':'running'})
        capture('patient-two','analysis-jobs/balance',{
            **base,'job_id':'00000000-0000-4000-8000-000000000302','status':'queued'})
        capture('patient-one','analysis-jobs/balance',{
            **base,'job_id':'00000000-0000-4000-8000-000000000303','status':'completed',
            'progress':100,'result':{'status':'success'}})
        client=APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer valid')
        from unittest.mock import patch
        import httpx
        with patch('platform_api.upstream.request',return_value=httpx.Response(200,json={
            'user_id':'patient-one','role':'patient','email':'one@example.test'})):
            response=client.get('/api/v2/analysis-jobs')
        self.assertEqual(response.status_code,200)
        self.assertEqual([row['job_id'] for row in response.json()],
            ['00000000-0000-4000-8000-000000000301'])
