from app.services.pose_quality_service import CRITICAL_LANDMARKS, assess_pose_quality


def frames(visibility=0.95, detected=10, total=10):
    landmarks = {
        name: {"x": 0.3 if "left" in name else 0.7, "y": 0.5, "visibility": visibility}
        for name in CRITICAL_LANDMARKS
    }
    return [
        {
            "frame_index": index,
            "source_total_frames": total,
            "landmarks": landmarks,
            "low_confidence": visibility < 0.45,
        }
        for index in range(detected)
    ]


def test_good_pose_quality_is_high():
    result = assess_pose_quality(frames())
    assert result.level == "high"
    assert result.pose_detection_rate == 1
    assert result.score >= 0.8


def test_low_visibility_and_missing_frames_reduce_confidence():
    result = assess_pose_quality(frames(visibility=0.2, detected=4, total=10))
    assert result.level == "low"
    assert result.pose_detection_rate == 0.4
    assert result.low_confidence_frames == 4
    assert result.warnings
