"""CRUD operations and API serialization for saved analysis sessions."""

from __future__ import annotations

import json
from collections import Counter
from statistics import mean
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.db.models import AnalysisSession, DetectedIssue, PatientProfile
from app.schemas.patient_schema import DetectedIssueTrend, PatientCreate, PatientProgressSummary, PatientUpdate
from app.schemas.therapist_schema import TherapistDashboardSummary
from app.schemas.session_schema import (
    DetectedIssueSchema, SessionDetail, SessionMetricSchema, SessionSummary,
)


def _json(value: str, fallback):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def to_summary(row: AnalysisSession) -> SessionSummary:
    return SessionSummary(
        session_id=row.session_id, exercise_id=row.exercise_id,
        exercise_display_name=row.exercise_display_name, status=row.status,
        created_at=row.created_at, total_reps=row.total_reps,
        movement_score=row.movement_score,
        analysis_confidence_level=row.analysis_confidence_level,
        pose_quality_level=row.pose_quality_level,
        detected_issues=_json(row.detected_issues_json, []),
        report_download_url=row.report_download_url,
        overlay_preview_url=row.overlay_preview_url,
    )


def to_detail(row: AnalysisSession) -> SessionDetail:
    return SessionDetail(
        **to_summary(row).model_dump(), error_code=row.error_code, message=row.message,
        updated_at=row.updated_at, source_filename=row.source_filename,
        video_duration_sec=row.video_duration_sec,
        rep_count_confidence=row.rep_count_confidence,
        analysis_confidence_score=row.analysis_confidence_score,
        pose_quality_score=row.pose_quality_score, summary=row.summary,
        limitations=_json(row.limitations_json, []), feedback=_json(row.feedback_json, []),
        score_breakdown=_json(row.score_breakdown_json, None),
        input_validity=_json(row.input_validity_json, None),
        ml_prediction=_json(row.ml_prediction_json, None),
        report_id=row.report_id, overlay_id=row.overlay_id,
        overlay_download_url=row.overlay_download_url,
        metrics=[SessionMetricSchema(
            metric_name=item.metric_name, metric_value_float=item.metric_value_float,
            metric_value_text=item.metric_value_text, unit=item.unit,
        ) for item in row.metrics],
        issue_details=[DetectedIssueSchema(
            issue_code=item.issue_code, severity=item.severity, message=item.message,
        ) for item in row.detected_issue_rows],
    )


