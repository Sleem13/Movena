"""Persist recognition outcomes without filenames, video bytes, or pose sequences."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RecognitionEvent


def save_recognition_event(
    result: dict[str, object],
    *,
    source_type: str,
    usable_pose_frames: int | None = None,
    actor_user_id: str | None = None,
    db: Session,
) -> RecognitionEvent | None:
    if result.get("status") not in {"success", "uncertain"}:
        return None
    model_id = str(result.get("model_id") or "")
    predicted = str(result.get("suggested_exercise_id") or "")
    if not model_id or not predicted:
        return None
    row = RecognitionEvent(
        event_id=str(uuid4()),
        actor_user_id=actor_user_id,
        model_id=model_id,
        source_type=source_type,
        status=str(result["status"]),
        predicted_exercise_id=predicted,
        confidence=float(result.get("confidence", 0.0)),
        confidence_threshold=(
            float(result["confidence_threshold"])
            if result.get("confidence_threshold") is not None else None
        ),
        abstained=result.get("status") == "uncertain",
        analyzer_available=bool(result.get("analyzer_available", False)),
        usable_pose_frames=usable_pose_frames,
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except Exception:
        db.rollback()
        raise


def confirm_recognition_event(
    event_id: str,
    confirmed_exercise_id: str,
    *,
    actor_user_id: str | None = None,
    db: Session,
) -> RecognitionEvent | None:
    row = db.scalar(select(RecognitionEvent).where(RecognitionEvent.event_id == event_id))
    if row is None:
        return None
    row.confirmed_exercise_id = confirmed_exercise_id
    row.confirmed_at = datetime.now(timezone.utc)
    if actor_user_id and not row.actor_user_id:
        row.actor_user_id = actor_user_id
    try:
        db.commit()
        db.refresh(row)
        return row
    except Exception:
        db.rollback()
        raise
