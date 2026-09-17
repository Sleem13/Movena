"""Loopback-only browser QA using real legacy routes and an in-memory database.

No production config, network email, stored media, or existing database is used.
All accounts and plan records are synthetic and disappear on process exit.
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.update(APP_ENV='development', DATABASE_URL='sqlite://', REQUIRE_EMAIL_VERIFICATION='false',
                  EMAIL_DELIVERY_MODE='disabled', SECRET_KEY='rebuild-fixture-only-not-a-production-secret')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.db.models import User, PatientProfile, TherapistPatientAssignment, ExercisePlan, ExercisePlanItem, TherapistAvailability, AnalysisSession, Appointment, ClinicalSessionNote
from app.core.security import get_password_hash
from app.core.authorization import permissions_json_for_role
from app.api.dependencies.auth import AuthError
from app.api.v1.auth import router as auth
from app.api.v1.patient import router as patient
from app.api.v1.therapist import router as therapist
from app.api.v1.therapist_care import router as therapist_care
from app.api.v1.connections import router as connections
from app.api.routes.exercises import router as exercises
from app.api.routes.sessions import router as sessions
from app.api.v1.scheduling import router as scheduling

engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
with Session(engine) as db:
    for role in ['patient', 'therapist', 'super_admin']:
        db.add(User(user_id=f'fixture-{role}', username=f'preview_{role}', email=f'{role}@example.test',
                    full_name=f'Preview {role.replace("_", " ")}', role=role, password_hash=get_password_hash('Preview-Only-482!'),
                    is_active=True, is_verified=True, permissions_json=permissions_json_for_role(role)))
    db.add(PatientProfile(patient_id='fixture-profile', user_id='fixture-patient', display_name='Preview patient', preferred_locale='en', timezone_name='UTC'))
    db.add(TherapistPatientAssignment(assignment_id='fixture-connection', therapist_user_id='fixture-therapist', patient_id='fixture-profile', status='active', source='fixture'))
    for weekday in range(7):
        db.add(TherapistAvailability(availability_id=f'fixture-availability-{weekday}', therapist_user_id='fixture-therapist', weekday=weekday, start_minute=540, end_minute=1020, timezone_name='UTC', is_active=True))
    db.add(ExercisePlan(plan_id='fixture-plan', patient_id='fixture-profile', created_by_user_id='fixture-therapist', title='Build your daily rhythm', status='active'))
    for index, exercise in enumerate(['knee_extension', 'sit_to_stand', 'shoulder_abduction']):
        db.add(ExercisePlanItem(item_id=f'fixture-item-{index}', plan_id='fixture-plan', exercise_id=exercise, sets=2, reps=10,
                               days_per_week=7, instructions='Synthetic QA plan — not a treatment prescription.', sort_order=index))
    for index in range(43):
        outcome=['success','rejected','error'][index % 3]
        db.add(AnalysisSession(session_id=f'fixture-history-{index:02}',patient_id='fixture-profile',owner_user_id='fixture-patient',
            exercise_id='knee_extension',exercise_display_name='Knee extension',status=outcome,
            created_at=datetime.now(timezone.utc)-timedelta(days=index),total_reps=0 if outcome=='success' else None,
            summary='Synthetic history fixture, not an evaluated analysis.'))
    db.add(AnalysisSession(session_id='fixture-private-history',owner_user_id='fixture-therapist',exercise_id='knee_extension',
        exercise_display_name='Knee extension',status='success',total_reps=5))
    db.add(Appointment(appointment_id='fixture-visit',patient_id='fixture-profile',therapist_user_id='fixture-therapist',created_by_user_id='fixture-therapist',
        starts_at=datetime.now(timezone.utc)-timedelta(days=2),ends_at=datetime.now(timezone.utc)-timedelta(days=2)+timedelta(minutes=30),status='completed',delivery_mode='in_person'))
    for suffix,shared in [('private',False),('shared',True)]:
        db.add(ClinicalSessionNote(note_id='fixture-note-'+suffix,appointment_id='fixture-visit',therapist_user_id='fixture-therapist',
            summary='Synthetic '+suffix+' note — not clinical advice.',patient_visible=shared))
    db.commit()

app = FastAPI(title='Movena isolated rebuild QA')
def database():
    with Session(engine, expire_on_commit=False) as db:
        yield db
app.dependency_overrides[get_db] = database
@app.exception_handler(AuthError)
def auth_error(_, exc):
    return JSONResponse({'status': 'error', 'error_code': exc.error_code, 'message': exc.message}, status_code=exc.status_code)
for router in [auth, patient, therapist, therapist_care, connections, exercises, sessions, scheduling]:
    app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8040, access_log=False)
