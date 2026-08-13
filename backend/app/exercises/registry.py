"""Small exercise registry; routing remains explicit for API stability."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.exercises.base import ExerciseAnalyzer


class ExerciseRegistry:
    def __init__(self) -> None:
        self._analyzers: dict[str, Any] = {}

    def register(self, exercise_id: str, analyzer: Any) -> None:
        if not exercise_id or exercise_id in self._analyzers:
            raise ValueError(f"Exercise analyzer already registered or invalid: {exercise_id}")
        self._analyzers[exercise_id] = analyzer

    def get(self, exercise_id: str) -> Any:
        try:
            return self._analyzers[exercise_id]
        except KeyError as exc:
            raise KeyError(f"Unsupported exercise: {exercise_id}") from exc

    def available_exercises(self) -> tuple[str, ...]:
        return tuple(sorted(self._analyzers))


registry = ExerciseRegistry()


class SquatAnalyzerAdapter(ExerciseAnalyzer):
    """Thin adapter that registers the stable squat pipeline without migrating it."""

    exercise_id = "bodyweight_squat"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> Any:
        from app.services.pose_estimation_service import extract_pose_landmarks
        from app.services.squat_analysis_service import analyze_squat_landmarks
        options = options or {}
        return analyze_squat_landmarks(
            extract_pose_landmarks(video_path),
            include_frame_data=bool(options.get("include_frame_data")),
        )

    def validate_input(self, *args: Any, **kwargs: Any) -> Any:
        from app.services.squat_validity_service import validate_squat_attempt
        return validate_squat_attempt(*args, **kwargs)

    def count_reps(self, *args: Any, **kwargs: Any) -> Any:
        from app.services.rep_counting_service import count_squat_reps
        return count_squat_reps(*args, **kwargs)

    def score_movement(self, *args: Any, **kwargs: Any) -> Any:
        from app.services.squat_scoring_service import score_squat
        return score_squat(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> Any:
        from app.services.feedback_service import build_feedback
        return build_feedback(*args, **kwargs)


registry.register("bodyweight_squat", SquatAnalyzerAdapter())

from app.exercises.sit_to_stand.analyzer import sit_to_stand_analyzer  # noqa: E402
from app.exercises.knee_extension.analyzer import knee_extension_analyzer  # noqa: E402
from app.exercises.shoulder_abduction.analyzer import shoulder_abduction_analyzer  # noqa: E402
from app.exercises.shoulder_flexion.analyzer import shoulder_flexion_analyzer  # noqa: E402
from app.exercises.hip_abduction.analyzer import hip_abduction_analyzer  # noqa: E402
from app.exercises.gait.analyzer import gait_analyzer  # noqa: E402
from app.exercises.balance.analyzer import balance_analyzer  # noqa: E402
from app.exercises.upper_body_cyclic import push_up_analyzer, shoulder_press_analyzer  # noqa: E402
from app.exercises.bicep_curl import bicep_curl_analyzer, hammer_curl_analyzer  # noqa: E402

registry.register("sit_to_stand", sit_to_stand_analyzer)
registry.register("knee_extension", knee_extension_analyzer)
registry.register("shoulder_abduction", shoulder_abduction_analyzer)
registry.register("shoulder_flexion", shoulder_flexion_analyzer)
registry.register("hip_abduction", hip_abduction_analyzer)
registry.register("walking_gait_screen", gait_analyzer)
registry.register("balance", balance_analyzer)
registry.register("push_up", push_up_analyzer)
registry.register("shoulder_press", shoulder_press_analyzer)
registry.register("bicep_curl", bicep_curl_analyzer)
registry.register("hammer_curl", hammer_curl_analyzer)
