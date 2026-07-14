import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.sit_to_stand.schemas import SitToStandCountResult
from app.exercises.sit_to_stand.scoring import score_sit_to_stand
from app.schemas.analysis_schema import PoseQuality


def quality(score=0.9):
    return PoseQuality(
        score=score, level="high", total_frames=90, pose_detected_frames=90,
        pose_detection_rate=1, average_visibility=score, critical_landmark_visibility=score,
        missing_critical_landmark_rate=0, low_confidence_frames=0,
    )


def count(confidence=0.9):
    return SitToStandCountResult(total_reps=3, rep_durations=[2.5, 2.6, 2.4], confidence=confidence)


def test_excessive_trunk_lean_lowers_score():
    upright = score_sit_to_stand(count(), [15] * 90, quality())
    leaning = score_sit_to_stand(count(), [55] * 90, quality())
    assert leaning.trunk_control_score < upright.trunk_control_score
    assert leaning.total < upright.total
    assert "excessive_trunk_lean" in leaning.issues


def test_low_pose_quality_lowers_confidence_component():
    high = score_sit_to_stand(count(), [15] * 90, quality(0.9))
    low = score_sit_to_stand(count(0.5), [15] * 90, quality(0.4))
    assert low.pose_confidence_score < high.pose_confidence_score
    assert "low_confidence_tracking" in low.issues
