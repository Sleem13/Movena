from app.exercises.shoulder_abduction.schemas import ShoulderAbductionCountResult, ShoulderAbductionRepEvent
from app.exercises.shoulder_abduction.scoring import score_shoulder_abduction
from app.schemas.analysis_schema import PoseQuality


def test_score_is_explainable_and_bounded():
    event = ShoulderAbductionRepEvent(0, 10, 20, 2.0, 10, 95, 85)
    count = ShoulderAbductionCountResult(total_reps=1, valid_reps=1, confidence=.9, rep_events=[event], rep_durations=[2.0])
    pose = PoseQuality(score=.9, level="high", total_frames=30, pose_detected_frames=30, pose_detection_rate=1, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)
    score = score_shoulder_abduction(count, pose, .9, [5] * 30)
    assert 0 <= score.total <= 100
    assert score.abduction_range_score >= 70
    assert score.rep_completion_score == 100
    assert "possible_trunk_compensation" not in score.issues
