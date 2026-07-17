import pandas as pd

from scripts.build_training_readiness_report import build_training_readiness_report


def test_unknown_labels_are_never_training_ready(tmp_path):
    samples = pd.DataFrame([{
        "exercise_id": "unknown", "dataset_name": "source", "modality": "sensor_timeseries",
        "requires_manual_review": True, "processing_status": "needs_manual_mapping",
        "label_quality": "low", "participant_id": "p1", "split": "train",
    }])
    samples.to_csv(tmp_path / "samples.csv", index=False)
    pd.DataFrame([{"dataset_name": "source"}]).to_csv(tmp_path / "registry.csv", index=False)
    pd.DataFrame([{"exercise_id": "unknown"}]).to_csv(tmp_path / "taxonomy.csv", index=False)
    result = build_training_readiness_report(
        tmp_path / "samples.csv", tmp_path / "registry.csv", tmp_path / "taxonomy.csv",
        tmp_path / "out.csv", tmp_path / "out.md",
    )
    row = result.iloc[0]
    assert not bool(row.can_train_sensor_model)
    assert "unknown_or_unreviewed_labels" in row.blockers

