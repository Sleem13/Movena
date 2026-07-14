"""Validate manual squat annotations without rejecting incomplete work-in-progress."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

try:
    from .create_manual_annotation_template import ANNOTATION_COLUMNS, normalize_path
except ImportError:  # Direct CLI execution from scripts/.
    from create_manual_annotation_template import ANNOTATION_COLUMNS, normalize_path


DEFAULT_INPUT = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_REPORT = Path("reports/manual_annotations/manual_annotation_validation_report.md")
DEFAULT_RESULTS = Path("reports/manual_annotations/manual_annotation_validation_results.csv")
PARTICIPANT_ID_PATTERN = re.compile(r"^P[A-Za-z0-9_-]{2,31}$")
VALID_VIEWS = {"front", "side", "oblique", "unknown"}
VALID_QUALITY = {"high", "medium", "low", "unusable"}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_BODY_REGIONS = {"full_body", "lower_body", "partial_body", "unknown"}
SUPPORTED_CLASSES = {
    "squat_correct", "squat_shallow_depth", "squat_knee_valgus",
    "squat_trunk_lean", "squat_fast_uncontrolled",
}
RESULT_COLUMNS = ["row_number", "video_path", "is_complete", "issue_codes"]


def _counts(values: Counter[str]) -> list[str]:
    return [f"- `{key}`: {count}" for key, count in sorted(values.items())] or ["- None"]


def validate_annotations(
    input_path: Path,
    report_path: Path,
    results_path: Path | None = None,
) -> dict[str, object]:
    if not input_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {input_path}")
    try:
        data = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ValueError(f"Annotation file is unreadable or malformed: {exc}") from exc
    if missing := set(ANNOTATION_COLUMNS).difference(data.columns):
        raise ValueError("Annotation file is missing: " + ", ".join(sorted(missing)))

    paths = data["video_path"].map(normalize_path)
    duplicate = paths.duplicated(keep=False) & paths.ne("")
    participant = data["participant_id"].str.strip()
    session = data["session_id"].str.strip()
    labels = data["exercise_label"].str.strip()
    expected_text = data["expected_reps"].str.strip()
    expected = pd.to_numeric(expected_text, errors="coerce")

    checks = {
        "missing_expected_reps": expected_text.eq(""),
        "invalid_expected_reps": expected_text.ne("") & (expected.isna() | expected.lt(0) | expected.mod(1).ne(0)),
        "missing_participant_id": participant.eq(""),
        "invalid_participant_id": participant.ne("") & ~participant.map(lambda x: bool(PARTICIPANT_ID_PATTERN.fullmatch(x))),
        "missing_session_id": session.eq(""),
        "duplicate_video_path": duplicate,
        "invalid_view_type": ~data["view_type"].str.strip().isin(VALID_VIEWS),
        "invalid_recording_quality": ~data["recording_quality"].str.strip().isin(VALID_QUALITY),
        "invalid_annotation_confidence": ~data["annotation_confidence"].str.strip().isin(VALID_CONFIDENCE),
        "invalid_visible_body_region": ~data["visible_body_region"].str.strip().isin(VALID_BODY_REGIONS),
        "missing_exercise_label": labels.eq(""),
    }
    incomplete = pd.Series(False, index=data.index)
    result_rows: list[dict[str, object]] = []
    for index in data.index:
        issues = [name for name, mask in checks.items() if bool(mask.loc[index])]
        incomplete.loc[index] = bool(issues)
        result_rows.append({
            "row_number": int(index) + 2,
            "video_path": paths.loc[index],
            "is_complete": not issues,
            "issue_codes": ";".join(issues),
        })

    complete_count = int((~incomplete).sum())
    total = len(data)
    distributions = {
        "class_distribution": Counter(labels[labels.ne("")]),
        "participant_distribution": Counter(participant[participant.ne("")]),
        "dataset_source_distribution": Counter(data["dataset_source"].str.strip().replace("", "unknown")),
        "expected_reps_distribution": Counter(expected_text.replace("", "missing")),
        "recording_quality_distribution": Counter(data["recording_quality"].str.strip().replace("", "missing")),
    }
    summary: dict[str, object] = {
        "total_rows": total,
        "complete_rows": complete_count,
        "completion_percentage": round(100 * complete_count / total, 2) if total else 0.0,
        **{name: int(mask.sum()) for name, mask in checks.items()},
        **{name: dict(counts) for name, counts in distributions.items()},
        "participant_count": int(participant[participant.ne("")].nunique()),
        "missing_supported_classes": sorted(SUPPORTED_CLASSES.difference(distributions["class_distribution"])),
        "is_ready": bool(total and not incomplete.any()),
    }

    results_path = results_path or report_path.with_name("manual_annotation_validation_results.csv")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result_rows, columns=RESULT_COLUMNS).to_csv(results_path, index=False)
    lines = [
        "# Manual Annotation Validation Report", "",
        f"**Status: {'READY' if summary['is_ready'] else 'INCOMPLETE'}**", "",
        "This is an engineering/data-quality review, not clinical validation.", "",
        "## Completion", "",
        f"- Total rows: {total}",
        f"- Completed annotations: {complete_count}",
        f"- Annotation completion: {summary['completion_percentage']:.2f}%", "",
        "## Missing and Invalid Fields", "",
    ]
    lines.extend(f"- {name.replace('_', ' ').title()}: {int(mask.sum())}" for name, mask in checks.items())
    for title, key in (
        ("Class Balance", "class_distribution"),
        ("Participant Distribution", "participant_distribution"),
        ("Dataset Source Distribution", "dataset_source_distribution"),
        ("Expected Reps Distribution", "expected_reps_distribution"),
        ("Recording Quality Distribution", "recording_quality_distribution"),
    ):
        lines.extend(["", f"## {title}", "", *_counts(Counter(summary[key]))])
    lines.extend([
        "", "## Recommendations", "",
        "- Complete rep counts and pseudonymous participant/session metadata through manual review.",
        "- Use only the documented categorical values and resolve duplicate paths before freezing a split.",
        "- Collect real videos for every missing or underrepresented class.",
        "- Keep the model experimental until the promotion gates are met.", "",
    ])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate_annotations(args.input, args.report, args.results)
    except Exception as exc:
        print(f"Manual annotation validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validation report: {args.report}")
    print(f"Validation rows: {args.results}")
    print(f"Complete rows: {summary['complete_rows']}/{summary['total_rows']}")
    if not summary["is_ready"]:
        print("WARNING: Manual annotations are incomplete; model promotion remains blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
