from app.exercises.hip_abduction.schemas import HipAbductionCountResult, HipAbductionRepEvent
from app.exercises.hip_abduction.scoring import score_hip_abduction
from app.schemas.analysis_schema import PoseQuality


def test_score_is_explainable_and_bounded():
    event = HipAbductionRepEvent(0, 10, 20, 2.0, 7, 36, 29)
    count = HipAbductionCountResult(total_reps=1, valid_reps=1, confidence=.9, rep_events=[event], rep_durations=[2.0])
    pose = PoseQuality(score=.9, level="high", total_frames=30, pose_detected_frames=30, pose_detection_rate=1, average_visibility=.9, critical_landmark_visibility=.9, missing_critical_landmark_rate=0, low_confidence_frames=0)
    score = score_hip_abduction(count, pose, .9, [4] * 30)
    assert 0 <= score.total <= 100
    assert score.abduction_range_score >= 70
    assert score.rep_completion_score == 100
    assert score.pelvis_trunk_stability_score == 100