def list_sessions(
    db: Session, exercise_id: str | None = None, status: str | None = None,
    limit: int = 50, offset: int = 0, owner_user_id: str | None = None,
) -> tuple[list[AnalysisSession], int]:
    filters = []
    if exercise_id:
        filters.append(AnalysisSession.exercise_id == exercise_id)
    if status:
        filters.append(AnalysisSession.status == status)
    if owner_user_id:
        filters.append(AnalysisSession.owner_user_id == owner_user_id)
    total = db.scalar(select(func.count()).select_from(AnalysisSession).where(*filters)) or 0
    rows = db.scalars(
        select(AnalysisSession).where(*filters)
        .order_by(AnalysisSession.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return list(rows), int(total)


def get_session(db: Session, session_id: str) -> AnalysisSession | None:
    return db.scalar(
        select(AnalysisSession).where(AnalysisSession.session_id == session_id).options(
            selectinload(AnalysisSession.metrics),
            selectinload(AnalysisSession.detected_issue_rows),
            selectinload(AnalysisSession.uploaded_media),
        )
    )


def delete_session(db: Session, session_id: str) -> bool:
    row = get_session(db, session_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def create_patient_profile(db: Session, data: PatientCreate) -> PatientProfile:
    row = PatientProfile(patient_id=str(uuid4()), **data.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return row


def list_patient_profiles(db: Session) -> list[PatientProfile]:
    return list(db.scalars(select(PatientProfile).order_by(PatientProfile.created_at.desc())).all())


def get_patient_profile(db: Session, patient_id: str) -> PatientProfile | None:
    return db.scalar(select(PatientProfile).where(PatientProfile.patient_id == patient_id))


def update_patient_profile(db: Session, patient_id: str, data: PatientUpdate) -> PatientProfile | None:
    row = get_patient_profile(db, patient_id)
    if row is None:
        return None
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(row, name, value.strip() if name == "display_name" and value else value)
    db.commit(); db.refresh(row)
    return row


def delete_patient_profile(db: Session, patient_id: str) -> bool:
    row = get_patient_profile(db, patient_id)
    if row is None:
        return False
    db.execute(update(AnalysisSession).where(AnalysisSession.patient_id == patient_id).values(patient_id=None))
    db.delete(row); db.commit()
    return True


def assign_session_to_patient(db: Session, patient_id: str, session_id: str) -> AnalysisSession | None:
    patient = get_patient_profile(db, patient_id)
    session = get_session(db, session_id)
    if patient is None or session is None:
        return None
    session.patient_id = patient_id
    db.commit(); db.refresh(session)
    return session


def list_patient_sessions(db: Session, patient_id: str) -> list[AnalysisSession]:
    return list(db.scalars(
        select(AnalysisSession).where(AnalysisSession.patient_id == patient_id)
        .order_by(AnalysisSession.created_at.desc())
    ).all())


def get_patient_detected_issue_summary(db: Session, patient_id: str) -> list[DetectedIssueTrend]:
    counts = Counter(db.scalars(
        select(DetectedIssue.issue_code).join(
            AnalysisSession, DetectedIssue.session_id == AnalysisSession.session_id
        ).where(AnalysisSession.patient_id == patient_id)
    ).all())
    return [DetectedIssueTrend(issue_code=code, count=count) for code, count in counts.most_common()]


def get_patient_progress_summary(db: Session, patient_id: str) -> PatientProgressSummary:
    sessions = list_patient_sessions(db, patient_id)
    scores = [float(row.movement_score) for row in sessions if row.movement_score is not None]
    confidences = [float(row.analysis_confidence_score) for row in sessions if row.analysis_confidence_score is not None]
    issue_counts = get_patient_detected_issue_summary(db, patient_id)
    provenance = [
        "total_sessions: analysis_sessions rows assigned to this patient_id",
        "sessions_by_exercise: analysis_sessions.exercise_id counts",
        "average_movement_score: mean of non-null analysis_sessions.movement_score values",
        "average_analysis_confidence: mean of non-null analysis_sessions.analysis_confidence_score values",
        "latest_session_date: latest analysis_sessions.created_at value",
        "detected_issue_counts: detected_issues rows joined by session_id",
        "low_confidence_session_count: analysis_sessions.analysis_confidence_level == 'low'",
    ]
    return PatientProgressSummary(
        patient_id=patient_id, total_sessions=len(sessions),
        sessions_by_exercise=dict(Counter(row.exercise_id for row in sessions)),
        average_movement_score=round(mean(scores), 2) if scores else None,
        average_analysis_confidence=round(mean(confidences), 3) if confidences else None,
        movement_score_observation_count=len(scores),
        analysis_confidence_observation_count=len(confidences),
        latest_session_date=max((row.created_at for row in sessions), default=None),
        detected_issue_counts=issue_counts,
        low_confidence_session_count=sum(row.analysis_confidence_level == "low" for row in sessions),
        metric_provenance=provenance if sessions else [],
    )


def get_therapist_dashboard_summary(db: Session) -> TherapistDashboardSummary:
    sessions = list(db.scalars(select(AnalysisSession).order_by(AnalysisSession.created_at.desc())).all())
    issue_counts = Counter(db.scalars(select(DetectedIssue.issue_code)).all())
    return TherapistDashboardSummary(
        total_patients=db.scalar(select(func.count()).select_from(PatientProfile)) or 0,
        total_sessions=len(sessions),
        recent_sessions=[to_summary(row) for row in sessions[:10]],
        low_confidence_sessions=sum(row.analysis_confidence_level == "low" for row in sessions),
        common_detected_issues=[DetectedIssueTrend(issue_code=code, count=count) for code, count in issue_counts.most_common(10)],
        sessions_by_exercise=dict(Counter(row.exercise_id for row in sessions)),
        low_confidence_sessions_by_exercise=dict(Counter(
            row.exercise_id for row in sessions if row.analysis_confidence_level == "low"
        )),
    )
