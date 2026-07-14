import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.registry import registry
from app.exercises.base import ExerciseAnalyzer


def test_registry_contains_squat_and_sit_to_stand():
    assert registry.available_exercises() == ("bodyweight_squat", "sit_to_stand")
    assert isinstance(registry.get("bodyweight_squat"), ExerciseAnalyzer)
    assert isinstance(registry.get("sit_to_stand"), ExerciseAnalyzer)
    assert registry.get("sit_to_stand").exercise_id == "sit_to_stand"
