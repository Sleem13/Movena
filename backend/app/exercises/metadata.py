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

_COACHING_CANDIDATES = (
    ExerciseMetadata(
        exercise_id="push_up", display_name="Push-Up", supported_in_app=True,
        body_region="Upper body and trunk", exercise_family="Closed-chain upper-body movement",
        recommended_camera_view="Side view preferred", required_landmarks=["shoulders", "elbows", "wrists", "hips", "ankles"],
        movement_description="A controlled push-up through a comfortable range with the trunk supported as one unit.",
        expected_movement_pattern="From a visible side-view support position, bend and extend the elbows with the body supported as one unit.",
        safety_notes="Use an appropriate supported variation and stop if pain, dizziness, numbness, or unusual symptoms occur.", endpoint_path="/api/v1/analyze/push-up",
        ml_model_status="not_applicable_rule_based_primary", recognition_status="experimental_suggestion_only_analyzer_available",
    ),
    ExerciseMetadata(
        exercise_id="shoulder_press", display_name="Shoulder Press", supported_in_app=True,
        body_region="Shoulder, upper limb, and trunk", exercise_family="Overhead press",
        recommended_camera_view="Front or slight diagonal view", required_landmarks=["shoulders", "elbows", "wrists", "hips"],
        movement_description="An overhead pressing movement distinct from shoulder abduction.",
        expected_movement_pattern="Begin with flexed elbows visible, extend overhead, then return with control.",
        safety_notes="Use only a clinician-approved load or unloaded practice; stop if pain, numbness, dizziness, or unusual symptoms occur.", endpoint_path="/api/v1/analyze/shoulder-press",
        ml_model_status="not_applicable_rule_based_primary", recognition_status="experimental_suggestion_only_analyzer_available",
    ),
    ExerciseMetadata(
        exercise_id="bicep_curl", display_name="Bicep Curl", supported_in_app=True,
        body_region="Elbow and upper limb", exercise_family="Elbow flexion",
        recommended_camera_view="Front or slight side view", required_landmarks=["shoulders", "elbows", "wrists", "hips"],
        movement_description="A controlled elbow-flexion movement observed with conservative upper-arm and trunk rules.",
        expected_movement_pattern="Begin with the elbow extended, flex through a comfortable visible range, then return with control.",
        safety_notes="Use only a clinician-approved load or unloaded practice; the analyzer cannot assess grip or safe load.", endpoint_path="/api/v1/analyze/bicep-curl",
        ml_model_status="not_applicable_rule_based_primary", recognition_status="experimental_suggestion_only_analyzer_available",
    ),
    ExerciseMetadata(
        exercise_id="hammer_curl", display_name="Hammer Curl", supported_in_app=False,
        body_region="Elbow, forearm, and upper limb", exercise_family="Neutral-grip elbow flexion",
        recommended_camera_view="Front or slight side view", required_landmarks=["shoulders", "elbows", "wrists", "hands", "hips"],
        movement_description="A neutral-grip curl candidate that requires hand-orientation evidence.",
        expected_movement_pattern="Research candidate only; the current body-pose contract cannot verify grip orientation.",
        safety_notes="Do not use PhysioVision AI to distinguish or assess hammer curls yet.", endpoint_path=None,
        ml_model_status="experimental_recognition_research_only", recognition_status="experimental_candidate_data_available",
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

EXERCISE_METADATA = _SUPPORTED + _COACHING_CANDIDATES + _PLANNED
EXERCISE_METADATA_BY_ID = {item.exercise_id: item for item in EXERCISE_METADATA}


def list_exercise_metadata() -> tuple[ExerciseMetadata, ...]:
    return EXERCISE_METADATA


def get_exercise_metadata(exercise_id: str) -> ExerciseMetadata | None:
    return EXERCISE_METADATA_BY_ID.get(exercise_id)
