from app.exercises.knee_extension.schemas import KneeExtensionCountResult
from app.exercises.knee_extension.validity import validate_knee_extension
from app.schemas.analysis_schema import PoseQuality


def quality(frames=40, rate=1.0):
    return PoseQuality(score=.9, level="high", total_frames=frames, pose_detected_frames=frames, pose_detection_rate=rate, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)


def test_static_sequence_fails_closed():
    validity = validate_knee_extension([100] * 40, KneeExtensionCountResult(), quality(), .9)
    assert not validity.is_valid
    assert any("static" in warning.lower() for warning in validity.warnings)
    assert any("No complete" in warning for warning in validity.warnings)


def test_complete_rep_with_visible_pose_is_valid():
    count = KneeExtensionCountResult(total_reps=1, valid_reps=1)
    assert validate_knee_extension([100, 170] * 20, count, quality(), .9).is_valid


def test_valid_synthetic_landmark_sequence_returns_success():
    angles = [100] * 5 + [110, 125, 140, 150, 158, 165, 170, 170, 168] + [155, 145, 130, 115, 105, 100, 100]
    frames = []
    for index, angle in enumerate(angles):
        radians = math.radians(angle)
        landmarks = {}
        for side, knee_x in (("left", .45), ("right", .65)):
            landmarks[f"{side}_shoulder"] = {"x": knee_x, "y": .2, "visibility": .95}
            landmarks[f"{side}_hip"] = {"x": knee_x, "y": .4, "visibility": .95}
            landmarks[f"{side}_knee"] = {"x": knee_x, "y": .5, "visibility": .95}
            landmarks[f"{side}_ankle"] = {"x": knee_x + .1 * math.sin(radians), "y": .5 - .1 * math.cos(radians), "visibility": .95}
            landmarks[f"{side}_heel"] = {"x": knee_x, "y": .7, "visibility": .95}
            landmarks[f"{side}_foot_index"] = {"x": knee_x + .05, "y": .7, "visibility": .95}
        frames.append({"frame_index": index, "timestamp_sec": index * .1, "source_total_frames": len(angles), "landmarks": landmarks})
    response = knee_extension_analyzer.analyze_landmarks(frames, include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.movement_score is not None
    assert response.frame_analysis
import math

from app.exercises.knee_extension.analyzer import knee_extension_analyzer
