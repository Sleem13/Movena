import math

from app.exercises.shoulder_abduction.analyzer import shoulder_abduction_analyzer
from app.exercises.shoulder_abduction.schemas import ShoulderAbductionCountResult
from app.exercises.shoulder_abduction.validity import validate_shoulder_abduction
from app.schemas.analysis_schema import PoseQuality


def quality(frames=40):
    return PoseQuality(score=.9, level="high", total_frames=frames, pose_detected_frames=frames, pose_detection_rate=1, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)


def test_static_sequence_is_rejected():
    result = validate_shoulder_abduction([25] * 40, ShoulderAbductionCountResult(), quality(), .9)
    assert not result.is_valid
    assert any("static" in warning.lower() for warning in result.warnings)


def test_valid_synthetic_landmarks_return_success():
    angles = [25] * 5 + [30, 45, 60, 78, 85, 90, 90, 88] + [70, 50, 35, 30, 25, 25, 25]
    frames = []
    for index, angle in enumerate(angles):
        radians = math.radians(angle)
        landmarks = {}
        for side, x, direction in (("left", .4, -1), ("right", .6, 1)):
            shoulder = {"x": x, "y": .35, "visibility": .95}
            landmarks[f"{side}_shoulder"] = shoulder
            landmarks[f"{side}_hip"] = {"x": x, "y": .6, "visibility": .95}
            landmarks[f"{side}_elbow"] = {"x": x + direction * .18 * math.sin(radians), "y": .35 + .18 * math.cos(radians), "visibility": .95}
            landmarks[f"{side}_wrist"] = {"x": x + direction * .32 * math.sin(radians), "y": .35 + .32 * math.cos(radians), "visibility": .95}
        frames.append({"frame_index": index, "timestamp_sec": index * .1, "source_total_frames": len(angles), "landmarks": landmarks})
    response = shoulder_abduction_analyzer.analyze_landmarks(frames, include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.movement_score is not None
    assert response.average_shoulder_angle is not None
    assert response.frame_analysis[0].shoulder_angle is not None
