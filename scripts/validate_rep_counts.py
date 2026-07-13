"""Validate stabilized squat rep counts against manually entered ground truth."""

from __future__ import annotations

import csv
import sys
from collections.abc import Callable
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

DEFAULT_METADATA = REPO_ROOT / "data/processed/labels/custom_squat_videos_labels.csv"
DEFAULT_MANUAL = REPO_ROOT / "data/processed/labels/custom_squat_manual_rep_counts.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports/rep_count_validation"


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def create_manual_template(metadata_path: Path, manual_path: Path) -> int:
    rows = _read_rows(metadata_path)
    unique_paths = list(dict.fromkeys(row.get("video_path", "") for row in rows if row.get("video_path")))
    manual_path.parent.mkdir(parents=True, exist_ok=True)
    with manual_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["video_path", "expected_reps", "notes"])
        writer.writeheader()
        writer.writerows(
            {"video_path": video_path, "expected_reps": "", "notes": ""}
            for video_path in unique_paths
        )
    return len(unique_paths)


def analyze_video(video_path: Path) -> dict[str, object]:
    from app.services.pose_estimation_service import extract_pose_landmarks
    from app.services.squat_analysis_service import analyze_squat_landmarks

    report = analyze_squat_landmarks(extract_pose_landmarks(video_path))
    return {
        "predicted_reps": report.total_reps,
        "rep_count_confidence": report.rep_count_confidence,
        "ignored_partial_reps": report.ignored_partial_reps,
        "status": report.status,
    }


def run_validation(
    manual_path: Path,
    output_dir: Path,
    analyze: Callable[[Path], dict[str, object]] = analyze_video,
) -> tuple[Path, Path, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "rep_count_validation_results.csv"
    summary_path = output_dir / "rep_count_validation_summary.md"
    results: list[dict[str, object]] = []

    for row in _read_rows(manual_path):
        expected_text = (row.get("expected_reps") or "").strip()
        if not expected_text:
            continue
        try:
            expected = int(expected_text)
        except ValueError:
            continue
        raw_path = Path(row["video_path"])
        video_path = raw_path if raw_path.is_absolute() else REPO_ROOT / raw_path
        try:
            prediction = analyze(video_path)
            predicted = int(prediction["predicted_reps"])
            results.append(
                {
                    "video_path": row["video_path"],
                    "expected_reps": expected,
                    "predicted_reps": predicted,
                    "absolute_error": abs(predicted - expected),
                    "rep_count_confidence": prediction["rep_count_confidence"],
                    "ignored_partial_reps": prediction["ignored_partial_reps"],
                    "status": prediction["status"],
                }
            )
        except Exception as exc:
            results.append(
                {
                    "video_path": row["video_path"],
                    "expected_reps": expected,
                    "predicted_reps": "",
                    "absolute_error": "",
                    "rep_count_confidence": 0,
                    "ignored_partial_reps": 0,
                    "status": f"failed: {exc}",
                }
            )

    fields = [
        "video_path", "expected_reps", "predicted_reps", "absolute_error",
        "rep_count_confidence", "ignored_partial_reps", "status",
    ]
    with results_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    measured = [row for row in results if isinstance(row["absolute_error"], int)]
    errors = [int(row["absolute_error"]) for row in measured]
    within_one = sum(error <= 1 for error in errors)
    worst = sorted(measured, key=lambda row: int(row["absolute_error"]), reverse=True)[:5]
    lines = [
        "# Rep Count Validation Summary",
        "",
        f"- Videos with manual expected counts: {len(results)}",
        f"- Successfully measured videos: {len(measured)}",
        f"- Mean absolute error: {mean(errors):.3f}" if errors else "- Mean absolute error: not available",
        f"- Videos within ±1 rep: {within_one}/{len(measured)}" if measured else "- Videos within ±1 rep: not available",
        "",
        "## Worst cases",
        "",
    ]
    if worst:
        lines.extend(
            f"- `{row['video_path']}`: expected {row['expected_reps']}, predicted {row['predicted_reps']}, error {row['absolute_error']}"
            for row in worst
        )
    else:
        lines.append("No completed manual labels were available.")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "Review every case outside ±1 rep and confirm start/end trimming, full-body visibility, and manual event boundaries before changing thresholds.",
        ]
    )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results_path, summary_path, len(measured)


def main() -> int:
    if not DEFAULT_MANUAL.exists():
        count = create_manual_template(DEFAULT_METADATA, DEFAULT_MANUAL)
        print(f"Created manual rep-count template with {count} videos: {DEFAULT_MANUAL}")
        print("Fill expected_reps after manual review, then run this command again.")
        return 0
    completed = sum(bool((row.get("expected_reps") or "").strip()) for row in _read_rows(DEFAULT_MANUAL))
    if completed == 0:
        print(f"Manual template exists but expected_reps is blank: {DEFAULT_MANUAL}")
        print("Enter manually verified counts, then run this command again.")
        return 0
    results, summary, measured = run_validation(DEFAULT_MANUAL, DEFAULT_OUTPUT_DIR)
    print(f"Validated {measured} videos. Results: {results}")
    print(f"Summary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
