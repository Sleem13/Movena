"""Product-facing exercise metadata; analyzer routing remains explicit."""

from __future__ import annotations

from pydantic import BaseModel


class ExerciseMetadata(BaseModel):
    exercise_id: str
    display_name: str
    supported_in_app: bool
    body_region: str
    exercise_family: str
    recommended_camera_view: str
    required_landmarks: list[str]
    movement_description: str
    expected_movement_pattern: str
    safety_notes: str
    endpoint_path: str | None = None
    ml_model_status: str = "experimental_not_applicable"
    recognition_status: str = "experimental_manual_selection_required"


_SUPPORTED = (
    ExerciseMetadata(
        exercise_id="bodyweight_squat", display_name="Bodyweight Squat", supported_in_app=True,
        body_region="Lower body and trunk", exercise_family="Squat", recommended_camera_view="Side or front/diagonal view",
        required_landmarks=["shoulders", "hips", "knees", "ankles", "feet"],
        movement_description="A controlled bodyweight squat through a comfortable range.",
        expected_movement_pattern="Perform 3–5 controlled squats with the full body visible.",
        safety_notes="Stop if pain, dizziness, or unusual symptoms occur; seek professional review when appropriate.",
        endpoint_path="/api/v1/analyze/squat", ml_model_status="optional_experimental_second_opinion",
    ),
    ExerciseMetadata(
        exercise_id="sit_to_stand", display_name="Sit-to-Stand", supported_in_app=True,
        body_region="Lower body and trunk", exercise_family="Functional transfer", recommended_camera_view="Side view preferred",
        required_landmarks=["shoulders", "hips", "knees", "ankles"],
        movement_description="A controlled rise from a stable chair followed by a return to sitting.",
        expected_movement_pattern="Show complete sitting, rising, standing, lowering, and return-to-sitting cycles.",
        safety_notes="Use a stable chair and stop if pain, dizziness, or unusual symptoms occur.",
        endpoint_path="/api/v1/analyze/sit-to-stand",
    ),
    ExerciseMetadata(
        exercise_id="knee_extension", display_name="Knee Extension", supported_in_app=True,
        body_region="Knee and lower limb", exercise_family="Seated open-chain movement", recommended_camera_view="Side view preferred",
        required_landmarks=["hip", "knee", "ankle"],
        movement_description="A seated knee extension from a flexed position and controlled return.",
        expected_movement_pattern="Extend the knee comfortably, pause if appropriate, then return with control.",
        safety_notes="Use a secure chair and stop if pain or unusual symptoms occur.",
        endpoint_path="/api/v1/analyze/knee-extension",
    ),
    ExerciseMetadata(
        exercise_id="shoulder_abduction", display_name="Shoulder Abduction", supported_in_app=True,
        body_region="Shoulder and upper limb", exercise_family="Upper-limb range of motion", recommended_camera_view="Front view preferred",
        required_landmarks=["shoulders", "elbows", "wrists", "trunk"],
        movement_description="An arm raise out to the side followed by a controlled return.",
        expected_movement_pattern="Raise the arm outward through a comfortable range and return to the side.",
        safety_notes="Stop if pain, numbness, dizziness, or unusual symptoms occur.",
        endpoint_path="/api/v1/analyze/shoulder-abduction",
    ),
    ExerciseMetadata(
        exercise_id="hip_abduction", display_name="Hip Abduction", supported_in_app=True,
        body_region="Hip and lower limb", exercise_family="Standing lower-limb range of motion", recommended_camera_view="Front view preferred",
        required_landmarks=["pelvis", "hips", "knees", "ankles", "trunk"],
        movement_description="A standing leg movement away from the body followed by a controlled return.",
        expected_movement_pattern="Move one leg outward through a comfortable range while keeping the setup stable.",
        safety_notes="Use safe support if needed and stop if pain, dizziness, or unusual symptoms occur.",
        endpoint_path="/api/v1/analyze/hip-abduction",
    ),
)

_PLANNED_IDS = ("heel_raise", "lunge", "step_up", "balance", "walking_gait_screen", "shoulder_flexion", "hip_flexion")
_PLANNED = tuple(
    ExerciseMetadata(
        exercise_id=exercise_id,
        display_name=exercise_id.replace("_", " ").title(),
        supported_in_app=False,
        body_region="Planned",
        exercise_family="Planned exercise",
        recommended_camera_view="To be validated",
        required_landmarks=[],
        movement_description="Planned exercise coverage; no working analyzer is available yet.",
        expected_movement_pattern="Not available for analysis.",
        safety_notes="Do not use PhysioVision AI to analyze this exercise yet.",
        endpoint_path=None,
        ml_model_status="not_applicable",
        recognition_status="planned_not_available",
    )
    for exercise_id in _PLANNED_IDS
)

EXERCISE_METADATA = _SUPPORTED + _PLANNED
EXERCISE_METADATA_BY_ID = {item.exercise_id: item for item in EXERCISE_METADATA}


def list_exercise_metadata() -> tuple[ExerciseMetadata, ...]:
    return EXERCISE_METADATA


def get_exercise_metadata(exercise_id: str) -> ExerciseMetadata | None:
    return EXERCISE_METADATA_BY_ID.get(exercise_id)
