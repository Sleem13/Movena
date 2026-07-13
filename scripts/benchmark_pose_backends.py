"""Benchmark optional pretrained pose backbones on custom squat videos."""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.pose_backends import (  # noqa: E402
    BasePoseBackend,
    MediaPipePoseBackend,
    PoseBackendResult,
    PoseBackendUnavailableError,
    create_pose_backend,
)
from app.services.squat_analysis_service import (  # noqa: E402
    analyze_squat_landmarks,
    create_frame_analysis,
)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
DEFAULT_INPUT = PROJECT_ROOT / "data/raw/custom_videos"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports/pose_backend_benchmark"
METRIC_COLUMNS = [
    "backend",
    "video_path",
    "label",
    "frames_processed",
    "frames_with_pose",
    "pose_detection_success_rate",
    "missing_landmark_rate",
    "average_landmark_confidence",
    "angle_smoothness_deg",
    "knee_angle_stability_deg",
    "hip_angle_stability_deg",
    "trunk_angle_stability_deg",
    "processing_fps",
    "runtime_sec",
    "issue_detection_agreement",
    "status",
    "error",
]


def discover_videos(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )


def _jitter(values: list[float]) -> float:
    """Return mean absolute second difference; lower means less frame jitter."""
    if len(values) < 3:
        return 0.0
    return statistics.fmean(
        abs(values[index] - 2 * values[index - 1] + values[index - 2])
        for index in range(2, len(values))
    )


def _issue_set(frames: list[dict[str, Any]]) -> set[str]:
    if not frames:
        return set()
    return set(analyze_squat_landmarks(frames).detected_issues)


def _agreement(candidate: set[str], baseline: set[str]) -> float:
    union = candidate | baseline
    return 1.0 if not union else len(candidate & baseline) / len(union)


def metrics_from_result(
    result: PoseBackendResult,
    video_path: Path,
    baseline_issues: set[str] | None = None,
) -> dict[str, Any]:
    """Convert a normalized backend result into one stable CSV-shaped row."""
    detected = len(result.detected_frames)
    expected_slots = result.processed_frames * result.expected_landmark_count
    observed_slots = sum(
        min(len(frame.get("landmarks", {})), result.expected_landmark_count)
        for frame in result.detected_frames
    )
    confidence_values = [
        float(point.get("visibility", 0.0))
        for frame in result.detected_frames
        for point in frame.get("landmarks", {}).values()
    ]

    analysis_rows = create_frame_analysis(result.detected_frames) if detected else []
    knee = [row.knee_angle for row in analysis_rows]
    hip = [row.hip_angle for row in analysis_rows]
    trunk = [row.trunk_angle for row in analysis_rows]
    stability = [_jitter(knee), _jitter(hip), _jitter(trunk)]
    candidate_issues = _issue_set(result.detected_frames)
    reference = candidate_issues if baseline_issues is None else baseline_issues

    return {
        "backend": result.backend_name,
        "video_path": video_path.as_posix(),
        "label": video_path.parent.name,
        "frames_processed": result.processed_frames,
        "frames_with_pose": detected,
        "pose_detection_success_rate": round(detected / result.processed_frames, 6),
        "missing_landmark_rate": round(
            (expected_slots - observed_slots) / expected_slots, 6
        ),
        "average_landmark_confidence": round(
            statistics.fmean(confidence_values), 6
        ) if confidence_values else 0.0,
        "angle_smoothness_deg": round(statistics.fmean(stability), 6),
        "knee_angle_stability_deg": round(stability[0], 6),
        "hip_angle_stability_deg": round(stability[1], 6),
        "trunk_angle_stability_deg": round(stability[2], 6),
        "processing_fps": round(result.processed_frames / result.runtime_sec, 3)
        if result.runtime_sec > 0 else math.inf,
        "runtime_sec": round(result.runtime_sec, 6),
        "issue_detection_agreement": round(_agreement(candidate_issues, reference), 6),
        "status": "success",
        "error": "",
    }


def benchmark_videos(
    backend: BasePoseBackend, videos: Iterable[Path]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    baseline = None if backend.name == "mediapipe" else MediaPipePoseBackend()
    for video_path in videos:
        try:
            baseline_issues = None
            if baseline is not None:
                baseline_issues = _issue_set(baseline.extract(video_path).detected_frames)
            rows.append(metrics_from_result(backend.extract(video_path), video_path, baseline_issues))
        except Exception as exc:  # Continue the offline batch and record the failure.
            row = {column: "" for column in METRIC_COLUMNS}
            row.update(
                backend=backend.name,
                video_path=video_path.as_posix(),
                label=video_path.parent.name,
                status="failed",
                error=str(exc),
            )
            rows.append(row)
    return rows


def write_outputs(rows: list[dict[str, Any]], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "pose_backend_metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METRIC_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    successes = [row for row in rows if row["status"] == "success"]
    failures = [row for row in rows if row["status"] != "success"]
    summary_path = output_dir / "pose_backend_summary.md"
    summary_lines = [
        "# Pose Backend Benchmark Summary",
        "",
        "> Offline engineering benchmark only. This is not clinical validation.",
        "",
        f"- Videos attempted: {len(rows)}",
        f"- Successful: {len(successes)}",
        f"- Failed: {len(failures)}",
    ]
    if successes:
        summary_lines.extend(
            [
                f"- Mean pose detection success rate: {statistics.fmean(float(row['pose_detection_success_rate']) for row in successes):.3f}",
                f"- Mean processing FPS: {statistics.fmean(float(row['processing_fps']) for row in successes):.2f}",
                f"- Mean issue-detection agreement: {statistics.fmean(float(row['issue_detection_agreement']) for row in successes):.3f}",
            ]
        )
    if failures:
        summary_lines.extend(["", "## Failures", ""])
        summary_lines.extend(
            f"- `{row['video_path']}`: {row['error']}" for row in failures
        )
    summary_lines.extend(
        [
            "",
            "Angle stability is mean absolute second difference in degrees (lower is smoother).",
            "Agreement is Jaccard agreement between candidate and current MediaPipe-backed rule issue sets.",
        ]
    )
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    return metrics_path, summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        default=os.getenv("POSE_BACKEND", "mediapipe"),
        choices=["mediapipe", "movenet_lightning", "movenet_thunder"],
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    videos = discover_videos(args.input_dir)
    if args.limit is not None:
        videos = videos[: max(args.limit, 0)]
    if not videos:
        print(f"No supported videos found under {args.input_dir}.", file=sys.stderr)
        return 1

    backend = create_pose_backend(args.backend)
    if not backend.is_available():
        try:
            backend.extract(videos[0])
        except PoseBackendUnavailableError as exc:
            print(str(exc), file=sys.stderr)
        return 2

    rows = benchmark_videos(backend, videos)
    metrics_path, summary_path = write_outputs(rows, args.output_dir)
    print(f"Saved {len(rows)} benchmark row(s): {metrics_path}")
    print(f"Saved summary: {summary_path}")
    return 0 if all(row["status"] == "success" for row in rows) else 3


if __name__ == "__main__":
    raise SystemExit(main())
