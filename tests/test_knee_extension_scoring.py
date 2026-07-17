from app.exercises.knee_extension.schemas import KneeExtensionCountResult, KneeExtensionRepEvent
from app.exercises.knee_extension.scoring import score_knee_extension
from app.schemas.analysis_schema import PoseQuality


def test_score_has_explainable_components_and_safe_issue_codes():
    event = KneeExtensionRepEvent(0, 10, 20, 2.0, 100, 170, 70)
    count = KneeExtensionCountResult(total_reps=1, valid_reps=1, confidence=.9, rep_events=[event], rep_durations=[2.0])
    pose = PoseQuality(score=.9, level="high", total_frames=30, pose_detected_frames=30, pose_detection_rate=1, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)
    score = score_knee_extension(count, pose, .9, [5] * 30)
    assert 0 <= score.total <= 100
    assert score.extension_range_score >= 80
    assert score.rep_completion_score == 100
    assert "possible_compensation" not in score.issues
