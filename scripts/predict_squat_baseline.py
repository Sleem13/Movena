"""Run experimental inference using the saved video-level squat baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd


DEFAULT_MODEL = Path("models/squat_baseline/artifacts/squat_quality_baseline.pkl")
DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features.csv")


def predict_rows(
    model_path: Path,
    input_path: Path,
    video_path: str | None = None,
) -> list[dict[str, object]]:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Baseline model not found: {model_path}. Run train_squat_baseline.py first."
        )
    if not input_path.exists():
        raise FileNotFoundError(f"Feature CSV not found: {input_path}")
    bundle = joblib.load(model_path)
    data = pd.read_csv(input_path)
    if video_path:
        normalized = video_path.replace("\\", "/")
        data = data[data["video_path"].astype(str).str.replace("\\", "/", regex=False) == normalized]
    if data.empty:
        raise ValueError("No feature rows matched the prediction request.")
    features = bundle["feature_columns"]
    missing = set(features).difference(data.columns)
    if missing:
        raise ValueError(f"Feature CSV is missing columns: {', '.join(sorted(missing))}")
    model = bundle["model"]
    predictions = model.predict(data[features])
    probabilities = model.predict_proba(data[features]) if hasattr(model, "predict_proba") else None
    results = []
    for index, (_, row) in enumerate(data.iterrows()):
        confidence = float(probabilities[index].max()) if probabilities is not None else None
        results.append(
            {
                "video_path": str(row.get("video_path", "")),
                "predicted_label": str(predictions[index]),
                "confidence": confidence,
                "model_name": bundle["model_name"],
                "model_version": bundle["model_version"],
                "warning": bundle.get(
                    "warning", "Experimental baseline model. Not clinically validated."
                ),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--video-path", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        results = predict_rows(args.model, args.input, args.video_path)
    except Exception as exc:
        print(f"Baseline prediction failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
