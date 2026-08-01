import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_zenodo_distribution_shift import analyze_distribution_shift
from test_train_zenodo_squat_baseline import write_training_files


def test_distribution_shift_exports_drift_and_balanced_error_review(tmp_path):
    features, metadata = write_training_files(tmp_path)
    metadata_frame = pd.read_csv(metadata)
    metadata_frame["source_split"] = metadata_frame["image_path"].map(
        lambda value: "test" if "test" in Path(value).parts else "train"
    )
    metadata_frame.to_csv(metadata, index=False)
    test_rows = pd.read_csv(features)
    test_rows = test_rows[test_rows["image_path"].map(lambda value: "test" in Path(value).parts)]
    prediction_rows = []
    for index, row in enumerate(test_rows.itertuples(index=False)):
        predicted = "good" if row.label != "good" else "bad_heel"
        prediction_rows.append(
            {
                "image_path": row.image_path,
                "actual_label": row.label,
                "predicted_label": predicted,
                "confidence": 0.99 - index * 0.01,
                "is_error": True,
                "error_pair": f"{row.label} -> {predicted}",
            }
        )
    predictions = tmp_path / "predictions.csv"
    pd.DataFrame(prediction_rows).to_csv(predictions, index=False)

    drift, review, summary = analyze_distribution_shift(
        features,
        metadata,
        predictions,
        tmp_path / "drift.csv",
        tmp_path / "report.md",
        tmp_path / "review.csv",
        None,
        samples_per_pair=1,
    )

    assert not drift.empty
    assert set(drift["scope"]) >= {"overall", "label:good", "label:bad_back", "label:bad_heel"}
    assert len(review) == review["error_pair"].nunique()
    assert summary["prepared_images"] == 18
    assert summary["detected_images"] == 18
    assert summary["promotion_supported"] is False
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "Pose Detection Coverage" in report
    assert "Largest Overall Feature Shifts" in report
