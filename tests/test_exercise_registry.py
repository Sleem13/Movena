import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.registry import registry
from app.exercises.base import ExerciseAnalyzer


def test_registry_contains_all_supported_rule_based_exercises():
    assert registry.available_exercises() == ("balance", "bicep_curl", "bodyweight_squat", "hammer_curl", "hip_abduction", "knee_extension", "push_up", "shoulder_abduction", "shoulder_flexion", "shoulder_press", "sit_to_stand", "walking_gait_screen")
    assert isinstance(registry.get("bodyweight_squat"), ExerciseAnalyzer)
    assert isinstance(registry.get("sit_to_stand"), ExerciseAnalyzer)
    assert registry.get("sit_to_stand").exercise_id == "sit_to_stand"
    assert registry.get("push_up").exercise_id == "push_up"
    assert registry.get("shoulder_press").exercise_id == "shoulder_press"
    assert registry.get("bicep_curl").exercise_id == "bicep_curl"
    assert registry.get("hammer_curl").exercise_id == "hammer_curl"
    assert registry.get("shoulder_flexion").exercise_id == "shoulder_flexion"
    assert registry.get("walking_gait_screen").exercise_id == "walking_gait_screen"
    assert registry.get("balance").exercise_id == "balance"
