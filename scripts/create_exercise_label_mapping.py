"""Create a conservative starter mapping from observed dataset folder labels."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_RAW_ROOT = Path("data/raw")
DEFAULT_OUTPUT = Path("data/processed/registry/exercise_label_mapping.csv")
REQUIRED_MAPPING_COLUMNS = [
    "dataset_name", "raw_label", "raw_folder_or_code", "inferred_exercise_id",
    "inferred_issue_label", "mapping_confidence", "requires_review", "reviewed_by",
    "review_status", "notes",
]
# Legacy aliases remain temporarily so older research scripts can migrate safely.
LEGACY_COLUMNS = ["raw_dataset_name", "normalized_exercise", "normalized_issue_label", "confidence"]
MAPPING_COLUMNS = REQUIRED_MAPPING_COLUMNS + LEGACY_COLUMNS
ISSUE_MAP = {
    "squat_correct": "squat_correct", "squat_knee_valgus": "squat_knee_valgus",
    "squat_shallow_depth": "squat_shallow_depth", "squat_trunk_lean": "squat_trunk_lean",
    "squat_fast_uncontrolled": "squat_fast_uncontrolled",
    "no_valid_squat_detected": "no_valid_squat_detected",
}
EXERCISE_TOKENS = {
    "bodyweight_squat": "bodyweight_squat", "squat": "bodyweight_squat",
    "sit_to_stand": "sit_to_stand", "walking": "walking_gait_screen", "walk": "walking_gait_screen",
    "knee_extension": "knee_extension", "shoulder_abduction": "shoulder_abduction",
    "balance": "balance",
}
ALIASES = {"Pyhsical-therapy exercises": "Physical-therapy exercises"}


def normalize_token(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.strip().lower())).strip("_")


def infer_mapping(dataset_name: str, raw_label: str) -> dict[str, object]:
    token = normalize_token(raw_label)
    if token in ISSUE_MAP:
        exercise, issue, confidence, notes = "bodyweight_squat", ISSUE_MAP[token], "high", "Exact approved folder-label match."
        review_status = "approved"
        requires_review = False
        return _mapping_result(exercise, issue, confidence, requires_review, review_status, notes)
    for key, exercise in EXERCISE_TOKENS.items():
        if token == key or token.startswith(key + "_"):
            issue = "not_applicable" if exercise != "bodyweight_squat" else "unknown"
            return _mapping_result(exercise, issue, "medium", True, "pending", "Exercise inferred from a folder token; human review is required.")
    if "squat" in dataset_name.lower() and token in {"good", "bad_back", "bad_heel"}:
        return _mapping_result("bodyweight_squat", "unknown", "low", True, "needs_more_info", "Squat context is clear, but the issue label requires source-document review.")
    return _mapping_result("unknown", "unknown", "low", True, "needs_more_info", "Uncertain folder/code; dataset documentation and manual mapping are required.")


def _mapping_result(exercise: str, issue: str, confidence: str, requires_review: bool, review_status: str, notes: str) -> dict[str, object]:
    return {
        "inferred_exercise_id": exercise,
        "inferred_issue_label": issue,
        "mapping_confidence": confidence,
        "requires_review": requires_review,
        "reviewed_by": "",
        "review_status": review_status,
        "notes": notes,
        # Compatibility aliases.
        "normalized_exercise": exercise,
        "normalized_issue_label": issue,
        "confidence": confidence,
    }


def create_mapping(raw_root: Path, output_path: Path) -> pd.DataFrame:
    rows = []
    if raw_root.exists():
        for dataset_path in sorted(item for item in raw_root.iterdir() if item.is_dir()):
            dataset_name = ALIASES.get(dataset_path.name, dataset_path.name)
            labels = sorted({item.name for item in dataset_path.rglob("*") if item.is_dir()})
            labels = labels or ["dataset_root"]
            for label in labels:
                rows.append({
                    "dataset_name": dataset_name,
                    "raw_dataset_name": dataset_name,
                    "raw_label": label,
                    "raw_folder_or_code": label,
                    **infer_mapping(dataset_name, label),
                })
    result = pd.DataFrame(rows, columns=MAPPING_COLUMNS).drop_duplicates(["dataset_name", "raw_label"])
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
    print(f"Mappings requiring review: {int(data.requires_review.astype(bool).sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
