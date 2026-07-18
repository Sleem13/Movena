from app.exercises.metadata import list_exercise_metadata
from app.exercises.registry import registry


def test_product_metadata_and_analyzer_registry_agree():
    supported = {item.exercise_id for item in list_exercise_metadata() if item.supported_in_app}
    assert supported == set(registry.available_exercises())


def test_unsupported_exercises_have_no_endpoint():
    assert all(
        item.endpoint_path is None
        for item in list_exercise_metadata()
        if not item.supported_in_app
    )
