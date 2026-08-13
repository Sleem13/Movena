"""Conservative extended-flexed-extended bicep-curl analyzer.

The analyzer observes elbow motion and upper-arm/trunk stability from 2D body
pose. It cannot assess resistance, safe load, forearm rotation, or grip type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import AnalysisConfidence, AnalysisResponse, FrameAnalysis, InputValidity, MLPrediction, RepEvent, ScoreBreakdown
from app.services.angle_calculation_service import calculate_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality
from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles


EXTENDED_ANGLE_MIN = 150.0
FLEXED_ANGLE_MAX = 75.0
MIN_ANGLE_RANGE = 70.0
MIN_PHASE_FRAMES = 3
MIN_FRAMES_BETWEEN_REPS = 3
MIN_REP_DURATION_SEC = 0.7
MAX_REP_DURATION_SEC = 10.0
MIN_POSE_DETECTED_FRAMES = 20
MIN_POSE_DETECTION_RATE = 0.45
MIN_VISIBILITY = 0.5
MIN_UPRIGHT_RATIO = 0.60
UPPER_ARM_DRIFT_ANGLE = 30.0
TRUNK_COMPENSATION_ANGLE = 20.0


@dataclass(frozen=True)
class CurlConfig:
    exercise_id: str = "bicep_curl"
    display_name: str = "Bicep Curl"
    error_code: str = "INVALID_BICEP_CURL_VIDEO"
    invalid_reason: str = "no_valid_bicep_curl"
    grip_note: str = "Body pose cannot verify grip orientation or distinguish a hammer curl reliably."


@dataclass(frozen=True)
class CurlRepEvent:
    start_frame: int
    flexed_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_angle: float
    maximum_angle: float


@dataclass
class CurlCountResult:
    total_reps: int = 0
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    rep_events: list[CurlRepEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)


def _filled(values: list[float | None], fallback: list[float]) -> list[float]:
    previous = next((float(value) for value in values if value is not None), fallback[0] if fallback else 0.0)
    result: list[float] = []
    for value in values:
        if value is not None:
            previous = float(value)
        result.append(round(previous, 2))
    return result


def count_bicep_curl_reps(
    angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
    low_confidence_mask: list[bool] | None = None,
    pose_quality_score: float = 1.0,
    pose_detection_rate: float = 1.0,
) -> CurlCountResult:
    """Count extended -> flexed -> extended cycles with noise hysteresis."""
    if not angles:
        return CurlCountResult()
    indexes = frame_indexes or list(range(len(angles)))
    processed = smooth_squat_angles(angles, low_confidence_mask)
    smoothed = _filled(processed, angles)
    phases = ["unreliable"] * len(smoothed)
    transitions: list[str] = []
    events: list[CurlRepEvent] = []
    state = "seeking_extended"
    extended_run = flexed_run = 0
    start_pos = flexed_pos = None
    minimum, maximum = 180.0, 0.0
    previous = None
    ignored = 0
    last_end_frame = -MIN_FRAMES_BETWEEN_REPS
    has_timing = bool(timestamps and len(timestamps) == len(smoothed) and timestamps[-1] > timestamps[0])

    def transition(next_state: str, position: int) -> None:
        nonlocal state
        transitions.append(f"{state}->{next_state}@{indexes[position]}")
        state = next_state

    def reset_extended(position: int) -> None:
        nonlocal extended_run, flexed_run, start_pos, flexed_pos, minimum, maximum
        transition("extended", position)
        extended_run, flexed_run = 1, 0
        start_pos = flexed_pos = None
        minimum = maximum = smoothed[position]

    for position, angle in enumerate(smoothed):
        if processed[position] is None or (position and indexes[position] - indexes[position - 1] > 3):
            if state in {"flexing", "flexed", "extending"}:
                ignored += 1
            state, extended_run, flexed_run, start_pos, flexed_pos, previous = "seeking_extended", 0, 0, None, None, None
            continue
        extended = angle >= EXTENDED_ANGLE_MIN
        flexed = angle <= FLEXED_ANGLE_MAX
        decreasing = previous is not None and angle < previous - 0.5
        increasing = previous is not None and angle > previous + 0.5
        if state == "seeking_extended":
            phases[position] = "extended" if extended else "unknown"
            extended_run = extended_run + 1 if extended else 0
            if extended_run >= MIN_PHASE_FRAMES:
                reset_extended(position)
        elif state == "extended":
            phases[position] = "extended"
            maximum = max(maximum, angle)
            if extended:
                extended_run += 1
            elif decreasing and indexes[position] - last_end_frame >= MIN_FRAMES_BETWEEN_REPS:
                start_pos = max(0, position - 1)
                transition("flexing", position)
                phases[position] = "flexing"
        elif state == "flexing":
            phases[position] = "flexing"
            minimum, maximum = min(minimum, angle), max(maximum, angle)
            flexed_run = flexed_run + 1 if flexed else 0
            if flexed_run >= MIN_PHASE_FRAMES:
                flexed_pos = position - MIN_PHASE_FRAMES + 1
                transition("flexed", position)
                for phase_pos in range(flexed_pos, position + 1):
                    phases[phase_pos] = "flexed"
            elif extended and not decreasing:
                if maximum - minimum >= MIN_ANGLE_RANGE / 2:
                    ignored += 1
                reset_extended(position)
        elif state == "flexed":
            phases[position] = "flexed"
            minimum = min(minimum, angle)
            if not flexed and increasing:
                transition("extending", position)
                phases[position] = "extending"
                extended_run = 0
        else:
            phases[position] = "extending"
            maximum = max(maximum, angle)
            extended_run = extended_run + 1 if extended else 0
            if extended_run >= MIN_PHASE_FRAMES:
                start = start_pos or 0
                duration = float(timestamps[position] - timestamps[start]) if has_timing and timestamps is not None else None
                valid_duration = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if flexed_pos is not None and maximum - minimum >= MIN_ANGLE_RANGE and valid_duration:
                    events.append(CurlRepEvent(indexes[start], indexes[flexed_pos], indexes[position], round(duration, 3) if duration is not None else None, round(minimum, 2), round(maximum, 2)))
                    last_end_frame = indexes[position]
                else:
                    ignored += 1
                reset_extended(position)
        previous = angle
    if state in {"flexing", "flexed", "extending"}:
        ignored += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    if events:
        completion = len(events) / (len(events) + ignored)
        range_clarity = mean(min(1.0, (event.maximum_angle - event.minimum_angle) / 100) for event in events)
        duration_consistency = max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else 0.85
        confidence = 0.30 * completion + 0.25 * (0.65 * pose_quality_score + 0.35 * pose_detection_rate) + 0.20 * range_clarity + 0.15 * compute_angle_stability(processed) + 0.10 * duration_consistency
    else:
        confidence = 0.0
    return CurlCountResult(len(events), ignored, round(max(0.0, min(1.0, confidence)), 3), events, [float(value) for value in durations], phases, transitions, smoothed)


def _visibility(frame: dict[str, Any], side: str) -> float:
    points = frame.get("landmarks", {})
    values = [float(points.get(f"{side}_{joint}", {}).get("visibility", 0)) for joint in ("shoulder", "elbow", "wrist", "hip")]
    return min(values) if values else 0.0


def _select_side(frames: list[dict[str, Any]]) -> str:
    scores = {side: mean(_visibility(frame, side) for frame in frames) for side in ("left", "right")}
    return max(scores, key=scores.get)


def _metrics(frame: dict[str, Any], side: str) -> tuple[float, float, float, bool, bool] | None:
    points = frame.get("landmarks", {})
    shoulder, elbow, wrist, hip = (points.get(f"{side}_{joint}") for joint in ("shoulder", "elbow", "wrist", "hip"))
    if not all((shoulder, elbow, wrist, hip)):
        return None
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    trunk_angle = calculate_trunk_angle(shoulder, hip)
    upper_arm_angle = calculate_trunk_angle(shoulder, elbow)
    upright = float(shoulder["y"]) < float(hip["y"]) and abs(float(shoulder["x"]) - float(hip["x"])) <= 0.15
    posture_ok = trunk_angle < TRUNK_COMPENSATION_ANGLE and upper_arm_angle < UPPER_ARM_DRIFT_ANGLE
    return elbow_angle, trunk_angle, upper_arm_angle, upright, posture_ok


def _feedback(issues: list[str], grip_note: str) -> list[str]:
    messages = {
        "incomplete_repetition": "Return to the visible extended starting position before beginning the next repetition.",
        "limited_observed_flexion_range": "The system observed limited elbow-flexion range in some repetitions.",
        "possible_upper_arm_drift": "The 2D view suggests that the upper arm moved substantially during some frames.",
        "possible_trunk_compensation": "The 2D view suggests trunk movement during some repetitions.",
        "upright_curl_position_not_visible": "Record from the front or slight side with the shoulder, elbow, wrist, and trunk visible in an upright position.",
        "no_complete_curl": "No complete visible extended-flexed-extended curl repetition was detected.",
    }
    result = [messages[issue] for issue in issues if issue in messages]
    if not result:
        result.append("The observed repetitions were completed with a generally controlled visible elbow movement pattern.")
    result.extend([grip_note, "This educational feedback does not assess resistance or safe load and does not replace a licensed physiotherapist."])
    return result


class BicepCurlAnalyzer(ExerciseAnalyzer):
    def __init__(self, config: CurlConfig | None = None) -> None:
        self.config = config or CurlConfig()
        self.exercise_id = self.config.exercise_id

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(extract_pose_landmarks(video_path), bool(options.get("include_frame_data")))

    def count_reps(self, *args: Any, **kwargs: Any) -> CurlCountResult:
        return count_bicep_curl_reps(*args, **kwargs)

    def validate_input(self, *, count: CurlCountResult, pose_quality: Any, visibility: float, upright_ratio: float) -> tuple[bool, list[str]]:
        warnings: list[str] = []
        if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES or pose_quality.pose_detection_rate < MIN_POSE_DETECTION_RATE:
            warnings.append("Too few usable pose-detected frames were available.")
        if visibility < MIN_VISIBILITY:
            warnings.append("The shoulder, elbow, wrist, or hip was not consistently visible.")
        if upright_ratio < MIN_UPRIGHT_RATIO:
            warnings.append("upright_curl_position_not_visible")
        if count.total_reps < 1:
            warnings.append("No complete extended-flexed-extended curl repetition was detected.")
        return not warnings, warnings

    def score_movement(self, count: CurlCountResult, visibility: float, posture_ratio: float) -> tuple[int, ScoreBreakdown, list[str]]:
        ranges = [event.maximum_angle - event.minimum_angle for event in count.rep_events]
        flexion_range = round(min(100, 100 * mean(ranges) / 100)) if ranges else 0
        completion = round(100 * count.total_reps / max(1, count.total_reps + count.ignored_partial_reps))
        durations = count.rep_durations
        consistency = round(max(0, 100 * (1 - pstdev(durations) / mean(durations)))) if len(durations) > 1 and mean(durations) else 85
        control = round(min(100, 100 * count.confidence))
        posture = round(100 * max(0.0, min(1.0, 0.55 * visibility + 0.45 * posture_ratio)))
        issues: list[str] = []
        if count.ignored_partial_reps:
            issues.append("incomplete_repetition")
        if ranges and mean(ranges) < 85:
            issues.append("limited_observed_flexion_range")
        if posture_ratio < 0.75:
            issues.append("possible_upper_arm_drift")
        total = round(0.25 * flexion_range + 0.20 * completion + 0.20 * consistency + 0.15 * control + 0.20 * posture)
        return total, ScoreBreakdown(extension_range_score=flexion_range, control_score=control, consistency_score=consistency, posture_visibility_score=posture, rep_completion_score=completion, pose_confidence_score=round(visibility * 100)), issues

    def generate_feedback(self, issues: list[str]) -> list[str]:
        return _feedback(issues, self.config.grip_note)

    def _ml_unavailable(self) -> MLPrediction:
        return MLPrediction(enabled=False, model_version="not_applicable", warning=f"Recognition may suggest {self.config.display_name.lower()}, but recognition confidence is not form evidence and cannot verify grip or load.")

    def _empty_rejection(self) -> AnalysisResponse:
        return AnalysisResponse(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name=self.config.display_name, status="rejected", error_code=self.config.error_code, message=f"No valid {self.config.display_name.lower()} movement was detected.", movement_score=None, valid_reps=0, detected_issues=["no_complete_curl"], feedback=self.generate_feedback(["no_complete_curl"]), ml_prediction=self._ml_unavailable(), limitations=["No usable pose-detected frames were available."])

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()
        side = _select_side(frames)
        usable = [(frame, metric) for frame in frames if (metric := _metrics(frame, side)) is not None]
        if not usable:
            return self._empty_rejection()
        usable_frames = [item[0] for item in usable]
        angles = [item[1][0] for item in usable]
        trunks = [item[1][1] for item in usable]
        upper_arms = [item[1][2] for item in usable]
        upright = [item[1][3] for item in usable]
        posture = [item[1][4] for item in usable]
        visibilities = [_visibility(frame, side) for frame in usable_frames]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(usable_frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(usable_frames)]
        quality = assess_pose_quality(frames)
        visibility = round(mean(visibilities), 3)
        upright_ratio = sum(upright) / len(upright)
        posture_ratio = sum(posture) / len(posture)
        count = count_bicep_curl_reps(angles, timestamps, indexes, [bool(frame.get("low_confidence", False)) or value < MIN_VISIBILITY for frame, value in zip(usable_frames, visibilities)], quality.score, quality.pose_detection_rate)
        is_valid, warnings = self.validate_input(count=count, pose_quality=quality, visibility=visibility, upright_ratio=upright_ratio)
        input_validity = InputValidity(is_valid=is_valid, reason=None if is_valid else self.config.invalid_reason, pose_detected_frames=quality.pose_detected_frames, pose_detection_rate=quality.pose_detection_rate, overall_pose_detection_rate=quality.pose_detection_rate, critical_landmark_visibility=visibility, knee_angle_range=0, hip_angle_range=0, motion_variation=round(max(angles) - min(angles), 2), valid_reps=count.total_reps, warnings=warnings)
        confidence_score = round(min(1.0, 0.50 * count.confidence + 0.20 * quality.score + 0.15 * visibility + 0.15 * upright_ratio), 3)
        confidence = AnalysisConfidence(score=confidence_score if is_valid else min(0.39, confidence_score), level="high" if is_valid and confidence_score >= 0.8 else "medium" if is_valid and confidence_score >= 0.6 else "low", reasons=[f"Rep-count confidence was {round(count.confidence * 100)}%.", f"Selected {side}-side visibility was {round(visibility * 100)}%.", f"Frames matching an upright curl position: {round(upright_ratio * 100)}%."], warnings=warnings)
        common = dict(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name=self.config.display_name, total_reps=count.total_reps, valid_reps=count.total_reps, average_elbow_angle=round(mean(angles), 2), average_trunk_angle=round(mean(trunks), 2), rep_events=[RepEvent(start_frame=event.start_frame, bottom_frame=event.flexed_frame, end_frame=event.end_frame, duration_sec=event.duration_sec, minimum_knee_angle=event.minimum_angle, maximum_knee_angle=event.maximum_angle) for event in count.rep_events], rep_durations=count.rep_durations, ignored_partial_reps=count.ignored_partial_reps, rep_count_confidence=count.confidence, phase_transitions=count.phase_transitions, pose_quality=quality, analysis_confidence=confidence, input_validity=input_validity, validation_warnings=warnings, ml_prediction=self._ml_unavailable())
        limitations = ["Synthetic tests cover the current state machine; reviewed real-video validation is not available.", "2D body pose cannot verify grip, forearm rotation, resistance, safe load, pain, tissue status, or treatment suitability.", self.config.grip_note, "Stop if pain, dizziness, numbness, or unusual symptoms occur."]
        if not is_valid:
            issues = ["upright_curl_position_not_visible"] if upright_ratio < MIN_UPRIGHT_RATIO else ["no_complete_curl"]
            return AnalysisResponse(**common, status="rejected", error_code=self.config.error_code, message=f"No valid {self.config.display_name.lower()} movement was detected.", movement_score=None, detected_issues=issues, feedback=self.generate_feedback(issues), summary=f"The recording did not contain a complete visible upright {self.config.display_name.lower()} repetition.", limitations=limitations)
        score, breakdown, issues = self.score_movement(count, visibility, posture_ratio)
        frame_rows = [FrameAnalysis(frame_index=indexes[index], timestamp_sec=timestamps[index], knee_angle=0, hip_angle=0, trunk_angle=round(trunks[index], 2), elbow_angle=count.smoothed_angles[index], phase=count.phases[index], detected_issue="possible_upper_arm_drift" if upper_arms[index] >= UPPER_ARM_DRIFT_ANGLE else "possible_trunk_compensation" if trunks[index] >= TRUNK_COMPENSATION_ANGLE else None) for index in range(len(usable_frames))]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(**common, status="success", movement_score=score, score_breakdown=breakdown, detected_issues=issues, feedback=self.generate_feedback(issues), summary=f"Analyzed {len(usable_frames)} pose-detected frames using the {side} arm and counted {count.total_reps} complete {self.config.display_name.lower()} repetition{'s' if count.total_reps != 1 else ''}.", limitations=limitations, frame_analysis=frame_rows if include_frame_data else None)


bicep_curl_analyzer = BicepCurlAnalyzer()
hammer_curl_analyzer = BicepCurlAnalyzer(
    CurlConfig(
        exercise_id="hammer_curl",
        display_name="Hammer Curl",
        error_code="INVALID_HAMMER_CURL_VIDEO",
        invalid_reason="no_valid_hammer_curl",
        grip_note="Hammer-curl grip orientation cannot be confirmed from body pose alone; this analyzer evaluates the visible elbow-flexion pattern and flags grip evidence as limited.",
    )
)
