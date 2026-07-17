import pandas as pd

from scripts.build_exercise_recognition_features import build_recognition_features


def test_feature_builder_marks_missing_features_without_crashing(tmp_path, monkeypatch):
    samples = pd.DataFrame([{
        "sample_id": "x", "dataset_name": "d", "exercise_id": "bodyweight_squat",
        "recognition_track": "skeleton_sequence_recognition", "participant_id": "p1",
        "split": "train", "file_path": "missing.npy",
    }])
    samples.to_csv(tmp_path / "samples.csv", index=False)
    result = build_recognition_features(
        tmp_path / "samples.csv", tmp_path / "features.csv", tmp_path / "report.md", dry_run=True
    )
    assert result.iloc[0].feature_status == "missing_features"

