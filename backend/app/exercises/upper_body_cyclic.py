"""Reusable, conservative elbow-cycle analyzers for upper-body exercises.

These engineering thresholds support educational movement review only. They are
not clinical cutoffs and deliberately reject recordings whose body geometry does
not match the selected exercise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import (
    AnalysisConfidence,
    AnalysisResponse,
    FrameAnalysis,
    InputValidity,
    MLPrediction,
    RepEvent,
    ScoreBreakdown,
)
from app.services.angle_calculation_service import calculate_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality
from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles


MIN_PHASE_FRAMES = 3
MIN_FRAMES_BETWEEN_REPS = 3
MIN_POSE_DETECTED_FRAMES = 20
MIN_VALID_FRAMES_RATIO = 0.45
MIN_VISIBILITY = 0.5
MIN_REP_DURATION_SEC = 0.7
MAX_REP_DURATION_SEC = 10.0


@dataclass(frozen=True)
class ElbowCycleEvent:
    start_frame: int
    extended_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_angle: float
    maximum_angle: float


@dataclass
class ElbowCycleResult:
    total_reps: int = 0
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    rep_events: list[ElbowCycleEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class UpperBodyExerciseConfig:
    exercise_id: str
    display_name: str
    error_code: str
    camera_view: str
    flexed_angle_max: float
    extended_angle_min: float
    min_angle_range: float
    geometry_issue: str
    min_geometry_ratio: float
    posture_issue: str
    success_geometry_label: str


PUSH_UP_CONFIG = UpperBodyExerciseConfig(
    exercise_id="push_up",
    display_name="Push-Up",
    error_code="INVALID_PUSH_UP_VIDEO",
    camera_view="A stable side view with the full body visible is preferred for push-up review.",
    flexed_angle_max=115.0,
    extended_angle_min=155.0,
    min_angle_range=45.0,
    geometry_issue="upright_or_incompatible_push_up_position",
    min_geometry_ratio=0.55,
    posture_issue="possible_hip_sag_or_pike",
    success_geometry_label="horizontal support position",
)


SHOULDER_PRESS_CONFIG = UpperBodyExerciseConfig(
    exercise_id="shoulder_press",
    display_name="Shoulder Press",
    error_code="INVALID_SHOULDER_PRESS_VIDEO",
    camera_view="A stable front or slight diagonal view with both arms and the trunk visible is preferred.",
    flexed_angle_max=120.0,
    extended_angle_min=155.0,
    min_angle_range=40.0,
    geometry_issue="no_visible_overhead_press_position",
    min_geometry_ratio=0.10,
    posture_issue="possible_trunk_compensation",
    success_geometry_label="overhead wrist position",
)


def _filled(values: list[float | None], fallback: list[float]) -> list[float]:
    previous = next((float(value) for value in values if value is not None), fallback[0] if fallback else 0.0)
    result: list[float] = []
    for value in values:
        if value is not None:
            previous = float(value)
        result.append(round(previous, 2))
    return result


def count_elbow_extension_cycles(
    angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
    low_confidence_mask: list[bool] | None = None,
    pose_quality_score: float = 1.0,
    pose_detection_rate: float = 1.0,
    *,
    config: UpperBodyExerciseConfig,
) -> ElbowCycleResult:
    """Count flexed -> extended -> flexed cycles with hysteresis and gap resets."""
    if not angles:
        return ElbowCycleResult()
    indexes = frame_indexes or list(range(len(angles)))
    processed = smooth_squat_angles(angles, low_confidence_mask)
    smoothed = _filled(processed, angles)
    phases = ["unreliable"] * len(smoothed)
    transitions: list[str] = []
    events: list[ElbowCycleEvent] = []
    state = "seeking_flexed"
    flexed_run = extended_run = 0
    start_pos = extended_pos = None
    minimum, maximum = 180.0, 0.0
    previous = None
    ignored = 0
    last_end_frame = -MIN_FRAMES_BETWEEN_REPS
    has_timing = bool(timestamps and len(timestamps) == len(smoothed) and timestamps[-1] > timestamps[0])

    def transition(next_state: str, position: int) -> None:
        nonlocal state
        transitions.append(f"{state}->{next_state}@{indexes[position]}")
        state = next_state

    def reset_flexed(position: int) -> None:
        nonlocal flexed_run, extended_run, start_pos, extended_pos, minimum, maximum
        transition("flexed", position)
        flexed_run, extended_run = 1, 0
        start_pos = extended_pos = None
        minimum = maximum = smoothed[position]

    for position, angle in enumerate(smoothed):
        if processed[position] is None or (position and indexes[position] - indexes[position - 1] > 3):
            if state in {"extending", "extended", "flexing"}:
                ignored += 1
            state, flexed_run, extended_run, start_pos, extended_pos, previous = "seeking_flexed", 0, 0, None, None, None
            continue
        flexed = angle <= config.flexed_angle_max
        extended = angle >= config.extended_angle_min
        increasing = previous is not None and angle > previous + 0.5
        decreasing = previous is not None and angle < previous - 0.5
        if state == "seeking_flexed":
            phases[position] = "flexed" if flexed else "unknown"
            flexed_run = flexed_run + 1 if flexed else 0
            if flexed_run >= MIN_PHASE_FRAMES:
                reset_flexed(position)
        elif state == "flexed":
            phases[position] = "flexed"
            minimum = min(minimum, angle)
            if flexed:
                flexed_run += 1
            elif increasing and indexes[position] - last_end_frame >= MIN_FRAMES_BETWEEN_REPS:
                start_pos = max(0, position - 1)
                transition("extending", position)
                phases[position] = "extending"
        elif state == "extending":
            phases[position] = "extending"
            minimum, maximum = min(minimum, angle), max(maximum, angle)
            extended_run = extended_run + 1 if extended else 0
            if extended_run >= MIN_PHASE_FRAMES:
                extended_pos = position - MIN_PHASE_FRAMES + 1
                transition("extended", position)
                for phase_pos in range(extended_pos, position + 1):
                    phases[phase_pos] = "extended"
            elif flexed and not increasing:
                if maximum - minimum >= config.min_angle_range / 2:
                    ignored += 1
                reset_flexed(position)
        elif state == "extended":
            phases[position] = "extended"
            maximum = max(maximum, angle)
            if not extended and decreasing:
                transition("flexing", position)
                phases[position] = "flexing"
                flexed_run = 0
        else:
            phases[position] = "flexing"
            minimum = min(minimum, angle)
            flexed_run = flexed_run + 1 if flexed else 0
            if flexed_run >= MIN_PHASE_FRAMES:
                start = start_pos or 0
                duration = float(timestamps[position] - timestamps[start]) if has_timing and timestamps is not None else None
                valid_duration = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if extended_pos is not None and maximum - minimum >= config.min_angle_range and valid_duration:
                    events.append(ElbowCycleEvent(indexes[start], indexes[extended_pos], indexes[position], round(duration, 3) if duration is not None else None, round(minimum, 2), round(maximum, 2)))
                    last_end_frame = indexes[position]
                else:
                    ignored += 1
                reset_flexed(position)
        previous = angle
    if state in {"extending", "extended", "flexing"}:
        ignored += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    if events:
        completion = len(events) / (len(events) + ignored)
        range_clarity = mean(min(1.0, (event.maximum_angle - event.minimum_angle) / 70) for event in events)
        duration_consistency = max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else 0.85
        confidence = 0.30 * completion + 0.25 * (0.65 * pose_quality_score + 0.35 * pose_detection_rate) + 0.20 * range_clarity + 0.15 * compute_angle_stability(processed) + 0.10 * duration_consistency
    else:
        confidence = 0.0
    return ElbowCycleResult(len(events), ignored, round(max(0.0, min(1.0, confidence)), 3), events, [float(value) for value in durations], phases, transitions, smoothed)


def _point_visibility(frame: dict[str, Any], side: str, exercise_id: str) -> float:
    points = frame.get("landmarks", {})
    joints = ("shoulder", "elbow", "wrist", "hip", "ankle") if exercise_id == "push_up" else ("shoulder", "elbow", "wrist", "hip")
    values = [float(points.get(f"{side}_{joint}", {}).get("visibility", 0)) for joint in joints]
    return min(values) if values else 0.0


def _select_side(frames: list[dict[str, Any]], exercise_id: str) -> str:
    scores = {side: mean(_point_visibility(frame, side, exercise_id) for frame in frames) for side in ("left", "right")}
    return max(scores, key=scores.get)


def _metrics(frame: dict[str, Any], side: str, exercise_id: str) -> tuple[float, float, float, bool, bool] | None:
    points = frame.get("landmarks", {})
    shoulder, elbow, wrist, hip, ankle = (points.get(f"{side}_{joint}") for joint in ("shoulder", "elbow", "wrist", "hip", "ankle"))
    if not all((shoulder, elbow, wrist, hip)) or (exercise_id == "push_up" and not ankle):
        return None
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    trunk_angle = calculate_trunk_angle(shoulder, hip)
    if exercise_id == "push_up":
        horizontal_span = abs(float(shoulder["x"]) - float(ankle["x"]))
        vertical_span = abs(float(shoulder["y"]) - float(ankle["y"]))
        geometry_ok = horizontal_span >= 0.18 and vertical_span / max(horizontal_span, 0.001) <= 0.85
        posture_ok = calculate_angle(shoulder, hip, ankle) >= 155.0
    else:
        geometry_ok = float(wrist["y"]) < float(shoulder["y"]) - 0.03 and elbow_angle >= 145.0
        posture_ok = trunk_angle < 22.0
    return elbow_angle, trunk_angle, _point_visibility(frame, side, exercise_id), geometry_ok, posture_ok


def _feedback(config: UpperBodyExerciseConfig, issues: list[str]) -> list[str]:
    messages = {
        "incomplete_repetition": "Return to the visible starting position before beginning the next repetition.",
        "limited_observed_extension_range": "The system observed limited elbow-extension range in some repetitions.",
        "upright_or_incompatible_push_up_position": "Record from the side with shoulders, hips, and ankles visible in a horizontal support position.",
        "no_visible_overhead_press_position": "Keep the wrist and elbow visible through the overhead position.",
        "possible_hip_sag_or_pike": "The 2D view suggests that the shoulder, hip, and ankle line changed during some frames.",
        "possible_trunk_compensation": "The 2D view suggests trunk movement during some overhead frames.",
        "no_complete_cycle": f"No complete visible {config.display_name.lower()} cycle was detected.",
    }
    result = [messages[issue] for issue in issues if issue in messages]
    if not result:
        result.append("The observed repetitions were completed with a generally controlled visible movement pattern.")
    result.append("This educational feedback does not replace assessment by a licensed physiotherapist.")
    return result


class UpperBodyCyclicAnalyzer(ExerciseAnalyzer):
    def __init__(self, config: UpperBodyExerciseConfig) -> None:
        self.config = config
        self.exercise_id = config.exercise_id

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(extract_pose_landmarks(video_path), bool(options.get("include_frame_data")))

    def count_reps(self, *args: Any, **kwargs: Any) -> ElbowCycleResult:
        return count_elbow_extension_cycles(*args, config=self.config, **kwargs)

    def validate_input(self, *, count: ElbowCycleResult, pose_quality: Any, visibility: float, geometry_ratio: float) -> tuple[bool, list[str]]:
        warnings: list[str] = []
        if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES or pose_quality.pose_detection_rate < MIN_VALID_FRAMES_RATIO:
            warnings.append("Too few usable pose-detected frames were available.")
        if visibility < MIN_VISIBILITY:
            warnings.append("Critical shoulder, elbow, wrist, hip, or ankle landmarks were not consistently visible.")
        if geometry_ratio < self.config.min_geometry_ratio:
            warnings.append(self.config.geometry_issue)
        if count.total_reps < 1:
            warnings.append("No complete flexed-extended-flexed repetition was detected.")
        return not warnings, warnings

    def score_movement(self, count: ElbowCycleResult, visibility: float, posture_ratio: float) -> tuple[int, ScoreBreakdown, list[str]]:
        events = count.rep_events
        ranges = [event.maximum_angle - event.minimum_angle for event in events]
        extension = round(min(100, 100 * mean(ranges) / 70)) if ranges else 0
        completion = round(100 * count.total_reps / max(1, count.total_reps + count.ignored_partial_reps))
        durations = count.rep_durations
        consistency = round(max(0, 100 * (1 - pstdev(durations) / mean(durations)))) if len(durations) > 1 and mean(durations) else 85
        control = round(min(100, 100 * count.confidence))
        posture = round(100 * max(0.0, min(1.0, 0.55 * visibility + 0.45 * posture_ratio)))
        issues: list[str] = []
        if count.ignored_partial_reps:
            issues.append("incomplete_repetition")
        if ranges and mean(ranges) < 55:
            issues.append("limited_observed_extension_range")
        if posture_ratio < 0.75:
            issues.append(self.config.posture_issue)
        total = round(0.25 * extension + 0.20 * completion + 0.20 * consistency + 0.15 * control + 0.20 * posture)
        return total, ScoreBreakdown(extension_range_score=extension, control_score=control, consistency_score=consistency, posture_visibility_score=posture, rep_completion_score=completion, pose_confidence_score=round(visibility * 100)), issues

    def generate_feedback(self, issues: list[str]) -> list[str]:
        return _feedback(self.config, issues)

    def _empty_rejection(self) -> AnalysisResponse:
        issue = "no_complete_cycle"
        return AnalysisResponse(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name=self.config.display_name, status="rejected", error_code=self.config.error_code, message=f"No valid {self.config.display_name.lower()} movement was detected.", movement_score=None, valid_reps=0, detected_issues=[issue], feedback=self.generate_feedback([issue]), ml_prediction=self._ml_unavailable(), limitations=["No usable pose-detected frames were available."])

    def _ml_unavailable(self) -> MLPrediction:
        return MLPrediction(enabled=False, model_version="not_applicable", warning=f"Recognition may suggest {self.config.display_name.lower()}, but this rule-based analyzer does not use recognition confidence as form evidence.")

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()
        side = _select_side(frames, self.exercise_id)
        usable = [(frame, metric) for frame in frames if (metric := _metrics(frame, side, self.exercise_id)) is not None]
        if not usable:
            return self._empty_rejection()
        usable_frames = [item[0] for item in usable]
        angles = [item[1][0] for item in usable]
        trunks = [item[1][1] for item in usable]
        visibilities = [item[1][2] for item in usable]
        geometry = [item[1][3] for item in usable]
        posture = [item[1][4] for item in usable]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(usable_frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(usable_frames)]
        quality = assess_pose_quality(frames)
        if (self.exercise_id == "push_up" and quality.camera_view != "side_or_oblique") or (self.exercise_id == "shoulder_press" and quality.camera_view == "side_or_oblique"):
            old_warning = quality.camera_view_warning
            quality.camera_view_warning = self.config.camera_view
            quality.warnings = [warning for warning in quality.warnings if warning != old_warning]
            quality.warnings.insert(0, quality.camera_view_warning)
        visibility = round(mean(visibilities), 3)
        geometry_ratio = sum(geometry) / len(geometry)
        posture_ratio = sum(posture) / len(posture)
        count = count_elbow_extension_cycles(angles, timestamps, indexes, [bool(frame.get("low_confidence", False)) or value < MIN_VISIBILITY for frame, value in zip(usable_frames, visibilities)], quality.score, quality.pose_detection_rate, config=self.config)
        is_valid, warnings = self.validate_input(count=count, pose_quality=quality, visibility=visibility, geometry_ratio=geometry_ratio)
        input_validity = InputValidity(is_valid=is_valid, reason=None if is_valid else "no_valid_exercise_cycle", pose_detected_frames=quality.pose_detected_frames, pose_detection_rate=quality.pose_detection_rate, overall_pose_detection_rate=quality.pose_detection_rate, critical_landmark_visibility=visibility, knee_angle_range=0, hip_angle_range=0, motion_variation=round(max(angles) - min(angles), 2), valid_reps=count.total_reps, warnings=warnings)
        confidence_score = round(min(1.0, 0.50 * count.confidence + 0.20 * quality.score + 0.15 * visibility + 0.15 * geometry_ratio), 3)
        confidence = AnalysisConfidence(score=confidence_score if is_valid else min(0.39, confidence_score), level="high" if is_valid and confidence_score >= 0.8 else "medium" if is_valid and confidence_score >= 0.6 else "low", reasons=[f"Rep-count confidence was {round(count.confidence * 100)}%.", f"Selected {side}-side landmark visibility was {round(visibility * 100)}%.", f"Frames matching the required {self.config.success_geometry_label}: {round(geometry_ratio * 100)}%."], warnings=warnings)
        common = dict(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name=self.config.display_name, total_reps=count.total_reps, valid_reps=count.total_reps, average_elbow_angle=round(mean(angles), 2), average_trunk_angle=round(mean(trunks), 2), rep_events=[RepEvent(start_frame=event.start_frame, standing_frame=event.extended_frame, end_frame=event.end_frame, duration_sec=event.duration_sec, minimum_knee_angle=event.minimum_angle, maximum_knee_angle=event.maximum_angle) for event in count.rep_events], rep_durations=count.rep_durations, ignored_partial_reps=count.ignored_partial_reps, rep_count_confidence=count.confidence, phase_transitions=count.phase_transitions, pose_quality=quality, analysis_confidence=confidence, input_validity=input_validity, validation_warnings=warnings, ml_prediction=self._ml_unavailable())
        limitations = ["Rule-based thresholds are adjustable engineering defaults and are not clinically validated.", self.config.camera_view, "2D pose does not measure strength, pain, load, tissue status, joint loading, or treatment suitability.", "Stop if pain, dizziness, numbness, or unusual symptoms occur; seek professional review when appropriate."]
        if not is_valid:
            issues = [self.config.geometry_issue] if geometry_ratio < self.config.min_geometry_ratio else ["no_complete_cycle"]
            return AnalysisResponse(**common, status="rejected", error_code=self.config.error_code, message=f"No valid {self.config.display_name.lower()} movement was detected.", movement_score=None, detected_issues=issues, feedback=self.generate_feedback(issues), summary=f"The recording did not contain a complete visible {self.config.display_name.lower()} repetition in the required position.", limitations=limitations)
        score, breakdown, issues = self.score_movement(count, visibility, posture_ratio)
        frame_rows = [FrameAnalysis(frame_index=indexes[index], timestamp_sec=timestamps[index], knee_angle=0, hip_angle=0, trunk_angle=round(trunks[index], 2), elbow_angle=count.smoothed_angles[index], phase=count.phases[index], detected_issue=self.config.posture_issue if not posture[index] else None) for index in range(len(usable_frames))]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(**common, status="success", movement_score=score, score_breakdown=breakdown, detected_issues=issues, feedback=self.generate_feedback(issues), summary=f"Analyzed {len(usable_frames)} pose-detected frames using the {side} arm and counted {count.total_reps} complete {self.config.display_name.lower()} repetition{'s' if count.total_reps != 1 else ''}.", limitations=limitations, frame_analysis=frame_rows if include_frame_data else None)


push_up_analyzer = UpperBodyCyclicAnalyzer(PUSH_UP_CONFIG)
shoulder_press_analyzer = UpperBodyCyclicAnalyzer(SHOULDER_PRESS_CONFIG)
