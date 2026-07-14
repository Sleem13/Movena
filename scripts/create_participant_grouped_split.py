"""Create a deterministic participant-grouped squat dataset split."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from create_manual_annotation_template import normalize_path
from validate_manual_rep_annotations import PARTICIPANT_ID_PATTERN


DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/participant_grouped_split.csv")
OUTPUT_COLUMNS = [
    "video_path", "participant_id", "session_id", "exercise_label", "split",
    "source_type", "split_reason",
]
SPLITS = ("train", "validation", "holdout")
TARGET_FRACTIONS = {"train": 0.70, "validation": 0.15, "holdout": 0.15}


def _source_type(path: str) -> str:
    normalized = normalize_path(path).lower()
    return "augmented" if "/augmented/" in f"/{normalized}" else "real"


def _assign_participants(data: pd.DataFrame) -> dict[str, str]:
    groups = {
        participant: group
        for participant, group in data.groupby("participant_id", sort=True)
    }
    total_rows = len(data)
    total_classes = Counter(data["exercise_label"])
    assigned_rows = Counter()
    assigned_classes: dict[str, Counter[str]] = defaultdict(Counter)
    assignments: dict[str, str] = {}

    def rarity(item: tuple[str, pd.DataFrame]) -> tuple[float, int, str]:
        participant, group = item
        score = sum(1 / max(1, total_classes[label]) for label in group["exercise_label"])
        return (-score, -len(group), participant)

    for participant, group in sorted(groups.items(), key=rarity):
        group_classes = Counter(group["exercise_label"])
        scores: dict[str, float] = {}
        for split in SPLITS:
            target_rows = max(1.0, total_rows * TARGET_FRACTIONS[split])
            row_fill = (assigned_rows[split] + len(group)) / target_rows
            class_fills = []
            for label, count in group_classes.items():
                target_class = max(1.0, total_classes[label] * TARGET_FRACTIONS[split])
                class_fills.append((assigned_classes[split][label] + count) / target_class)
            scores[split] = 0.45 * row_fill + 0.55 * (sum(class_fills) / len(class_fills))
        selected = min(SPLITS, key=lambda split: (scores[split], SPLITS.index(split)))
        assignments[participant] = selected
        assigned_rows[selected] += len(group)
        assigned_classes[selected].update(group_classes)
    return assignments


def create_grouped_split(annotations_path: Path, output_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    if not annotations_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotations_path}")
    data = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
    required = {"video_path", "participant_id", "session_id", "exercise_label"}
    if missing := required.difference(data.columns):
        raise ValueError("Annotation file is missing: " + ", ".join(sorted(missing)))
    data = data.copy()
    data["video_path"] = data["video_path"].map(normalize_path)
    data["participant_id"] = data["participant_id"].str.strip()
    valid_participant = data["participant_id"].map(
        lambda value: bool(PARTICIPANT_ID_PATTERN.fullmatch(value))
    )
    valid_label = data["exercise_label"].str.strip().ne("") & data["exercise_label"].ne("unlabeled")
    eligible = data[valid_participant & valid_label].copy()
    assignments = _assign_participants(eligible) if not eligible.empty else {}

    rows = []
    for row in data.itertuples(index=False):
        participant = row.participant_id.strip()
        label = row.exercise_label.strip()
        if not PARTICIPANT_ID_PATTERN.fullmatch(participant):
            split = "unassigned"
            reason = "missing_or_invalid_participant_id"
        elif not label or label == "unlabeled":
            split = "excluded"
            reason = "missing_or_unsupported_label"
        else:
            split = assignments[participant]
            reason = "participant_grouped"
        rows.append({
            "video_path": normalize_path(row.video_path),
            "participant_id": participant,
            "session_id": row.session_id.strip(),
            "exercise_label": label,
            "split": split,
            "source_type": _source_type(row.video_path),
            "split_reason": reason,
        })
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    leakage = (
        result[result["split"].isin(SPLITS)]
        .groupby("participant_id")["split"].nunique()
        .gt(1).any()
    )
    summary = {
        "total_rows": len(result),
        "assigned_rows": int(result["split"].isin(SPLITS).sum()),
        "unassigned_rows": int((result["split"] == "unassigned").sum()),
        "excluded_rows": int((result["split"] == "excluded").sum()),
        "assigned_participants": int(result[result["split"].isin(SPLITS)]["participant_id"].nunique()),
        "split_distribution": result["split"].value_counts().to_dict(),
        "participant_leakage": bool(leakage),
        "is_ready": bool(assignments and not leakage and all(split in result["split"].values for split in SPLITS)),
    }
    return result, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, summary = create_grouped_split(args.annotations, args.output)
    except Exception as exc:
        print(f"Participant-grouped split creation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Participant-grouped split: {args.output}")
    print(f"Assigned rows: {summary['assigned_rows']}/{summary['total_rows']}")
    if not summary["is_ready"]:
        print("WARNING: A valid train/validation/holdout split is not yet established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
