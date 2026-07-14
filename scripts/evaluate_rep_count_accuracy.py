"""Evaluate the current squat rep counter against completed manual annotations."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from statistics import mean

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))
DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_RESULTS = Path("reports/rep_count_validation/rep_count_accuracy_results.csv")
DEFAULT_SUMMARY = Path("reports/rep_count_validation/rep_count_accuracy_summary.md")
RESULT_COLUMNS = [
    "video_path", "expected_reps", "predicted_reps", "absolute_error",
    "within_exact_match", "within_plus_minus_1", "rep_count_confidence",
    "ignored_partial_reps", "analysis_status", "validation_warnings",
]


def analyze_video(video_path: Path) -> dict[str, object]:
    from app.services.pose_estimation_service import extract_pose_landmarks
    from app.services.squat_analysis_service import analyze_squat_landmarks

    report = analyze_squat_landmarks(extract_pose_landmarks(video_path))
    return {
        "predicted_reps": report.total_reps,
        "rep_count_confidence": report.rep_count_confidence,
        "ignored_partial_reps": report.ignored_partial_reps,
        "analysis_status": report.status,
        "validation_warnings": "; ".join(report.validation_warnings or []),
    }


def evaluate_rep_counts(
    annotations_path: Path,
    results_path: Path,
    summary_path: Path,
    analyze: Callable[[Path], dict[str, object]] = analyze_video,
    repo_root: Path = REPO_ROOT,
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not annotations_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotations_path}")
    data = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
    required = {"video_path", "expected_reps"}
    if missing := required.difference(data.columns):
        raise ValueError("Annotation file is missing: " + ", ".join(sorted(missing)))

    annotated = data[data["expected_reps"].str.strip().ne("")].copy()
    rows: list[dict[str, object]] = []
    for row in annotated.itertuples(index=False):
        path_text = str(row.video_path).strip()
        try:
            expected = int(str(row.expected_reps).strip())
            if expected < 0:
                raise ValueError
        except ValueError:
            rows.append({
                "video_path": path_text, "expected_reps": row.expected_reps,
                "analysis_status": "skipped_invalid_expected_reps",
                "validation_warnings": "expected_reps must be a non-negative integer",
            })
            continue
        raw_path = Path(path_text)
        video_path = raw_path if raw_path.is_absolute() else repo_root / raw_path
        if not video_path.exists():
            rows.append({
                "video_path": path_text, "expected_reps": expected,
                "analysis_status": "skipped_missing_video",
                "validation_warnings": "Video file was not found.",
            })
            continue
        try:
            prediction = analyze(video_path)
            predicted = int(prediction["predicted_reps"])
            error = abs(predicted - expected)
            rows.append({
                "video_path": path_text, "expected_reps": expected,
                "predicted_reps": predicted, "absolute_error": error,
                "within_exact_match": error == 0, "within_plus_minus_1": error <= 1,
                "rep_count_confidence": prediction.get("rep_count_confidence", ""),
                "ignored_partial_reps": prediction.get("ignored_partial_reps", 0),
                "analysis_status": prediction.get("analysis_status", prediction.get("status", "unknown")),
                "validation_warnings": prediction.get("validation_warnings", ""),
            })
        except Exception as exc:
            rows.append({
                "video_path": path_text, "expected_reps": expected,
                "analysis_status": "failed", "validation_warnings": str(exc),
            })

    result = pd.DataFrame(rows).reindex(columns=RESULT_COLUMNS).fillna("")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(results_path, index=False)
    measured = result[pd.to_numeric(result["absolute_error"], errors="coerce").notna()].copy()
    errors = pd.to_numeric(measured["absolute_error"], errors="coerce")
    exact = int((errors == 0).sum())
    within_one = int((errors <= 1).sum())
    low_confidence = measured[pd.to_numeric(measured["rep_count_confidence"], errors="coerce").fillna(0) < 0.5]
    worst = measured.assign(_error=errors).sort_values("_error", ascending=False).head(5)
    summary: dict[str, object] = {
        "total_annotated_videos": len(annotated), "evaluated_videos": len(measured),
        "exact_match_rate": exact / len(measured) if len(measured) else None,
        "within_plus_minus_1_rate": within_one / len(measured) if len(measured) else None,
        "mean_absolute_error": mean(errors) if len(measured) else None,
        "low_confidence_cases": len(low_confidence),
    }
    metric = lambda value: "not available" if value is None else f"{value:.3f}"
    lines = [
        "# Rep Count Accuracy Summary", "",
        "Current rule-based rep counting is compared with human annotations; this is not clinical validation.", "",
        f"- Total annotated videos: {len(annotated)}", f"- Evaluated videos: {len(measured)}",
        f"- Exact match rate: {metric(summary['exact_match_rate'])}",
        f"- Within ±1 rate: {metric(summary['within_plus_minus_1_rate'])}",
        f"- Mean absolute error: {metric(summary['mean_absolute_error'])}",
        f"- Low-confidence cases: {len(low_confidence)}", "", "## Worst Cases", "",
    ]
    if worst.empty:
        lines.append("- No completed, readable annotation cases were available.")
    else:
        lines.extend(
            f"- `{row.video_path}`: expected {row.expected_reps}, predicted {row.predicted_reps}, absolute error {row.absolute_error}"
            for row in worst.itertuples()
        )
    lines.extend([
        "", "## Recommendations", "",
        "- Complete manual rep annotations before drawing reliability conclusions.",
        "- Review failures, low-confidence cases, ignored partial reps, and every error outside ±1.",
        "- Preserve current analyzer thresholds until reviewed evidence supports a change.", "",
    ])
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return result, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, summary = evaluate_rep_counts(args.annotations, args.results, args.summary)
    except Exception as exc:
        print(f"Rep count evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Rep count results: {args.results}")
    print(f"Rep count summary: {args.summary}")
    print(f"Evaluated videos: {summary['evaluated_videos']}/{summary['total_annotated_videos']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
