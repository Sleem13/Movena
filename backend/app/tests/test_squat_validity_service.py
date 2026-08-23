from app.schemas.analysis_schema import PoseQuality
from app.services.squat_validity_service import validate_squat_attempt


def quality(frames=60, detection_rate=1.0, visibility=0.9):
    return PoseQuality(
        score=0.9,
        level="high",
        total_frames=frames,
        pose_detected_frames=frames,
        pose_detection_rate=detection_rate,
        average_visibility=visibility,
        critical_landmark_visibility=visibility,
        missing_critical_landmark_rate=0,
        low_confidence_frames=0,
        camera_view="front_or_oblique",
    )


def test_static_angle_sequence_is_invalid():
    result = validate_squat_attempt([165.0] * 60, [175.0] * 60, 0, quality())
    assert result.is_valid is False
    assert result.reason == "no_valid_squat_detected"
    assert result.motion_variation == 0
    assert any("static" in warning.lower() for warning in result.warnings)
    assert any("no complete squat" in warning.lower() for warning in result.warnings)


def test_low_visibility_body_is_invalid_even_with_motion():
    knees = ([170, 155, 135, 105, 135, 165] * 10)
    hips = ([175, 160, 135, 100, 135, 170] * 10)
    result = validate_squat_attempt(knees, hips, 3, quality(visibility=0.3))
    assert result.is_valid is False
    assert any("full body" in warning.lower() for warning in result.warnings)


def test_visible_complete_squat_attempt_is_valid():
    knees = ([170, 155, 135, 105, 135, 165] * 10)
    hips = ([175, 160, 135, 100, 135, 170] * 10)
    result = validate_squat_attempt(knees, hips, 3, quality())
    assert result.is_valid is True
    assert result.valid_reps == 3
    assert result.warnings == []


def test_sampled_video_is_not_mistaken_for_inconsistent_pose_detection():
    knees = [170, 155, 135, 105, 135, 165] * 10
    hips = [175, 160, 135, 100, 135, 170] * 10
    sampled_source_indexes = list(range(0, 180, 3))

    result = validate_squat_attempt(
        knees,
        hips,
        3,
        quality(frames=60),
        sampled_source_indexes,
        sample_stride=3,
    )

    assert result.is_valid is True
    assert result.pose_detection_rate == 1
    assert not any("not detected consistently" in warning.lower() for warning in result.warnings)
