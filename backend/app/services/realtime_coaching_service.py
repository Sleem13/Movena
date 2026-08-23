"""Bounded, metadata-only state for authenticated real-time exercise coaching."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import AnalysisSession, SessionMetric


SUPPORTED_EXERCISES = {"bicep_curl", "hammer_curl", "bodyweight_squat", "shoulder_press", "shoulder_abduction"}
EXERCISE_NAMES = {
    "bicep_curl": "Bicep Curl",
    "hammer_curl": "Hammer Curl",
    "bodyweight_squat": "Bodyweight Squat",
    "shoulder_press": "Shoulder Press",
    "shoulder_abduction": "Lateral Raise",
}
MAX_MESSAGE_BYTES = 64 * 1024
MAX_SESSION_SECONDS = 15 * 60
MIN_FRAME_INTERVAL_MS = 90
MIN_VISIBILITY = 0.5
MIN_PHASE_FRAMES = 2
SQUAT_START_ANGLE = 155.0
SQUAT_BOTTOM_ANGLE = 125.0
NEUTRAL_GRIP_RATIO_MAX = 0.48
PALM_GRIP_RATIO_MIN = 0.68


def _angle(a: dict, b: dict, c: dict) -> float:
    ba = (float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))
    bc = (float(c["x"]) - float(b["x"]), float(c["y"]) - float(b["y"]))
    denominator = math.hypot(*ba) * math.hypot(*bc)
    if denominator <= 1e-9:
        return 0.0
    cosine = max(-1.0, min(1.0, (ba[0] * bc[0] + ba[1] * bc[1]) / denominator))
    return math.degrees(math.acos(cosine))


def _visible(point: dict | None) -> bool:
    return bool(point) and float(point.get("visibility", 1.0)) >= MIN_VISIBILITY


def _best_measurement(pose: list[dict], triples: tuple[tuple[str, tuple[int, int, int]], ...]) -> tuple[str, float, dict] | None:
    candidates: list[tuple[float, str, float, dict]] = []
    for side, indexes in triples:
        if max(indexes) >= len(pose):
            continue
        a, joint, c = (pose[index] for index in indexes)
        if not all(_visible(point) for point in (a, joint, c)):
            continue
        visibility = min(float(point.get("visibility", 1.0)) for point in (a, joint, c))
        candidates.append((visibility, side, _angle(a, joint, c), c))
    if not candidates:
        return None
    _, side, angle, endpoint = max(candidates, key=lambda item: item[0])
    return side, angle, endpoint


def _arm_measurement(pose: list[dict]) -> tuple[str, float, dict] | None:
    return _best_measurement(pose, (("left", (11, 13, 15)), ("right", (12, 14, 16))))


def _knee_measurement(pose: list[dict]) -> tuple[str, float, dict] | None:
    return _best_measurement(pose, (("left", (23, 25, 27)), ("right", (24, 26, 28))))


def _shoulder_measurement(pose: list[dict]) -> tuple[str, float, dict] | None:
    return _best_measurement(pose, (("left", (23, 11, 13)), ("right", (24, 12, 14))))


def _grip_evidence(hands: list[dict], wrist: dict) -> tuple[str, float | None]:
    closest: tuple[float, list[dict]] | None = None
    for hand in hands[:2]:
        landmarks = hand.get("landmarks") or []
        if len(landmarks) < 18:
            continue
        distance = math.hypot(float(landmarks[0]["x"]) - float(wrist["x"]), float(landmarks[0]["y"]) - float(wrist["y"]))
        if closest is None or distance < closest[0]:
            closest = (distance, landmarks)
    if closest is None or closest[0] > 0.20:
        return "unavailable", None
    index_mcp, pinky_mcp = closest[1][5], closest[1][17]
    dx = abs(float(index_mcp["x"]) - float(pinky_mcp["x"]))
    dy = abs(float(index_mcp["y"]) - float(pinky_mcp["y"]))
    ratio = dx / max(1e-6, math.hypot(dx, dy))
    if ratio <= NEUTRAL_GRIP_RATIO_MAX:
        return "neutral", round(ratio, 3)
    if ratio >= PALM_GRIP_RATIO_MIN:
        return "palm_facing", round(ratio, 3)
    return "uncertain", round(ratio, 3)


@dataclass
class RealtimeExerciseSession:
    user_id: str
    exercise_id: str
    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_timestamp_ms: float = -1
    frames_received: int = 0
    frames_dropped: int = 0
    reps: int = 0
    phase: str = "seeking_start"
    phase_run: int = 0
    rep_started_ms: float | None = None
    minimum_angle: float = 180.0
    maximum_angle: float = 0.0
    neutral_grip_frames: int = 0
    palm_grip_frames: int = 0
    grip_evidence_frames: int = 0

    def _configuration(self, pose: list[dict]) -> tuple[tuple[str, float, dict] | None, float, float, str]:
        if self.exercise_id == "bodyweight_squat":
            return _knee_measurement(pose), SQUAT_START_ANGLE, SQUAT_BOTTOM_ANGLE, "knee"
        if self.exercise_id == "shoulder_abduction":
            return _shoulder_measurement(pose), 30.0, 75.0, "shoulder"
        if self.exercise_id == "shoulder_press":
            return _arm_measurement(pose), 105.0, 155.0, "elbow"
        return _arm_measurement(pose), 150.0, 75.0, "elbow"

    def process_frame(self, payload: dict) -> list[dict]:
        timestamp_ms = float(payload.get("timestamp_ms", 0))
        if timestamp_ms <= self.last_timestamp_ms or (
            self.last_timestamp_ms >= 0 and timestamp_ms - self.last_timestamp_ms < MIN_FRAME_INTERVAL_MS
        ):
            self.frames_dropped += 1
            return []
        self.last_timestamp_ms = timestamp_ms
        self.frames_received += 1
        measurement, start_threshold, peak_threshold, joint = self._configuration(payload.get("pose_landmarks") or [])
        if measurement is None:
            return [{"type": "warning", "code": "POSE_NOT_VISIBLE", "message": f"Keep the working {joint} and connected joints visible."}]

        side, angle, endpoint = measurement
        ascending = peak_threshold > start_threshold
        at_start = angle <= start_threshold if ascending else angle >= start_threshold
        at_peak = angle >= peak_threshold if ascending else angle <= peak_threshold
        grip, grip_ratio = "not_applicable", None
        if self.exercise_id in {"bicep_curl", "hammer_curl"}:
            grip, grip_ratio = _grip_evidence(payload.get("hands") or [], endpoint)
            if grip != "unavailable":
                self.grip_evidence_frames += 1
            if grip == "neutral":
                self.neutral_grip_frames += 1
            elif grip == "palm_facing":
                self.palm_grip_frames += 1

        events: list[dict] = []
        if self.phase == "seeking_start":
            self.phase_run = self.phase_run + 1 if at_start else 0
            if self.phase_run >= MIN_PHASE_FRAMES:
                self.phase, self.phase_run = "ready", 0
        elif self.phase == "ready":
            if not at_start:
                self.phase = "working"
                self.rep_started_ms = timestamp_ms
                self.minimum_angle = self.maximum_angle = angle
        elif self.phase == "working":
            self.minimum_angle = min(self.minimum_angle, angle)
            self.maximum_angle = max(self.maximum_angle, angle)
            self.phase_run = self.phase_run + 1 if at_peak else 0
            if self.phase_run >= MIN_PHASE_FRAMES:
                self.phase, self.phase_run = "returning", 0
            elif at_start:
                # A partial attempt must not leave the session stuck in "working".
                # Reset so the next complete movement can be counted normally.
                self.phase, self.phase_run, self.rep_started_ms = "ready", 0, None
        elif self.phase == "returning":
            self.minimum_angle = min(self.minimum_angle, angle)
            self.maximum_angle = max(self.maximum_angle, angle)
            self.phase_run = self.phase_run + 1 if at_start else 0
            if self.phase_run >= MIN_PHASE_FRAMES:
                duration = (timestamp_ms - (self.rep_started_ms or timestamp_ms)) / 1000
                required_range = abs(peak_threshold - start_threshold) * 0.75
                if self.maximum_angle - self.minimum_angle >= required_range and 0.5 <= duration <= 12:
                    self.reps += 1
                    events.append({
                        "type": "rep_event", "rep_number": self.reps, "duration_sec": round(duration, 2),
                        "minimum_angle": round(self.minimum_angle, 1), "maximum_angle": round(self.maximum_angle, 1),
                        "joint": joint, "grip": grip, "exercise_id": self.exercise_id,
                    })
                self.phase, self.phase_run, self.rep_started_ms = "ready", 0, None

        expected_grip = "neutral" if self.exercise_id == "hammer_curl" else "palm_facing"
        events.insert(0, {
            "type": "frame_feedback", "phase": self.phase, "reps": self.reps, "side": side,
            "joint": joint, "joint_angle": round(angle, 1), "grip": grip, "grip_ratio": grip_ratio,
            "grip_matches_exercise": grip == expected_grip if self.exercise_id in {"bicep_curl", "hammer_curl"} else None,
        })
        return events

    def summary(self) -> dict:
        evidence = max(1, self.grip_evidence_frames)
        neutral_ratio = self.neutral_grip_frames / evidence
        palm_ratio = self.palm_grip_frames / evidence
        expected_ratio = neutral_ratio if self.exercise_id == "hammer_curl" else palm_ratio
        return {
            "type": "session_summary", "session_id": self.session_id, "exercise_id": self.exercise_id,
            "total_reps": self.reps, "frames_received": self.frames_received, "frames_dropped": self.frames_dropped,
            "grip_evidence_frames": self.grip_evidence_frames, "neutral_grip_ratio": round(neutral_ratio, 3),
            "palm_facing_grip_ratio": round(palm_ratio, 3),
            "grip_match_ratio": round(expected_ratio, 3) if self.exercise_id in {"bicep_curl", "hammer_curl"} else None,
        }

    def persist(self, db: Session) -> dict:
        summary = self.summary()
        row = AnalysisSession(
            session_id=self.session_id, owner_user_id=self.user_id, created_by_user_id=self.user_id,
            exercise_id=self.exercise_id, exercise_display_name=EXERCISE_NAMES[self.exercise_id],
            status="success" if self.reps else "completed_no_reps", total_reps=self.reps,
            rep_count_confidence=min(1.0, self.frames_received / 20),
            summary="Real-time session stored as derived metadata only; no camera frames or landmark sequences were retained.",
            limitations_json=json.dumps(["Camera-derived joint angles and hand orientation are coaching estimates, not load, pain, injury, or clinical assessments."]),
        )
        row.metrics.append(SessionMetric(metric_name="frames_received", metric_value_float=float(self.frames_received), unit="frames"))
        if self.exercise_id in {"bicep_curl", "hammer_curl"}:
            row.metrics.extend([
                SessionMetric(metric_name="grip_evidence_frames", metric_value_float=float(self.grip_evidence_frames), unit="frames"),
                SessionMetric(metric_name="grip_match_ratio", metric_value_float=float(summary["grip_match_ratio"]), unit="ratio"),
            ])
        db.add(row)
        db.commit()
        return summary


# Retain the public name used by existing imports and tests.
RealtimeCurlSession = RealtimeExerciseSession
