import numpy as np
import pytest

from app.services.prmd_feature_adapter_service import (
    PRMDFeatureCompatibilityError,
    extract_prmd_frame_features,
    normalize_prmd_sequence,
    prepare_prmd_model_input,
)


LANDMARK_NAMES = (
    "nose",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_foot_index",
    "right_foot_index",
)


def _frame() -> dict[str, object]:
    points = {
        name: {"x": 0.1 + index * 0.03, "y": 0.2 + index * 0.02, "z": index * 0.01, "visibility": 0.95}
        for index, name in enumerate(LANDMARK_NAMES)
    }
    points["left_hip"] = {"x": 0.4, "y": 0.6, "z": 0.0, "visibility": 0.95}
    points["right_hip"] = {"x": 0.6, "y": 0.6, "z": 0.0, "visibility": 0.95}
    points["left_shoulder"] = {"x": 0.4, "y": 0.3, "z": 0.0, "visibility": 0.95}
    points["right_shoulder"] = {"x": 0.6, "y": 0.3, "z": 0.0, "visibility": 0.95}
    return {"landmarks": points}


def test_extracts_source_prmd_joint_order_and_coordinate_orientation():
    features = extract_prmd_frame_features(_frame()).reshape(22, 3)

    np.testing.assert_allclose(features[0], [0.5, -0.6, 0.0])
    np.testing.assert_allclose(features[1], [0.4, -0.6, 0.0])
    np.testing.assert_allclose(features[2], [0.5, -0.3, 0.0])
    np.testing.assert_allclose(features[3], features[2])
    np.testing.assert_allclose(features[8], features[9])
    np.testing.assert_allclose(features[18], features[1])


def test_mirror_negates_x_without_changing_y_or_z():
    normal = extract_prmd_frame_features(_frame()).reshape(22, 3)
    mirrored = extract_prmd_frame_features(_frame(), mirror_x=True).reshape(22, 3)

    np.testing.assert_allclose(mirrored[:, 0], -normal[:, 0])
    np.testing.assert_allclose(mirrored[:, 1:], normal[:, 1:])


def test_prepares_pelvis_normalized_model_shape():
    prepared = prepare_prmd_model_input(
        [_frame(), _frame()],
        target_frames=5,
        normalizer="pelvis_width",
    )
    joints = prepared.reshape(5, 22, 3)

    assert prepared.shape == (1, 5, 66)
    assert prepared.dtype == np.float32
    np.testing.assert_allclose(joints[:, 0, :], 0.0, atol=1e-6)
    np.testing.assert_allclose(
        np.linalg.norm(joints[:, 18, :] - joints[:, 14, :], axis=1),
        1.0,
        atol=1e-6,
    )


def test_rejects_missing_and_low_visibility_landmarks():
    missing = _frame()
    del missing["landmarks"]["left_knee"]
    with pytest.raises(PRMDFeatureCompatibilityError, match="left_knee"):
        extract_prmd_frame_features(missing)

    low_visibility = _frame()
    low_visibility["landmarks"]["right_wrist"]["visibility"] = 0.1
    with pytest.raises(PRMDFeatureCompatibilityError, match="right_wrist"):
        extract_prmd_frame_features(low_visibility)


def test_rejects_frame_quality_and_subject_continuity_warnings():
    low_confidence = _frame()
    low_confidence["low_confidence"] = True
    with pytest.raises(PRMDFeatureCompatibilityError, match="high-confidence"):
        extract_prmd_frame_features(low_confidence)

    subject_warning = _frame()
    subject_warning["subject_continuity_warning"] = "Possible subject switch."
    with pytest.raises(PRMDFeatureCompatibilityError, match="subject continuity"):
        extract_prmd_frame_features(subject_warning)


def test_rejects_incomplete_three_dimensional_coordinates():
    frame = _frame()
    del frame["landmarks"]["nose"]["z"]
    with pytest.raises(PRMDFeatureCompatibilityError, match="nose has invalid coordinates"):
        extract_prmd_frame_features(frame)


def test_rejects_empty_bad_shape_and_degenerate_scale():
    with pytest.raises(PRMDFeatureCompatibilityError, match="non-empty"):
        normalize_prmd_sequence([], target_frames=5, normalizer="pelvis_width")
    with pytest.raises(PRMDFeatureCompatibilityError, match=r"\(frames, 66\)"):
        normalize_prmd_sequence(np.zeros((2, 65)), target_frames=5, normalizer="pelvis_width")

    degenerate = extract_prmd_frame_features(_frame()).reshape(1, 66)
    joints = degenerate.reshape(1, 22, 3)
    joints[:, 14, :] = joints[:, 18, :]
    with pytest.raises(PRMDFeatureCompatibilityError, match="degenerate"):
        normalize_prmd_sequence(joints.reshape(1, 66), target_frames=5, normalizer="pelvis_width")
