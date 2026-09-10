from app.exercises.metadata import list_exercise_metadata, get_exercise_metadata
from app.exercises.registry import registry
from app.schemas.patient_schema import ExercisePlanItemCreate


def test_guides_are_unique_complete_and_not_misrepresented_as_analyzers():
    items = list_exercise_metadata()
    assert len({item.exercise_id for item in items}) == len(items)
    guides = [item for item in items if item.guidance_available]
    assert {item.exercise_id for item in guides} == {
        "heel_raise", "lunge", "step_up", "hip_flexion", "ankle_pumps",
        "heel_slide", "quad_set", "straight_leg_raise", "glute_bridge",
    }
    for guide in guides:
        assert not guide.supported_in_app
        assert guide.endpoint_path is None
        assert guide.exercise_id not in registry.available_exercises()
        assert len(guide.instructions) >= 2
        assert guide.safety_notes and guide.dosage_guidance
        assert guide.source_urls and all(url.startswith("https://") for url in guide.source_urls)
        assert guide.localized_ar["instructions"] and guide.localized_ar["safety_notes"]


def test_guided_exercises_can_be_assigned_without_an_analysis_requirement():
    for exercise in list_exercise_metadata():
        if not exercise.guidance_available:
            continue
        item = ExercisePlanItemCreate(
            exercise_id=exercise.exercise_id, sets=1, reps=5, days_per_week=3,
            instructions=" ".join(exercise.instructions), precautions=exercise.safety_notes,
        )
        assert not item.requires_ai_analysis
        assert get_exercise_metadata(item.exercise_id).guidance_available


def test_existing_analyzers_include_bilingual_instructions_and_references():
    supported = [item for item in list_exercise_metadata() if item.supported_in_app]
    assert len(supported) == 12
    for item in supported:
        assert item.endpoint_path and item.exercise_id in registry.available_exercises()
        assert len(item.instructions) == 3
        assert len(item.localized_ar["instructions"]) == 3
        assert item.dosage_guidance and item.localized_ar["dosage_guidance"]
        assert item.reference_note and item.source_urls
        assert all(url.startswith("https://") for url in item.source_urls)
