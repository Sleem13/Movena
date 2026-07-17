from app.datasets.adapters.squat_kaggle_adapter import SquatKaggleAdapter


def test_squat_kaggle_detects_tabular_features_but_requires_review(tmp_path):
    (tmp_path / "features.csv").write_text("label,x\ncorrect,1\n", encoding="utf-8")
    row = SquatKaggleAdapter(tmp_path).export_unified_metadata()[0]
    assert row["modality"] == "tabular_features"
    assert row["exercise_id"] == "bodyweight_squat"
    assert row["requires_manual_review"] is True
    assert SquatKaggleAdapter(tmp_path).is_compatible_with_pipeline("tabular_feature_pipeline")

