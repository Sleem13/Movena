import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from train_squat_baseline_v2 import train_baselines_v2


def dummy_v2(path):
    rows = []
    for label_index, label in enumerate(["squat_correct", "squat_knee_valgus", "squat_trunk_lean"]):
        for index in range(2):
            rows.append({"video_path": f"{label}-{index}.mp4", "label": label, "split": "development_unassigned", "source_dataset": "dummy", "source_type": "real", "original_label": label, "augmented_label": "", "f1": label_index * 10 + index, "f2": label_index * 5 + index})
        rows.append({"video_path": f"{label}-test.mp4", "label": label, "split": "holdout_test", "source_dataset": "dummy", "source_type": "real", "original_label": label, "augmented_label": "", "f1": label_index * 10 + .5, "f2": label_index * 5 + .5})
    pd.DataFrame(rows).to_csv(path, index=False)


def test_v2_training_saves_models_metrics_and_comparison(tmp_path):
    data = tmp_path / "v2.csv"
    dummy_v2(data)
    old_metrics = tmp_path / "old.json"
    old_metrics.write_text(json.dumps({"best_model": "svc_rbf", "dataset_rows": 6, "saved_model_evaluation": {"accuracy": .5, "macro_f1": .4, "weighted_f1": .4}}))
    model_dir = tmp_path / "models"

    metrics, comparison = train_baselines_v2(data, model_dir, old_metrics)

    assert set(metrics["models"]) == {"logistic_regression", "random_forest", "svc_rbf"}
    assert (model_dir / "artifacts/squat_quality_baseline_v2.pkl").exists()
    assert (model_dir / "metrics.json").exists()
    assert (model_dir / "comparison_to_sprint5.json").exists()
    assert comparison["sprint7_dataset_rows"] == 9
    assert comparison["accuracy"]["delta"] is not None
