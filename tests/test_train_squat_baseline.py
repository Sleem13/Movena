import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from train_squat_baseline import train_baselines


def dummy_training_data(path: Path) -> None:
    rows = []
    for label_index, label in enumerate(["squat_correct", "squat_shallow_depth", "squat_trunk_lean"]):
        for index in range(2):
            rows.append({"video_path": f"{label}-{index}.mp4", "label": label, "split": "development", "source_dataset": "dummy", "feature_a": label_index * 10 + index, "feature_b": label_index * 5 + index})
        rows.append({"video_path": f"{label}-holdout.mp4", "label": label, "split": "holdout_test", "source_dataset": "dummy", "feature_a": label_index * 10 + 0.5, "feature_b": label_index * 5 + 0.5})
    pd.DataFrame(rows).to_csv(path, index=False)


def test_training_saves_three_model_results_and_best_artifact(tmp_path):
    input_path = tmp_path / "features.csv"
    model_dir = tmp_path / "models"
    dummy_training_data(input_path)

    metrics = train_baselines(input_path, model_dir)

    assert set(metrics["models"]) == {"logistic_regression", "random_forest", "svc_rbf"}
    assert metrics["best_model"] in metrics["models"]
    assert (model_dir / "artifacts/squat_quality_baseline.pkl").exists()
    assert len(json.loads((model_dir / "feature_columns.json").read_text())) == 2
    assert set(json.loads((model_dir / "label_mapping.json").read_text())) == {"squat_correct", "squat_shallow_depth", "squat_trunk_lean"}
    assert 0 <= metrics["models"][metrics["best_model"]]["macro_f1"] <= 1
