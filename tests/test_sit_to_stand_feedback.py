import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.sit_to_stand.feedback import build_sit_to_stand_feedback


def test_feedback_is_supportive_and_non_diagnostic():
    feedback = " ".join(build_sit_to_stand_feedback(["incomplete_stand", "excessive_trunk_lean"]))
    assert "stand up fully" in feedback
    assert "licensed physiotherapist" in feedback
    assert "fall risk" not in feedback.lower()
    assert "diagnos" not in feedback.lower()
