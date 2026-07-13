from app.schemas.analysis_schema import PoseQuality
from app.services.squat_scoring_service import score_squat


def quality(score=0.9, camera_view="front_or_oblique"):
    return PoseQuality(
        score=score, level="high", total_frames=10, pose_detected_frames=10,
        pose_detection_rate=1, average_visibility=0.9,
        critical_landmark_visibility=0.9, missing_critical_landmark_rate=0,
        low_confidence_frames=0, camera_view=camera_view,
    )


def test_good_squat_dummy_data_has_high_explainable_score():
    score, breakdown = score_squat([170, 145, 105, 145, 170], [10] * 5, [False] * 5, quality(), [105])
    assert score >= 85
    assert breakdown.depth_score == 100


def test_shallow_squat_lowers_depth_score():
    _, good = score_squat([170, 105, 170], [10] * 3, [False] * 3, quality(), [105])
    _, shallow = score_squat([170, 140, 170], [10] * 3, [False] * 3, quality(), [140])
    assert shallow.depth_score < good.depth_score


def test_excessive_trunk_lean_lowers_trunk_control_score():
    _, upright = score_squat([170, 105, 170], [10] * 3, [False] * 3, quality(), [105])
    _, leaning = score_squat([170, 105, 170], [55] * 3, [False] * 3, quality(), [105])
    assert leaning.trunk_control_score < upright.trunk_control_score


def test_side_view_moderates_knee_alignment_penalty():
    _, front = score_squat([170, 105, 170], [10] * 3, [True] * 3, quality(), [105])
    _, side = score_squat([170, 105, 170], [10] * 3, [True] * 3, quality(camera_view="side_or_oblique"), [105])
    assert side.knee_alignment_score > front.knee_alignment_score
