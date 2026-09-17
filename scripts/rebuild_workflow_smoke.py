"""Replacement contract smoke tests against real routes on disposable records."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from scripts.rebuild_fixture_server import app
from app.schemas.care_schema import PatientTodayResponse, AdherenceDetail
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from app.core.config import get_settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from scripts.rebuild_fixture_server import engine
from app.db.models import User, UserConsent, AdherenceEntry, Notification, Appointment, PatientProfile, TherapistPatientAssignment
from app.services.auth_token_service import issue_password_reset_token


def login(client, role):
    response = client.post('/api/v1/auth/login', json={
        'email': f'{role}@example.test', 'password': 'Preview-Only-482!',
    })
    assert response.status_code == 200
    return {'Authorization': 'Bearer ' + response.json()['access_token']}


def test_patient_response_retry_and_clinician_review_contract():
    with TestClient(app) as client:
        patient = login(client, 'patient')
        therapist = login(client, 'therapist')
        today = PatientTodayResponse.model_validate(client.get('/api/v1/patient/today', headers=patient).json())
        item = today.plan_items[0]
        values = {'plan_item_id': item.item_id, 'scheduled_date': today.date.isoformat(),
                  'completion_status': 'partial', 'pain_before': 0, 'pain_after': 5,
                  'symptoms_changed': True, 'safety_acknowledged': True,
                  'note': 'Synthetic contract test, not clinical evidence.'}
        headers = {**patient, 'Idempotency-Key': 'fixture-response-retry'}
        first = client.post('/api/v1/patient/adherence', json=values, headers=headers)
        assert first.status_code == 201
        response = AdherenceDetail.model_validate(first.json())
        repeated = client.post('/api/v1/patient/adherence', json=values, headers=headers)
        assert repeated.status_code == 201
        assert repeated.json()['adherence_id'] == response.adherence_id
        assert response.pain_before == 0 and response.clinician_review_required
        path = f'/api/v1/therapist/patients/{today.patient_id}/adherence/{response.adherence_id}/acknowledge'
        assert client.post(path, json={'disposition': 'reviewed_no_change', 'clinician_attestation': True}, headers=therapist).status_code == 422
        reviewed = client.post(path, json={'disposition': 'contacted_patient', 'note': 'Synthetic review.', 'clinician_attestation': True}, headers=therapist)
        assert reviewed.status_code == 200
        assert reviewed.json()['reviewed_at'] is not None
        assert client.get('/api/v1/therapist/patients/unassigned/adherence', headers=therapist).status_code == 403
        assert client.get('/api/v1/therapist/patients', headers=patient).status_code == 403
        assert client.get('/api/v1/patient/today').status_code == 401


def test_scheduling_retry_permissions_changes_and_private_video():
    with TestClient(app) as client:
        patient, therapist = login(client, 'patient'), login(client, 'therapist')
        day = (datetime.now(timezone.utc) + timedelta(days=3)).date().isoformat()
        initial_ids = {item['appointment_id'] for item in client.get('/api/v1/patient/appointments', headers=patient).json()}
        availability = client.get('/api/v1/scheduling/availability', params={'therapist_user_id':'fixture-therapist','day':day}, headers=patient)
        assert availability.status_code == 200
        slots = availability.json()['slots']
        assert len(slots) == 16
        body = {'patient_id':'fixture-profile','therapist_user_id':'fixture-therapist','delivery_mode':'video',**slots[0]}
        headers = {**patient,'Idempotency-Key':'fixture-book-retry'}
        first = client.post('/api/v1/scheduling/appointments',json=body,headers=headers)
        assert first.status_code == 201, first.text
        identifier = first.json()['appointment_id']
        repeated = client.post('/api/v1/scheduling/appointments',json=body,headers=headers)
        assert repeated.json()['appointment_id'] == identifier
        assert client.post('/api/v1/scheduling/appointments',json=body,headers={**patient,'Idempotency-Key':'fixture-conflict'}).status_code == 409
        assert client.post('/api/v1/scheduling/appointments',json={**body,'patient_id':'another-patient'},headers=patient).status_code == 403
        assert client.post('/api/v1/scheduling/appointments',json={**body,'therapist_user_id':'another-therapist'},headers=therapist).status_code == 403
        path = f'/api/v1/scheduling/appointments/{identifier}'
        assert client.patch(path,json={'status':'cancelled'},headers=patient).status_code == 422
        moved = client.patch(path,json=slots[1],headers=patient)
        assert moved.status_code == 200 and moved.json()['appointment_id'] == identifier
        assert client.patch(path,json={'status':'confirmed'},headers=therapist).json()['status'] == 'confirmed'
        assert {item['appointment_id'] for item in client.get('/api/v1/patient/appointments',headers=patient).json()} == initial_ids | {identifier}
        with patch('app.services.telemedicine_service._request') as provider:
            assert client.get(path+'/join',headers=patient).status_code == 409
            provider.assert_not_called()
        cancelled = client.patch(path,json={'status':'cancelled','cancellation_reason':'Synthetic cancellation test'},headers=patient)
        assert cancelled.status_code == 200 and cancelled.json()['status'] == 'cancelled'
        assert client.get(path+'/join',headers=patient).status_code == 409

        now = datetime.now(timezone.utc)
        live = client.post('/api/v1/scheduling/appointments',json={**body,'starts_at':(now+timedelta(minutes=5)).isoformat(),'ends_at':(now+timedelta(minutes=35)).isoformat()},headers={**patient,'Idempotency-Key':'fixture-live-video'})
        live_path = '/api/v1/scheduling/appointments/'+live.json()['appointment_id']
        settings = get_settings().model_copy(update={'enable_telemedicine':True,'daily_domain':'video.example.test','daily_api_key':'fixture-only'})
        with patch('app.services.telemedicine_service.get_settings',return_value=settings), patch('app.services.telemedicine_service._request',side_effect=[{}, {'token':'fixture-patient-token'}, {'token':'fixture-owner-token'}]) as provider:
            joined = client.get(live_path+'/join',headers=patient)
            assert joined.status_code == 200, joined.text
            assert joined.json()['room_url'].startswith('https://video.example.test/')
            assert provider.call_args_list[0].args[2]['privacy'] == 'private'
            assert provider.call_args_list[0].args[2]['properties']['enable_recording'] == 'off'
            assert provider.call_args_list[1].args[2]['properties']['is_owner'] is False
            assert provider.call_args_list[1].args[2]['properties']['enable_screenshare'] is False
            assert client.get(live_path+'/join',headers=therapist).status_code == 200
            assert provider.call_args_list[2].args[2]['properties']['is_owner'] is True
        assert client.patch(live_path,json={'status':'cancelled','cancellation_reason':'Too late'},headers=patient).status_code == 409


def test_account_lifecycle_and_immutable_plan_history():
    with TestClient(app) as client:
        settings=get_settings().model_copy(update={'require_email_verification':True})
        values={'username':'fixture_new','email':'new@example.test','full_name':'Synthetic New','password':'Initial-Only-482!','role':'patient','accepted_terms':True,'accepted_privacy':True}
        with patch('app.api.v1.auth.get_settings',return_value=settings),patch('app.api.v1.auth.send_verification_email') as mail:
            registered=client.post('/api/v1/auth/register',json=values)
            assert registered.status_code==201 and registered.json()['is_verified'] is False
            token=mail.call_args.args[1]
            assert client.post('/api/v1/auth/login',json={'email':values['email'],'password':values['password']}).status_code==403
        assert client.post('/api/v1/auth/verify-email',json={'token':token}).status_code==200
        assert client.post('/api/v1/auth/verify-email',json={'token':token}).status_code==400
        auth=client.post('/api/v1/auth/login',json={'email':values['email'],'password':values['password']}).json()
        headers={'Authorization':'Bearer '+auth['access_token']}
        with Session(engine) as db:
            assert len(db.scalars(select(UserConsent).where(UserConsent.user_id==registered.json()['user_id'])).all())==2
        with patch('app.api.v1.auth.send_password_reset_email') as mail:
            found=client.post('/api/v1/auth/forgot-password',json={'email':values['email']})
            token=mail.call_args.args[1]
            absent=client.post('/api/v1/auth/forgot-password',json={'email':'absent@example.test'})
            assert found.json()==absent.json()
        reset={'token':token,'new_password':'Replacement-Only-482!'}
        assert client.post('/api/v1/auth/reset-password',json=reset).status_code==200
        assert client.post('/api/v1/auth/reset-password',json=reset).status_code==400
        assert client.get('/api/v1/auth/me',headers=headers).status_code==401
        assert client.post('/api/v1/auth/login',json={'email':values['email'],'password':values['password']}).status_code==401
        assert client.post('/api/v1/auth/login',json={'email':values['email'],'password':reset['new_password']}).status_code==200
        with Session(engine) as db:
            user=db.scalar(select(User).where(User.email==values['email']))
            expired=issue_password_reset_token(user)
            user.reset_password_expires=datetime.now(timezone.utc)-timedelta(seconds=1)
            db.commit()
        assert client.post('/api/v1/auth/reset-password',json={'token':expired,'new_password':'Unused-Only-482!'}).status_code==400
        assert client.post('/api/v1/auth/register',json={**values,'role':'admin'}).status_code==403

        therapist,patient=login(client,'therapist'),login(client,'patient')
        path='/api/v1/therapist/patients/fixture-profile/exercise-plans'
        body={'title':'Synthetic revised plan','items':[{'exercise_id':'knee_extension','sets':2,'reps':8,'days_per_week':7,'rest_interval_seconds':0,'target_rom_degrees':None,'schedule_days':list(range(7)),'requires_ai_analysis':True}]}
        assert client.post(path,json=body,headers=patient).status_code==403
        assert client.post(path.replace('fixture-profile','unassigned'),json=body,headers=therapist).status_code==403
        created=client.post(path,json=body,headers=therapist)
        assert created.status_code==201,created.text
        rows=client.get(path,headers=therapist).json()
        assert len(rows)==2
        assert next(row for row in rows if row['plan_id']=='fixture-plan')['status']=='paused'
        assert created.json()['items'][0]['rest_interval_seconds']==0
        assert created.json()['items'][0]['target_rom_degrees'] is None
        with Session(engine) as db:
            assert db.scalar(select(AdherenceEntry).where(AdherenceEntry.plan_item_id=='fixture-item-0')) is not None
        current=client.get('/api/v1/patient/today',headers=patient).json()
        assert current['plan_title']=='Synthetic revised plan'
        assert client.patch(path+'/'+created.json()['plan_id'],json={'status':'paused'},headers=therapist).status_code==200


def test_health_profile_and_notification_ownership():
    with TestClient(app) as client:
        patient,therapist=login(client,'patient'),login(client,'therapist')
        path='/api/v1/patient/health-profile'
        assert client.get(path,headers=therapist).status_code==403
        assert client.patch(path,json={'medical_summary':'Synthetic health fixture','precautions':'Synthetic precaution'},headers=patient).status_code==200
        assert client.get(path,headers=patient).json()['medical_summary']=='Synthetic health fixture'
        result=client.patch(path,json={'precautions':None},headers=patient)
        assert result.json()['precautions'] is None and result.json()['medical_summary']=='Synthetic health fixture'
        with Session(engine) as db:
            db.add_all([Notification(notification_id='health-patient-message',user_id='fixture-patient',kind='qa',title='Synthetic inbox',body='Synthetic message',action_url='/appointments'),
                        Notification(notification_id='health-private-message',user_id='fixture-therapist',kind='qa',title='Other account',body='Synthetic ownership check')]);db.commit()
        inbox=client.get('/api/v1/patient/notifications',headers=patient).json()
        assert any(row['notification_id']=='health-patient-message' for row in inbox)
        assert not any(row['notification_id']=='health-private-message' for row in inbox)
        assert client.post('/api/v1/patient/notifications/health-private-message/read',headers=patient).status_code==404
        read=client.post('/api/v1/patient/notifications/health-patient-message/read',headers=patient)
        assert read.status_code==200 and read.json()['read_at'] is not None
        unread=client.get('/api/v1/patient/notifications?unread_only=true',headers=patient).json()
        assert not any(row['notification_id']=='health-patient-message' for row in unread)
        assert client.get('/api/v1/patient/consents',headers=therapist).status_code==403

def test_history_pages_filters_and_private_records():
    with TestClient(app) as client:
        patient=login(client,'patient')
        seen=[]
        for offset in [0,20,40]:
            result=client.get(f'/api/v1/sessions?limit=20&offset={offset}',headers=patient)
            assert result.status_code==200
            data=result.json()
            assert data['total']==43 and data['offset']==offset
            seen.extend(row['session_id'] for row in data['items'])
        assert len(set(seen))==43 and seen[-1]=='fixture-history-42'
        assert 'fixture-private-history' not in seen
        assert client.get('/api/v1/sessions/fixture-private-history',headers=patient).status_code==404
        rejected=client.get('/api/v1/sessions?status=rejected',headers=patient).json()
        assert rejected['total']==14
        assert all(row['status']=='rejected' and row['total_reps'] is None for row in rejected['items'])
        zero=client.get('/api/v1/sessions/fixture-history-00',headers=patient).json()
        assert zero['total_reps']==0 and zero['movement_score'] is None
        assert client.get('/api/v1/sessions?offset=-1',headers=patient).status_code==422

def test_progress_report_sharing_and_permissions():
    with TestClient(app) as client:
        patient,therapist=login(client,'patient'),login(client,'therapist')
        path='/api/v1/therapist/patients/fixture-profile/reports'
        params={'period_start':'2026-08-01','period_end':'2026-08-31','share_with_patient':True}
        assert client.post(path,params=params,headers=patient).status_code==403
        assert client.post(path.replace('fixture-profile','unassigned'),params=params,headers=therapist).status_code==403
        with patch('app.api.v1.therapist_care.create_artifact',return_value=('a'*32,Path('synthetic-report.pdf'))), \
             patch('app.api.v1.therapist_care.generate_progress_report') as generate:
            created=client.post(path,params=params,headers=therapist)
            assert created.status_code==200,created.text
            assert created.json()['shared_with_patient'] is True
            generate.assert_called_once()
        visible=client.get('/api/v1/patient/reports',headers=patient)
        assert visible.status_code==200
        assert created.json()['progress_report_id'] in {row['progress_report_id'] for row in visible.json()}
        assert client.get('/api/v1/patient/reports',headers=therapist).status_code==403

def test_visit_note_visibility_ownership_and_revocation():
    with TestClient(app) as client:
        patient,therapist=login(client,'patient'),login(client,'therapist')
        path='/api/v1/therapist/appointments/fixture-visit/session-notes'
        patient_path='/api/v1/patient/appointments/fixture-visit/session-notes'
        assert client.post(path,json={'summary':'Denied'},headers=patient).status_code==403
        created=client.post(path,json={'summary':'Synthetic private addition'},headers=therapist)
        assert created.status_code==201 and created.json()['patient_visible'] is False
        shared=client.post(path,json={'summary':'<b>Synthetic shared addition</b>','patient_visible':True},headers=therapist)
        assert shared.status_code==201
        own_notes=client.get(path,headers=therapist).json()
        visible=client.get(patient_path,headers=patient).json()
        assert len(own_notes)==4 and len(visible)==2
        assert all(note['patient_visible'] and note['author_name']=='Preview therapist' for note in visible)
        assert shared.json()['summary'] in [note['summary'] for note in visible]
        assert created.json()['note_id'] not in [note['note_id'] for note in visible]
        with Session(engine) as db:
            db.add(PatientProfile(patient_id='notes-other-patient',display_name='Other synthetic patient'))
            db.add_all([Appointment(appointment_id='notes-other-owner',patient_id='fixture-profile',therapist_user_id='fixture-super_admin',created_by_user_id='fixture-super_admin',
                starts_at=datetime.now(timezone.utc),ends_at=datetime.now(timezone.utc)+timedelta(minutes=30)),
                Appointment(appointment_id='notes-other-patient',patient_id='notes-other-patient',therapist_user_id='fixture-therapist',created_by_user_id='fixture-therapist',
                starts_at=datetime.now(timezone.utc),ends_at=datetime.now(timezone.utc)+timedelta(minutes=30))]);db.commit()
        assert client.get('/api/v1/therapist/appointments/notes-other-owner/session-notes',headers=therapist).status_code==403
        assert client.get('/api/v1/patient/appointments/notes-other-patient/session-notes',headers=patient).status_code==404
        with Session(engine) as db:
            db.query(TherapistPatientAssignment).filter_by(assignment_id='fixture-connection').one().status='inactive';db.commit()
        assert client.get(path,headers=therapist).status_code==403
        assert client.post(path,json={'summary':'Revoked'},headers=therapist).status_code==403
        assert len(client.get(patient_path,headers=patient).json())==2

if __name__ == "__main__":
    test_patient_response_retry_and_clinician_review_contract()
    test_scheduling_retry_permissions_changes_and_private_video()
    test_account_lifecycle_and_immutable_plan_history()
    test_health_profile_and_notification_ownership()
    test_history_pages_filters_and_private_records()
    test_progress_report_sharing_and_permissions()
    test_visit_note_visibility_ownership_and_revocation()
    print("Recovery, scheduling, accounts and plan workflow contracts passed on isolated fixtures.")
