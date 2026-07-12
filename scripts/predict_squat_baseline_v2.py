"""Run offline inference using the Sprint 7 candidate baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from predict_squat_baseline import predict_rows


DEFAULT_MODEL = Path("models/squat_baseline_v2/artifacts/squat_quality_baseline_v2.pkl")
DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features_v2.csv")


def predict_rows_v2(model_path: Path, input_path: Path, video_path: str | None = None):
    results = predict_rows(model_path, input_path, video_path)
    for result in results:
        result["model_version"] = "sprint_7_baseline_v2"
        result["warning"] = "Experimental baseline model. Not clinically validated."
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
        result = predict_rows_v2(args.model, args.input, args.video_path)
    except Exception as exc:
        print(f"Baseline v2 prediction failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
