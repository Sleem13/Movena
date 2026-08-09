import numpy as np

from app.ml.exercise_pose_features import (
    COCO_LANDMARK_NAMES,
    extract_mediapipe_frame_features,
    extract_pose_features,
    feature_columns,
)


def usable_pose():
    points = np.zeros((17, 2), dtype=float)
    points[5] = [0.0, 1.0]
    points[6] = [1.0, 1.0]
    points[11] = [0.0, 0.0]
    points[12] = [1.0, 0.0]
    points[7], points[8] = [0.0, 0.5], [1.0, 0.5]
    points[9], points[10] = [0.0, 0.0], [1.0, 0.0]
    points[13], points[14] = [0.1, -0.5], [0.9, -0.5]
    points[15], points[16] = [0.0, -1.0], [1.0, -1.0]
    return points, np.ones(17, dtype=float)


def test_feature_contract_is_ordered_and_camera_translation_invariant():
    points, confidence = usable_pose()
    first = extract_pose_features(points, confidence)
    second = extract_pose_features(points + np.asarray([200.0, 75.0]), confidence)
    assert first is not None and second is not None
    assert list(first) == feature_columns()
    assert len(first) == 40
    assert np.allclose(list(first.values()), list(second.values()))


def test_feature_contract_rejects_missing_critical_keypoint():
    points, confidence = usable_pose()
    confidence[5] = 0.1
    assert extract_pose_features(points, confidence) is None


def test_runtime_mediapipe_frame_maps_to_coco_feature_contract():
    landmarks = {
        name: {"x": float(index % 4), "y": float(index // 4), "visibility": 0.95}
        for index, name in enumerate(COCO_LANDMARK_NAMES)
    }
    landmarks.update({
        "left_shoulder": {"x": 0.0, "y": 1.0, "visibility": 0.95},
        "right_shoulder": {"x": 1.0, "y": 1.0, "visibility": 0.95},
        "left_hip": {"x": 0.0, "y": 0.0, "visibility": 0.95},
        "right_hip": {"x": 1.0, "y": 0.0, "visibility": 0.95},
    })
    result = extract_mediapipe_frame_features({"landmarks": landmarks})
    assert result is not None
    assert list(result) == feature_columns()
