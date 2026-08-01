"""Run offline inference with the experimental Zenodo posture baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd


DEFAULT_MODEL = Path(
    "models/zenodo_squat_baseline/artifacts/zenodo_squat_posture_baseline.pkl"
)
DEFAULT_INPUT = Path(
    "data/processed/angle_features/zenodo_squat_dataset/zenodo_squat_angle_features.csv"
)


def predict_rows(
    model_path: Path,
    input_path: Path,
    image_path: str | None = None,
) -> list[dict[str, object]]:
    if not model_path.exists():
        raise FileNotFoundError(f"Zenodo posture model not found: {model_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Zenodo posture features not found: {input_path}")
    bundle = joblib.load(model_path)
    required_bundle = {"model", "model_name", "model_version", "feature_columns"}
    if missing := required_bundle.difference(bundle):
        raise ValueError("Model artifact is missing: " + ", ".join(sorted(missing)))

    data = pd.read_csv(input_path)
    if "image_path" not in data:
        raise ValueError("Feature CSV is missing image_path.")
    feature_columns = list(bundle["feature_columns"])
    if missing := set(feature_columns).difference(data.columns):
        raise ValueError("Feature CSV is missing model features: " + ", ".join(sorted(missing)))
    if image_path is not None:
        data = data[data["image_path"].astype(str).eq(str(image_path))].copy()
        if data.empty:
            raise ValueError(f"Image was not found in the feature CSV: {image_path}")
    if data.empty:
        return []

    model = bundle["model"]
    predicted = model.predict(data[feature_columns])
    probabilities = model.predict_proba(data[feature_columns]) if hasattr(model, "predict_proba") else None
    classes = list(getattr(model, "classes_", []))
    results: list[dict[str, object]] = []
    for position, (_, row) in enumerate(data.iterrows()):
        predicted_label = str(predicted[position])
        class_probabilities: dict[str, float] = {}
        confidence = None
        if probabilities is not None:
            class_probabilities = {
                str(label): float(probability)
                for label, probability in zip(classes, probabilities[position])
            }
            confidence = float(max(class_probabilities.values()))
        results.append(
            {
                "image_path": str(row["image_path"]),
                "actual_label": str(row["label"]) if "label" in row else None,
                "predicted_label": predicted_label,
                "confidence": confidence,
                "class_probabilities": class_probabilities,
                "model_name": str(bundle["model_name"]),
                "model_version": str(bundle["model_version"]),
                "scope": str(bundle.get("scope", "static_squat_posture_research_only")),
                "warning": str(bundle.get("warning", "Experimental model.")),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--image-path", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        results = predict_rows(args.model, args.input, args.image_path)
    except Exception as exc:
        print(f"Zenodo posture prediction failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
