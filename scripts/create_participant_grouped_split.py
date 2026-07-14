"""Create a deterministic participant-grouped squat dataset split and audit report."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

try:
    from .create_manual_annotation_template import normalize_path
    from .validate_manual_rep_annotations import PARTICIPANT_ID_PATTERN
except ImportError:  # Direct CLI execution from scripts/.
    from create_manual_annotation_template import normalize_path
    from validate_manual_rep_annotations import PARTICIPANT_ID_PATTERN


DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_METADATA = Path("data/processed/labels/participant_metadata.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/participant_grouped_split.csv")
DEFAULT_REPORT = Path("reports/participant_split/participant_grouped_split_report.md")
OUTPUT_COLUMNS = [
    "video_path", "dataset_source", "participant_id", "session_id", "exercise_label",
    "split", "source_type", "split_reason",
]
SPLITS = ("train", "validation", "holdout_test")
TARGET_FRACTIONS = {"train": 0.70, "validation": 0.15, "holdout_test": 0.15}


def _source_type(path: str, dataset_source: str = "") -> str:
    value = f"{normalize_path(path)} {dataset_source}".lower()
    return "augmented" if "augmented" in value else "real"


def _assign_participants(data: pd.DataFrame) -> dict[str, str]:
    groups = {participant: group for participant, group in data.groupby("participant_id", sort=True)}
    total_rows = len(data)
    total_classes = Counter(data["exercise_label"])
    total_sources = Counter(data["dataset_source"])
    assigned_rows = Counter()
    assigned_classes: dict[str, Counter[str]] = defaultdict(Counter)
    assigned_sources: dict[str, Counter[str]] = defaultdict(Counter)
    assignments: dict[str, str] = {}

    def rarity(item: tuple[str, pd.DataFrame]) -> tuple[float, int, str]:
        participant, group = item
        score = sum(1 / max(1, total_classes[label]) for label in group["exercise_label"])
        return (-score, -len(group), participant)

    for participant, group in sorted(groups.items(), key=rarity):
        group_classes = Counter(group["exercise_label"])
        group_sources = Counter(group["dataset_source"])
        scores: dict[str, float] = {}
        for split in SPLITS:
            target_rows = max(1.0, total_rows * TARGET_FRACTIONS[split])
            row_fill = (assigned_rows[split] + len(group)) / target_rows
            class_fill = sum(
                (assigned_classes[split][label] + count)
                / max(1.0, total_classes[label] * TARGET_FRACTIONS[split])
                for label, count in group_classes.items()
            ) / max(1, len(group_classes))
            source_fill = sum(
                (assigned_sources[split][source] + count)
                / max(1.0, total_sources[source] * TARGET_FRACTIONS[split])
                for source, count in group_sources.items()
            ) / max(1, len(group_sources))
            scores[split] = 0.35 * row_fill + 0.45 * class_fill + 0.20 * source_fill
        selected = min(SPLITS, key=lambda split: (scores[split], SPLITS.index(split)))
        assignments[participant] = selected
        assigned_rows[selected] += len(group)
        assigned_classes[selected].update(group_classes)
        assigned_sources[selected].update(group_sources)
    return assignments


def _distribution_table(data: pd.DataFrame, field: str) -> list[str]:
    if data.empty:
        return ["- No assigned rows."]
    table = pd.crosstab(data["split"], data[field])
    return ["```", table.to_string(), "```"]


def create_grouped_split(
    annotations_path: Path,
    output_path: Path,
    metadata_path: Path | None = None,
    report_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not annotations_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotations_path}")
    data = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
    required = {"video_path", "participant_id", "session_id", "exercise_label"}
    if missing := required.difference(data.columns):
        raise ValueError("Annotation file is missing: " + ", ".join(sorted(missing)))
    data = data.copy()
    data["dataset_source"] = data.get("dataset_source", pd.Series("unknown", index=data.index)).replace("", "unknown")
    data["video_path"] = data["video_path"].map(normalize_path)
    data["participant_id"] = data["participant_id"].str.strip()

    metadata_ids: set[str] = set()
    if metadata_path and metadata_path.exists() and metadata_path.stat().st_size:
        metadata = pd.read_csv(metadata_path, dtype=str, keep_default_na=False)
        if "participant_id" not in metadata.columns:
            raise ValueError("Participant metadata is missing: participant_id")
        metadata_ids = {value.strip() for value in metadata["participant_id"] if value.strip()}

    valid_participant = data["participant_id"].map(lambda value: bool(PARTICIPANT_ID_PATTERN.fullmatch(value)))
    valid_label = data["exercise_label"].str.strip().ne("") & data["exercise_label"].ne("unlabeled")
    eligible = data[valid_participant & valid_label].copy()
    assignments = _assign_participants(eligible) if not eligible.empty else {}

    rows = []
    warnings: list[str] = []
    for row in data.itertuples(index=False):
        participant = row.participant_id.strip()
        label = row.exercise_label.strip()
        if not PARTICIPANT_ID_PATTERN.fullmatch(participant):
            split, reason = "unassigned", "missing_or_invalid_participant_id"
        elif not label or label == "unlabeled":
            split, reason = "excluded", "missing_or_unsupported_label"
        else:
            split, reason = assignments[participant], "participant_grouped"
            if metadata_path is not None and participant not in metadata_ids:
                reason += ";participant_metadata_missing"
        source = str(row.dataset_source).strip() or "unknown"
        rows.append({
            "video_path": normalize_path(row.video_path), "dataset_source": source,
            "participant_id": participant, "session_id": row.session_id.strip(),
            "exercise_label": label, "split": split,
            "source_type": _source_type(row.video_path, source), "split_reason": reason,
        })
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    assigned = result[result["split"].isin(SPLITS)]
    leakage = bool(assigned.groupby("participant_id")["split"].nunique().gt(1).any())
    participant_count = int(assigned["participant_id"].nunique())
    holdout_participants = int(assigned[assigned["split"] == "holdout_test"]["participant_id"].nunique())
    if participant_count < 7:
        warnings.append("Too few reviewed participants for a reliable 70/15/15 grouped split.")
    if holdout_participants < 5:
        warnings.append("Holdout has fewer than five participants and cannot support model promotion.")
    if int((result["split"] == "unassigned").sum()):
        warnings.append("Rows with missing or invalid participant IDs remain unassigned for review.")
    is_ready = bool(assignments and not leakage and all(split in assigned["split"].values for split in SPLITS))
    promotion_valid = bool(is_ready and holdout_participants >= 5)
    summary: dict[str, object] = {
        "total_rows": len(result), "assigned_rows": len(assigned),
        "unassigned_rows": int((result["split"] == "unassigned").sum()),
        "excluded_rows": int((result["split"] == "excluded").sum()),
        "assigned_participants": participant_count,
        "holdout_participants": holdout_participants,
        "split_distribution": result["split"].value_counts().to_dict(),
        "participant_leakage": leakage, "warnings": warnings, "is_ready": is_ready,
        "promotion_valid": promotion_valid,
    }

    if report_path is not None:
        participants_per_split = assigned.groupby("split")["participant_id"].nunique().to_dict()
        lines = [
            "# Participant-Grouped Split Report", "",
            "This split is for engineering evaluation and is not clinical validation.", "",
            "## Summary", "",
            f"- Total videos: {len(result)}", f"- Assigned videos: {len(assigned)}",
            f"- Assigned participants: {participant_count}",
            f"- Participant leakage detected: {str(leakage).lower()}",
            f"- Structurally valid grouped split: {str(is_ready).lower()}",
            f"- Valid for model promotion: {str(promotion_valid).lower()}", "",
            "## Participants per Split", "",
            *[f"- `{split}`: {participants_per_split.get(split, 0)}" for split in SPLITS], "",
            "## Videos per Split", "",
            *[f"- `{key}`: {value}" for key, value in sorted(summary["split_distribution"].items())], "",
            "## Class Distribution per Split", "", *_distribution_table(assigned, "exercise_label"), "",
            "## Dataset Distribution per Split", "", *_distribution_table(assigned, "dataset_source"), "",
            "## Warnings", "", *([f"- {warning}" for warning in warnings] or ["- None"]), "",
        ]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
    return result, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, summary = create_grouped_split(args.annotations, args.output, args.metadata, args.report)
    except Exception as exc:
        print(f"Participant-grouped split creation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Participant-grouped split: {args.output}")
    print(f"Split report: {args.report}")
    print(f"Assigned rows: {summary['assigned_rows']}/{summary['total_rows']}")
    if not summary["is_ready"]:
        print("WARNING: A promotion-grade participant-grouped holdout is not yet established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
