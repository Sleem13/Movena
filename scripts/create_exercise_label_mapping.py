"""Create a conservative starter mapping from observed dataset folder labels."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_RAW_ROOT = Path("data/raw")
DEFAULT_OUTPUT = Path("data/processed/registry/exercise_label_mapping.csv")
MAPPING_COLUMNS = ["raw_dataset_name", "raw_label", "normalized_exercise", "normalized_issue_label", "confidence", "notes"]
ISSUE_MAP = {
    "squat_correct": "squat_correct", "squat_knee_valgus": "squat_knee_valgus",
    "squat_shallow_depth": "squat_shallow_depth", "squat_trunk_lean": "squat_trunk_lean",
    "squat_fast_uncontrolled": "squat_fast_uncontrolled",
    "no_valid_squat_detected": "no_valid_squat_detected",
}
EXERCISE_TOKENS = {
    "bodyweight_squat": "bodyweight_squat", "squat": "squat",
    "sit_to_stand": "sit_to_stand", "walking": "walking", "walk": "walking",
    "knee_extension": "knee_extension", "shoulder_abduction": "shoulder_abduction",
    "balance": "balance",
}
ALIASES = {"Pyhsical-therapy exercises": "Physical-therapy exercises"}


def normalize_token(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.strip().lower())).strip("_")


def infer_mapping(dataset_name: str, raw_label: str) -> dict[str, str]:
    token = normalize_token(raw_label)
    if token in ISSUE_MAP:
        return {"normalized_exercise": "bodyweight_squat", "normalized_issue_label": ISSUE_MAP[token], "confidence": "high", "notes": "Exact approved folder-label match."}
    for key, exercise in EXERCISE_TOKENS.items():
        if token == key or token.startswith(key + "_"):
            return {"normalized_exercise": exercise, "normalized_issue_label": "not_applicable" if exercise not in {"squat", "bodyweight_squat"} else "unknown", "confidence": "medium", "notes": "Exercise inferred from an explicit folder token; issue meaning remains unverified."}
    if "squat" in dataset_name.lower() and token in {"good", "bad_back", "bad_heel"}:
        return {"normalized_exercise": "squat", "normalized_issue_label": "unknown", "confidence": "low", "notes": "Squat context is clear, but the source label is not mapped to a clinical issue without documentation review."}
    return {"normalized_exercise": "unknown", "normalized_issue_label": "unknown", "confidence": "low", "notes": "Uncertain folder label; dataset-specific documentation and adapter required."}


def create_mapping(raw_root: Path, output_path: Path) -> pd.DataFrame:
    rows = []
    if raw_root.exists():
        for dataset_path in sorted(item for item in raw_root.iterdir() if item.is_dir()):
            dataset_name = ALIASES.get(dataset_path.name, dataset_path.name)
            labels = sorted({item.name for item in dataset_path.rglob("*") if item.is_dir()})
            labels = labels or ["dataset_root"]
            for label in labels:
                rows.append({"raw_dataset_name": dataset_name, "raw_label": label, **infer_mapping(dataset_name, label)})
    result = pd.DataFrame(rows, columns=MAPPING_COLUMNS).drop_duplicates(["raw_dataset_name", "raw_label"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = create_mapping(args.raw_root, args.output)
    print(f"Saved {len(data)} conservative label mappings to {args.output}")
    print(f"Unknown issue mappings: {int((data.normalized_issue_label == 'unknown').sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
