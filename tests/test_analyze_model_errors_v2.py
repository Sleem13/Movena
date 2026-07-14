import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_model_errors_v2 import analyze_model_errors
from create_manual_annotation_template import ANNOTATION_COLUMNS


def test_model_error_analysis_groups_false_results_and_metadata(tmp_path):
    features = tmp_path / "features.csv"
    annotations = tmp_path / "annotations.csv"
    pd.DataFrame([
        {"video_path": "a.mp4", "label": "squat_correct", "split": "holdout_test", "source_type": "real", "f1": 1},
        {"video_path": "b.mp4", "label": "squat_knee_valgus", "split": "holdout_test", "source_type": "real", "f1": 2},
        {"video_path": "c.mp4", "label": "squat_correct", "split": "train", "source_type": "real", "f1": 3},
    ]).to_csv(features, index=False)
    rows = []
    for path, view, quality in [("a.mp4", "side", "good"), ("b.mp4", "front", "fair")]:
        row = {column: "" for column in ANNOTATION_COLUMNS}
        row.update({"video_path": path, "view_type": view, "recording_quality": quality})
        rows.append(row)
    pd.DataFrame(rows).to_csv(annotations, index=False)

    def predictor(_model, _features, _video):
        return [
            {"video_path": "a.mp4", "predicted_label": "squat_correct", "confidence": 0.8},
            {"video_path": "b.mp4", "predicted_label": "squat_correct", "confidence": 0.6},
            {"video_path": "c.mp4", "predicted_label": "squat_correct", "confidence": 0.9},
        ]

    result, summary = analyze_model_errors(
        features, tmp_path / "model.pkl", annotations,
        tmp_path / "errors.csv", tmp_path / "errors.md", predictor,
    )

    assert len(result) == 2
    assert summary["error_rows"] == 1
    assert summary["false_negatives_by_class"] == {"squat_knee_valgus": 1}
    assert summary["false_positives_by_class"] == {"squat_correct": 1}
    assert summary["errors_by_view"] == {"front": 1}
    assert "remains experimental" in (tmp_path / "errors.md").read_text(encoding="utf-8")
