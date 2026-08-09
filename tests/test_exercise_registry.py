import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.registry import registry
from app.exercises.base import ExerciseAnalyzer


def test_registry_contains_all_supported_rule_based_exercises():
    assert registry.available_exercises() == ("bicep_curl", "bodyweight_squat", "hip_abduction", "knee_extension", "push_up", "shoulder_abduction", "shoulder_press", "sit_to_stand")
    assert isinstance(registry.get("bodyweight_squat"), ExerciseAnalyzer)
    assert isinstance(registry.get("sit_to_stand"), ExerciseAnalyzer)
    assert registry.get("sit_to_stand").exercise_id == "sit_to_stand"
    assert registry.get("push_up").exercise_id == "push_up"
    assert registry.get("shoulder_press").exercise_id == "shoulder_press"
    assert registry.get("bicep_curl").exercise_id == "bicep_curl"
