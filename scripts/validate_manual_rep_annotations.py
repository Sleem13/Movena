"""Validate manual squat annotations and write a human-readable readiness report."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from create_manual_annotation_template import ANNOTATION_COLUMNS, normalize_path


DEFAULT_INPUT = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_REPORT = Path("reports/manual_annotations/manual_annotation_validation_report.md")
PARTICIPANT_ID_PATTERN = re.compile(r"^P[A-Za-z0-9_-]{2,31}$")
VALID_VIEWS = {"front", "side", "front_oblique", "side_oblique"}
VALID_QUALITY = {"poor", "fair", "good", "excellent"}
VALID_CONFIDENCE = {"low", "medium", "high"}
SUPPORTED_CLASSES = {
    "squat_correct", "squat_shallow_depth", "squat_knee_valgus",
    "squat_trunk_lean", "squat_fast_uncontrolled",
}


def _markdown_counts(values: Counter[str]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- `{key}`: {count}" for key, count in sorted(values.items())]


def validate_annotations(input_path: Path, report_path: Path) -> dict[str, object]:
    if not input_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {input_path}")
    data = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if missing := set(ANNOTATION_COLUMNS).difference(data.columns):
        raise ValueError("Annotation file is missing: " + ", ".join(sorted(missing)))

    paths = data["video_path"].map(normalize_path)
    duplicate_mask = paths.duplicated(keep=False)
    participant_values = data["participant_id"].str.strip()
    missing_participant = participant_values.eq("")
    invalid_participant = ~missing_participant & ~participant_values.map(
        lambda value: bool(PARTICIPANT_ID_PATTERN.fullmatch(value))
    )

    expected = pd.to_numeric(data["expected_reps"], errors="coerce")
    missing_expected = data["expected_reps"].str.strip().eq("")
    invalid_expected = ~missing_expected & (
        expected.isna() | (expected < 0) | (expected % 1 != 0)
    )
    invalid_view = ~data["view_type"].str.strip().isin(VALID_VIEWS) & data["view_type"].str.strip().ne("")
    invalid_quality = ~data["recording_quality"].str.strip().isin(VALID_QUALITY) & data["recording_quality"].str.strip().ne("")
    invalid_confidence = ~data["annotation_confidence"].str.strip().isin(VALID_CONFIDENCE) & data["annotation_confidence"].str.strip().ne("")

    complete = ~(
        missing_participant
        | invalid_participant
        | missing_expected
        | invalid_expected
        | duplicate_mask
    )
    class_counts = Counter(value for value in data["exercise_label"].str.strip() if value)
    participant_counts = Counter(value for value in participant_values if value)
    missing_classes = sorted(SUPPORTED_CLASSES.difference(class_counts))
    summary: dict[str, object] = {
        "total_rows": int(len(data)),
        "complete_rows": int(complete.sum()),
        "missing_expected_reps": int(missing_expected.sum()),
        "invalid_expected_reps": int(invalid_expected.sum()),
        "missing_participant_ids": int(missing_participant.sum()),
        "invalid_participant_ids": int(invalid_participant.sum()),
        "duplicate_video_rows": int(duplicate_mask.sum()),
        "invalid_view_types": int(invalid_view.sum()),
        "invalid_recording_quality": int(invalid_quality.sum()),
        "invalid_annotation_confidence": int(invalid_confidence.sum()),
        "class_distribution": dict(class_counts),
        "missing_supported_classes": missing_classes,
        "participant_distribution": dict(participant_counts),
        "is_ready": bool(len(data) > 0 and complete.all()),
    }

    status = "READY" if summary["is_ready"] else "INCOMPLETE"
    lines = [
        "# Manual Annotation Validation Report",
        "",
        f"**Status: {status}**",
        "",
        "This report validates annotation completeness and structure. It is not clinical validation.",
        "",
        "## Summary",
        "",
        f"- Total rows: {summary['total_rows']}",
        f"- Structurally complete rows: {summary['complete_rows']}",
        f"- Missing expected reps: {summary['missing_expected_reps']}",
        f"- Invalid expected reps: {summary['invalid_expected_reps']}",
        f"- Missing participant IDs: {summary['missing_participant_ids']}",
        f"- Invalid participant IDs: {summary['invalid_participant_ids']}",
        f"- Rows involved in duplicate video paths: {summary['duplicate_video_rows']}",
        f"- Invalid view types: {summary['invalid_view_types']}",
        f"- Invalid recording-quality values: {summary['invalid_recording_quality']}",
        f"- Invalid annotation-confidence values: {summary['invalid_annotation_confidence']}",
        "",
        "## Class Distribution",
        "",
        *_markdown_counts(class_counts),
        "",
        "## Participant Distribution",
        "",
        *_markdown_counts(participant_counts),
        "",
        "## Missing Supported Classes",
        "",
        *([f"- `{label}`" for label in missing_classes] or ["- None"]),
        "",
        "## Readiness Decision",
        "",
    ]
    if summary["is_ready"]:
        lines.append("Annotations are structurally ready for participant-grouped split generation.")
    else:
        lines.append(
            "Annotations are not ready for reliability claims. Complete manual rep counts and pseudonymous participant IDs, then rerun validation."
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate_annotations(args.input, args.report)
    except Exception as exc:
        print(f"Manual annotation validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validation report: {args.report}")
    print(f"Complete rows: {summary['complete_rows']}/{summary['total_rows']}")
    if not summary["is_ready"]:
        print("WARNING: Manual annotations are incomplete; model promotion remains blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
