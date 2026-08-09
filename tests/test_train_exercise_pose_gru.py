import numpy as np
import pandas as pd

from scripts.train_exercise_pose_gru import (
    build_video_sequences,
    calibrated_probabilities,
    expected_calibration_error,
    fit_temperature,
    select_confidence_threshold,
    stratified_video_split,
    train_candidate,
)


def test_temperature_calibration_and_threshold_are_evidence_derived():
    logits = np.asarray([[8.0, 0.0], [0.0, 8.0], [7.0, 0.0], [0.0, 7.0]])
    targets = np.asarray([0, 1, 1, 1])
    temperature = fit_temperature(logits, targets)
    probabilities = calibrated_probabilities(logits, temperature)
    evidence = select_confidence_threshold(
        probabilities, targets, target_precision=0.6, minimum_coverage=0.5
    )
    assert temperature > 1.0
    assert np.allclose(probabilities.sum(axis=1), 1.0)
    assert 0.0 <= expected_calibration_error(probabilities, targets) <= 1.0
    assert evidence["coverage"] >= 0.5
    assert evidence["selective_accuracy"] >= 0.6


def prepared_rows(classes=5, videos_per_class=5, frames_per_video=3):
    rows = []
    for class_index in range(classes):
        label = f"exercise_{class_index}"
        for video_index in range(videos_per_class):
            for frame_index in range(frames_per_video):
                rows.append({
                    "sample_id": f"{label}-{video_index}:{frame_index}",
                    "exercise_id": label,
                    "group_id": f"{label}-{video_index}",
                    "feature_status": "available_features",
                    **{f"f{feature_index}": float(class_index + frame_index + feature_index / 100)
                       for feature_index in range(40)},
                })
    return pd.DataFrame(rows)


def test_video_sequences_are_one_sample_per_group_and_resampled():
    data = prepared_rows(classes=2, videos_per_class=5)
    columns = [f"f{index}" for index in range(40)]
    sequences, labels, groups = build_video_sequences(data, columns, sequence_length=8)
    assert sequences.shape == (10, 8, 40)
    assert len(labels) == len(groups) == 10
    assert np.isfinite(sequences).all()


def test_stratified_video_split_is_disjoint_and_preserves_classes():
    labels = np.repeat(["a", "b", "c", "d", "e"], 10)
    split = stratified_video_split(labels)
    assert not set(split["train"]) & set(split["validation"])
    assert not set(split["train"]) & set(split["holdout"])
    assert not set(split["validation"]) & set(split["holdout"])
    assert set(np.concatenate(list(split.values()))) == set(range(len(labels)))
    for indexes in split.values():
        assert set(labels[indexes]) == {"a", "b", "c", "d", "e"}


def test_gru_dry_run_validates_real_sequence_table_without_writing(tmp_path):
    source = tmp_path / "features.csv"
    prepared_rows().to_csv(source, index=False)
    result = train_candidate(source, tmp_path / "models", dry_run=True)
    assert result["valid"] is True
    assert result["trained"] is False
    assert result["status"] == "candidate"
    assert result["video_sequences"] == 25
    assert result["split_video_counts"] == {"train": 15, "validation": 5, "holdout": 5}
    assert not (tmp_path / "models").exists()
