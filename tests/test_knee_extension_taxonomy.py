import csv
from pathlib import Path


def test_knee_extension_is_supported_without_ml_model():
    rows = list(csv.DictReader(Path("data/processed/registry/exercise_taxonomy.csv").open(encoding="utf-8")))
    knee = next(row for row in rows if row["exercise_id"] == "knee_extension")
    assert knee["supported_in_app"] == "True"
    assert knee["rule_based_analyzer_status"] == "implemented"
    assert knee["ml_model_status"] == "not_available"
    assert knee["recommended_camera_view"] == "side_view"
    assert knee["implementation_status"] == "implemented_mvp"
    assert "clinical" not in knee["safety_notes"].lower()
