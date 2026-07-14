import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.sit_to_stand.schemas import SitToStandCountResult
from app.exercises.sit_to_stand.validity import validate_sit_to_stand
from app.schemas.analysis_schema import PoseQuality


def quality(score=0.9):
    return PoseQuality(
        score=score, level="high", total_frames=60, pose_detected_frames=60,
        pose_detection_rate=1, average_visibility=0.9, critical_landmark_visibility=0.9,
        missing_critical_landmark_rate=0, low_confidence_frames=0,
    )


def test_static_sequence_is_rejected():
    result = validate_sit_to_stand([90] * 60, [100] * 60, SitToStandCountResult(), quality())
    assert result.is_valid is False
    assert any("static" in warning for warning in result.warnings)


def test_standing_only_and_sitting_only_are_rejected():
    for value in (90, 170):
        result = validate_sit_to_stand([value] * 60, [value] * 60, SitToStandCountResult(), quality())
        assert result.is_valid is False
        assert result.valid_reps == 0
