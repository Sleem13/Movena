import math

from app.exercises.hip_abduction.analyzer import hip_abduction_analyzer
from app.exercises.hip_abduction.schemas import HipAbductionCountResult
from app.exercises.hip_abduction.validity import validate_hip_abduction
from app.schemas.analysis_schema import PoseQuality


def quality(frames=40):
    return PoseQuality(score=.9, level="high", total_frames=frames, pose_detected_frames=frames, pose_detection_rate=1, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)


def test_static_sequence_is_rejected():
    result = validate_hip_abduction([8] * 40, HipAbductionCountResult(), quality(), .9)
    assert not result.is_valid
    assert any("static" in warning.lower() for warning in result.warnings)


def test_valid_synthetic_landmarks_return_success():
    angles = [8] * 5 + [12, 18, 24, 28, 32, 35, 35, 33] + [25, 18, 12, 9, 8, 8, 8]
    frames = []
    for index, left_angle in enumerate(angles):
        landmarks = {}
        for side, x, angle, direction in (("left", .43, left_angle, -1), ("right", .57, 6, 1)):
            radians = math.radians(angle)
            landmarks[f"{side}_shoulder"] = {"x": x, "y": .2, "visibility": .95}
            landmarks[f"{side}_hip"] = {"x": x, "y": .45, "visibility": .95}
            landmarks[f"{side}_knee"] = {"x": x + direction * .15 * math.sin(radians), "y": .45 + .15 * math.cos(radians), "visibility": .95}
            landmarks[f"{side}_ankle"] = {"x": x + direction * .3 * math.sin(radians), "y": .45 + .3 * math.cos(radians), "visibility": .95}
        frames.append({"frame_index": index, "timestamp_sec": index * .1, "source_total_frames": len(angles), "landmarks": landmarks})
    response = hip_abduction_analyzer.analyze_landmarks(frames, include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.movement_score is not None
    assert response.average_hip_abduction_angle is not None
    assert response.frame_analysis[0].hip_abduction_angle is not None
