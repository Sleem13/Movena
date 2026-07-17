"""Failure-isolated persistence of analysis metadata and derived metrics."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import AnalysisSession, DetectedIssue, PatientProfile, SessionMetric, UploadedMedia


DISPLAY_NAMES = {"bodyweight_squat": "Bodyweight Squat", "sit_to_stand": "Sit-to-Stand"}


def _value(source: Any, name: str, default=None):
    return getattr(source, name, default) if not isinstance(source, dict) else source.get(name, default)


def _dump(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, default=str)


def save_analysis_session(
    analysis_response: Any,
    source_filename: str | None = None,
    media_metadata: dict[str, Any] | None = None,
    db: Session | None = None,
    patient_id: str | None = None,
    owner_user_id: str | None = None,
    created_by_user_id: str | None = None,
) -> AnalysisSession:
    owns_session = db is None
    database = db or SessionLocal()
    session_id = str(uuid4())
    exercise_id = str(_value(analysis_response, "exercise", "bodyweight_squat"))
    confidence = _value(analysis_response, "analysis_confidence")
    pose_quality = _value(analysis_response, "pose_quality")
    issues = list(_value(analysis_response, "detected_issues", []) or [])
    try:
        valid_patient_id = None
        if patient_id and database.scalar(select(PatientProfile.patient_id).where(PatientProfile.patient_id == patient_id)):
            valid_patient_id = patient_id
        row = AnalysisSession(
            session_id=session_id, exercise_id=exercise_id,
            patient_id=valid_patient_id,
            owner_user_id=owner_user_id,
            created_by_user_id=created_by_user_id,
            exercise_display_name=DISPLAY_NAMES.get(exercise_id, exercise_id.replace("_", " ").title()),
            status=str(_value(analysis_response, "status", "unknown")),
            error_code=_value(analysis_response, "error_code"), message=_value(analysis_response, "message"),
            source_filename=source_filename,
            video_duration_sec=(media_metadata or {}).get("video_duration_sec"),
            total_reps=_value(analysis_response, "total_reps"),
            movement_score=_value(analysis_response, "movement_score"),
            rep_count_confidence=_value(analysis_response, "rep_count_confidence"),
            analysis_confidence_score=_value(confidence, "score"),
            analysis_confidence_level=_value(confidence, "level"),
            pose_quality_score=_value(pose_quality, "score"),
            pose_quality_level=_value(pose_quality, "level"),
            summary=_value(analysis_response, "summary"),
            limitations_json=_dump(_value(analysis_response, "limitations", []) or []),
            feedback_json=_dump(_value(analysis_response, "feedback", []) or []),
            detected_issues_json=_dump(issues),
            score_breakdown_json=_dump(_value(analysis_response, "score_breakdown")),
            input_validity_json=_dump(_value(analysis_response, "input_validity")),
            ml_prediction_json=_dump(_value(analysis_response, "ml_prediction")),
            report_id=_value(analysis_response, "report_id"),
            report_download_url=_value(analysis_response, "report_download_url"),
            overlay_id=_value(analysis_response, "overlay_id"),
            overlay_preview_url=_value(analysis_response, "overlay_preview_url"),
            overlay_download_url=_value(analysis_response, "overlay_download_url"),
        )
        database.add(row)
        metric_specs = (
            ("average_knee_angle", "degrees"), ("average_hip_angle", "degrees"),
            ("average_trunk_angle", "degrees"), ("total_reps", "reps"),
            ("movement_score", "score_0_100"),
        )
        for name, unit in metric_specs:
            value = _value(analysis_response, name)
            if value is not None:
                database.add(SessionMetric(
                    session_id=session_id, metric_name=name,
                    metric_value_float=float(value), unit=unit,
                ))
        for issue in issues:
            database.add(DetectedIssue(session_id=session_id, issue_code=str(issue)))
        if source_filename or media_metadata:
            metadata = media_metadata or {}
            database.add(UploadedMedia(
                session_id=session_id,
                original_filename=source_filename or str(metadata.get("original_filename", "unknown")),
                stored_path=None, content_type=metadata.get("content_type"),
                size_bytes=metadata.get("size_bytes"),
            ))
        database.commit()
        database.refresh(row)
        row.patient_assignment_warning = bool(patient_id and not valid_patient_id)
        return row
    except Exception:
        database.rollback()
        raise
    finally:
        if owns_session:
            database.close()
