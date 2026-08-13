import csv
from pathlib import Path


def test_shoulder_abduction_supports_optional_ml_second_opinion():
    rows = list(csv.DictReader(Path("data/processed/registry/exercise_taxonomy.csv").open(encoding="utf-8")))
    shoulder = next(row for row in rows if row["exercise_id"] == "shoulder_abduction")
    assert shoulder["supported_in_app"] == "True"
    assert shoulder["rule_based_analyzer_status"] == "implemented"
    assert shoulder["ml_model_status"] == "optional_experimental_second_opinion"
    assert shoulder["recommended_camera_view"] == "front_view"
