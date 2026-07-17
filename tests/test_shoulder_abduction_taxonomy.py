import csv
from pathlib import Path


def test_shoulder_abduction_is_supported_without_ml():
    rows = list(csv.DictReader(Path("data/processed/registry/exercise_taxonomy.csv").open(encoding="utf-8")))
    shoulder = next(row for row in rows if row["exercise_id"] == "shoulder_abduction")
    assert shoulder["supported_in_app"] == "True"
    assert shoulder["rule_based_analyzer_status"] == "implemented"
    assert shoulder["ml_model_status"] == "not_available"
    assert shoulder["recommended_camera_view"] == "front_view"
