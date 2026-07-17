import csv
from pathlib import Path


def test_hip_abduction_is_supported_without_ml():
    rows = list(csv.DictReader(Path("data/processed/registry/exercise_taxonomy.csv").open(encoding="utf-8")))
    hip = next(row for row in rows if row["exercise_id"] == "hip_abduction")
    assert hip["supported_in_app"] == "True"
    assert hip["rule_based_analyzer_status"] == "implemented"
    assert hip["ml_model_status"] == "not_available"
    assert hip["recommended_camera_view"] == "front_view"
    assert hip["implementation_status"] == "implemented_mvp"
