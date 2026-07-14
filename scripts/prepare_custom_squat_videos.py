"""Prepare metadata and validation reporting for local custom squat videos."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from collections import Counter
from pathlib import Path


LOGGER = logging.getLogger(__name__)
SOURCE_DATASET = "custom_squat_videos"
DEFAULT_INPUT_DIR = Path("data/raw/custom_videos")
DEFAULT_METADATA_PATH = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_REPORT_PATH = Path(
    "data/processed/labels/custom_squat_videos_validation_report.md"
)
DEFAULT_LANDMARKS_PATH = Path(
    "data/processed/pose_landmarks/custom_squat_videos_landmarks.csv"
)
DEFAULT_FAILED_PATH = Path("data/processed/pose_landmarks/failed_videos.csv")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
EXPECTED_LABELS = [
    "squat_correct",
    "squat_shallow_depth",
    "squat_knee_valgus",
    "squat_trunk_lean",
    "squat_fast_uncontrolled",
]
METADATA_COLUMNS = [
    "source_dataset",
    "video_path",
    "label",
    "filename",
    "file_extension",
    "file_size_bytes",
    "parent_folder",
    "is_supported_video",
    "notes",
]


def scan_files(input_dir: Path) -> list[Path]:
    """Return local files recursively, excluding repository placeholders."""
    if not input_dir.exists():
        return []
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    )


def metadata_row(path: Path) -> dict[str, object]:
    """Create one metadata row without opening or decoding the video."""
    parent_folder = path.parent.name.lower()
    is_supported = path.suffix.lower() in VIDEO_EXTENSIONS
    if parent_folder in EXPECTED_LABELS:
        label = parent_folder
        label_note = ""
    else:
        label = "unlabeled"
        label_note = (
            f"Unrecognized label folder: {path.parent.name}. Review-only video; "
            "excluded from official supervised-label use until manually curated."
        )

    filename_lower = path.stem.lower()
    filename_label = next(
        (candidate for candidate in EXPECTED_LABELS if filename_lower.startswith(candidate)),
        None,
    )
    if filename_label and filename_label != label:
        label_note = (
            f"{label_note} Filename suggests {filename_label}, but the parent folder "
            f"maps to {label}."
        ).strip()

    notes = label_note
    if not is_supported:
        notes = f"{notes} Unsupported file extension.".strip()

    return {
        "source_dataset": SOURCE_DATASET,
        "video_path": str(path),
        "label": label,
        "filename": path.name,
        "file_extension": path.suffix.lower(),
        "file_size_bytes": path.stat().st_size,
        "parent_folder": path.parent.name,
        "is_supported_video": str(is_supported).lower(),
        "notes": notes,
    }


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV as dictionaries, returning an empty list when absent."""
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def landmark_video_paths(landmarks_path: Path) -> set[str]:
    """Return unique video paths represented in a combined landmark CSV."""
    if not landmarks_path.exists():
        return set()
    paths: set[str] = set()
    with landmarks_path.open("r", newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            if video_path := row.get("video_path", ""):
                paths.add(video_path)
    return paths


def write_validation_report(
    metadata_path: Path,
    report_path: Path,
    landmarks_path: Path = DEFAULT_LANDMARKS_PATH,
    failed_path: Path = DEFAULT_FAILED_PATH,
) -> Path:
    """Write a concise readiness report from metadata and optional extraction outputs."""
    rows = read_csv_rows(metadata_path)
    supported = [row for row in rows if row.get("is_supported_video") == "true"]
    unsupported = [row for row in rows if row.get("is_supported_video") != "true"]
    counts = Counter(row.get("label", "unlabeled") for row in supported)
    extracted_paths = landmark_video_paths(landmarks_path)
    failures = read_csv_rows(failed_path)
    failed_paths = {row.get("video_path", "") for row in failures}

    missing_labels = [label for label in EXPECTED_LABELS if counts[label] == 0]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Custom Squat Videos Validation Report",
        "",
        f"- Total videos found: {len(supported)}",
        f"- Unsupported files: {len(unsupported)}",
        f"- Videos with extracted landmarks: {len(extracted_paths)}",
        f"- Landmark extraction failures: {len(failed_paths)}",
        "",
        "## Videos Per Label",
        "",
        "| Label | Videos |",
        "|---|---:|",
    ]
    for label in EXPECTED_LABELS + (["unlabeled"] if counts["unlabeled"] else []):
        lines.append(f"| `{label}` | {counts[label]} |")

    lines.extend(["", "## Unsupported Files", ""])
    if unsupported:
        lines.extend(
            f"- `{row.get('video_path', '')}`: {row.get('notes', 'unsupported')}"
            for row in unsupported
        )
    else:
        lines.append("- None detected.")

    warnings = [row for row in rows if row.get("notes")]
    lines.extend(["", "## Metadata Warnings", ""])
    if warnings:
        lines.extend(
            f"- `{row.get('video_path', '')}`: {row.get('notes', '')}" for row in warnings
        )
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Landmark Extraction", ""])
    if extracted_paths:
        lines.append(f"- Success: {len(extracted_paths)} video(s).")
    else:
        lines.append("- Not available yet; run `python scripts/extract_landmarks_from_videos.py`.")
    if failures:
        for row in failures:
            lines.append(
                f"- Failed: `{row.get('video_path', '')}` — {row.get('error', 'unknown error')}"
            )
    else:
        lines.append("- No failed-video records are currently available.")

    lines.extend(["", "## Recommendations", ""])
    if missing_labels:
        lines.append(
            "- Add consented validation videos for missing labels: "
            + ", ".join(f"`{label}`" for label in missing_labels)
            + "."
        )
    else:
        lines.append("- Every expected label has at least one video.")
    if counts["unlabeled"]:
        lines.append(
            "- Review files under unrecognized folders and move them only after confirming the correct label."
        )
    lines.append(
        "- Keep raw videos local and obtain consent before using recordings for product validation."
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def prepare_custom_videos(
    input_dir: Path,
    metadata_path: Path,
    report_path: Path,
) -> tuple[Path, Path, int]:
    """Scan local files, write metadata, and return the supported-video count."""
    rows = [metadata_row(path) for path in scan_files(input_dir)]
    supported_count = sum(row["is_supported_video"] == "true" for row in rows)
    if supported_count == 0:
        raise FileNotFoundError(
            f"No supported videos found under {input_dir}. Add .mp4, .mov, .avi, .mkv, "
            "or .webm files to the expected squat label folders first."
        )

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    write_validation_report(metadata_path, report_path)
    LOGGER.info("Saved %s supported video records to %s", supported_count, metadata_path)
    return metadata_path, report_path, supported_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare custom squat video metadata.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        metadata_path, report_path, count = prepare_custom_videos(
            args.input_dir, args.output, args.report
        )
    except Exception as exc:
        print(f"Custom squat video preparation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Detected {count} custom squat videos.")
    print(f"Saved metadata: {metadata_path}")
    print(f"Saved validation report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
