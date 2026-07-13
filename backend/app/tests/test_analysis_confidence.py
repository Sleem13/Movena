from app.schemas.analysis_schema import PoseQuality
from app.services.analysis_confidence_service import calculate_analysis_confidence


def pose(score):
    return PoseQuality(
        score=score, level="high" if score >= 0.8 else "low", total_frames=10,
        pose_detected_frames=10, pose_detection_rate=score, average_visibility=score,
        critical_landmark_visibility=score, missing_critical_landmark_rate=1-score,
        low_confidence_frames=0 if score >= 0.8 else 5, camera_view="front_or_oblique",
        warnings=[] if score >= 0.8 else ["Review recording quality."],
    )


def test_pose_quality_reduces_analysis_confidence():
    high = calculate_analysis_confidence(pose(0.95), 0.95, [170, 160, 150, 140])
    low = calculate_analysis_confidence(pose(0.3), 0.5, [170, 130, 170, 120])
    assert high.score > low.score
    assert low.level == "low"
    assert low.warnings
