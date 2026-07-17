import pandas as pd

from scripts.build_exercise_recognition_dataset import build_recognition_dataset


def _build(tmp_path, rows, include_low=False):
    pd.DataFrame(rows).to_csv(tmp_path / "samples.csv", index=False)
    pd.DataFrame([
        {"exercise_id": "bodyweight_squat"}, {"exercise_id": "sit_to_stand"}, {"exercise_id": "unknown"}
    ]).to_csv(tmp_path / "taxonomy.csv", index=False)
    return build_recognition_dataset(
        tmp_path / "samples.csv", tmp_path / "taxonomy.csv", tmp_path / "out.csv", tmp_path / "report.md",
        include_low_confidence=include_low, min_samples_per_class=1, dry_run=True,
    )


def test_dataset_builder_excludes_unknown_exercise(tmp_path):
    result = _build(tmp_path, [{
        "sample_id": "x", "dataset_name": "d", "file_path": "x.mp4", "modality": "video",
        "exercise_id": "unknown", "raw_label": "e1", "normalized_label": "unknown",
        "participant_id": "p1", "split": "train", "label_quality": "high",
        "requires_manual_review": False, "processing_status": "ready",
    }])
    assert not bool(result.iloc[0].training_ready)
    assert "unknown_exercise_id" in result.iloc[0].reason_excluded


def test_dataset_builder_excludes_low_confidence_by_default(tmp_path):
    result = _build(tmp_path, [{
        "sample_id": "x", "dataset_name": "d", "file_path": "x.mp4", "modality": "video",
        "exercise_id": "bodyweight_squat", "raw_label": "squat", "normalized_label": "bodyweight_squat",
        "participant_id": "p1", "split": "train", "label_quality": "low",
        "requires_manual_review": False, "processing_status": "ready",
    }])
    assert not bool(result.iloc[0].training_ready)
    assert "low_confidence_label" in result.iloc[0].reason_excluded

