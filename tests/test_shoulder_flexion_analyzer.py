import math

from app.exercises.shoulder_flexion.analyzer import shoulder_flexion_analyzer
from app.exercises.shoulder_flexion.schemas import ShoulderFlexionCountResult
from app.exercises.shoulder_flexion.state_machine import count_shoulder_flexion_reps
from app.exercises.shoulder_flexion.validity import validate_shoulder_flexion
from app.schemas.analysis_schema import PoseQuality


FLEXION_CYCLE = [20] * 5 + [35, 55, 80, 105, 120, 130, 132, 130] + [110, 85, 55, 35, 22, 20, 20]


def quality(frames=40):
    return PoseQuality(score=0.9, level="high", total_frames=frames, pose_detected_frames=frames, pose_detection_rate=1, average_visibility=0.9, critical_landmark_visibility=0.9, missing_critical_landmark_rate=0, low_confidence_frames=0)


def _frames():
    frames = []
    for index, angle in enumerate(FLEXION_CYCLE):
        radians = math.radians(angle)
        landmarks = {}
        for side, x, direction in (("left", 0.4, -1), ("right", 0.6, 1)):
            shoulder = {"x": x, "y": 0.35, "visibility": 0.95}
            wrist = {"x": x + direction * 0.28 * math.sin(radians), "y": 0.35 + 0.28 * math.cos(radians), "visibility": 0.95}
            elbow = {"x": (shoulder["x"] + wrist["x"]) / 2, "y": (shoulder["y"] + wrist["y"]) / 2, "visibility": 0.95}
            landmarks[f"{side}_shoulder"] = shoulder
            landmarks[f"{side}_hip"] = {"x": x, "y": 0.62, "visibility": 0.95}
            landmarks[f"{side}_elbow"] = elbow
            landmarks[f"{side}_wrist"] = wrist
            landmarks[f"{side}_knee"] = {"x": x, "y": 0.78, "visibility": 0.95}
            landmarks[f"{side}_ankle"] = {"x": x, "y": 0.90, "visibility": 0.95}
            landmarks[f"{side}_heel"] = {"x": x, "y": 0.91, "visibility": 0.95}
            landmarks[f"{side}_foot_index"] = {"x": x + 0.02, "y": 0.91, "visibility": 0.95}
        frames.append({"frame_index": index, "timestamp_sec": index * 0.1, "source_total_frames": len(FLEXION_CYCLE), "landmarks": landmarks})
    return frames


def test_lowered_raised_lowered_flexion_cycle_counts():
    result = count_shoulder_flexion_reps(FLEXION_CYCLE, [index * 0.1 for index in range(len(FLEXION_CYCLE))])
    assert result.total_reps == 1
    assert result.rep_events[0].maximum_angle >= 120


def test_static_flexion_sequence_is_rejected():
    result = validate_shoulder_flexion([25] * 40, ShoulderFlexionCountResult(), quality(), 0.9)
    assert not result.is_valid
    assert any("static" in warning.lower() for warning in result.warnings)


def test_shoulder_flexion_analyzer_succeeds_for_forward_raise():
    response = shoulder_flexion_analyzer.analyze_landmarks(_frames(), include_frame_data=True)
    assert response.status == "success"
    assert response.exercise_id == "shoulder_flexion"
    assert response.total_reps == 1
    assert response.average_shoulder_angle is not None
    assert response.frame_analysis[0].shoulder_angle is not None
