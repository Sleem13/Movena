"""Extract a combined MediaPipe landmark CSV from prepared custom squat videos."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

from prepare_custom_squat_videos import (
    DEFAULT_METADATA_PATH,
    DEFAULT_REPORT_PATH,
    SOURCE_DATASET,
    VIDEO_EXTENSIONS,
    write_validation_report,
)


LOGGER = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path("data/raw/custom_videos")
DEFAULT_OUTPUT_PATH = Path(
    "data/processed/pose_landmarks/custom_squat_videos_landmarks.csv"
)
DEFAULT_FAILED_PATH = Path("data/processed/pose_landmarks/failed_videos.csv")
OUTPUT_COLUMNS = [
    "source_dataset",
    "video_path",
    "label",
    "frame_index",
    "timestamp_sec",
    "landmark_id",
    "landmark_name",
    "x",
    "y",
    "z",
    "visibility",
]


def resolve_video_path(value: str) -> Path:
    """Resolve metadata paths written absolutely or relative to the project root."""
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return REPO_ROOT / path


def infer_label(path: Path) -> str:
    """Return an expected folder label or preserve the file as unlabeled."""
    parent = path.parent.name.lower()
    return parent if parent.startswith("squat_") else "unlabeled"


def discover_video_records(input_dir: Path) -> list[dict[str, str]]:
    """Discover videos directly when prepared metadata is unavailable."""
    if not input_dir.exists():
        return []
    return [
        {
            "source_dataset": SOURCE_DATASET,
            "video_path": str(path),
            "label": infer_label(path),
            "is_supported_video": "true",
        }
        for path in sorted(input_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]


def load_video_records(metadata_path: Path, input_dir: Path) -> list[dict[str, str]]:
    """Load supported videos from metadata, falling back to folder discovery."""
    if not metadata_path.exists():
        LOGGER.warning(
            "Metadata CSV not found at %s; discovering videos directly. Run "
            "prepare_custom_squat_videos.py for validation reporting.",
            metadata_path,
        )
        return discover_video_records(input_dir)

    with metadata_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"source_dataset", "video_path", "label", "is_supported_video"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Metadata CSV is missing columns: {', '.join(sorted(missing))}")
        return [row for row in reader if row["is_supported_video"].lower() == "true"]


def load_pose_dependencies():
    """Load and validate the OpenCV/MediaPipe runtime with actionable guidance."""
    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV and MediaPipe are required. Activate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        ) from exc

    if not all(
        hasattr(cv2, name)
        for name in ("VideoCapture", "cvtColor", "COLOR_BGR2RGB", "CAP_PROP_FPS")
    ):
        raise RuntimeError(
            "The installed cv2 package is incomplete. Recreate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        )
    if not hasattr(mp, "solutions"):
        raise RuntimeError(
            "The installed MediaPipe package is incomplete. Recreate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        )
    return cv2, mp


def process_video(
    record: dict[str, str],
    writer: csv.DictWriter,
    pose,
    cv2,
    mp,
    max_frames: int | None,
) -> tuple[int, int]:
    """Append one video's detected landmarks and return rows/processed-frame counts."""
    video_path = resolve_video_path(record["video_path"])
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Unable to open video.")

    rows_written = 0
    frame_index = 0
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            if max_frames is not None and frame_index >= max_frames:
                break

            result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if result.pose_landmarks:
                for landmark_id, landmark in enumerate(result.pose_landmarks.landmark):
                    writer.writerow(
                        {
                            "source_dataset": record.get("source_dataset") or SOURCE_DATASET,
                            "video_path": record["video_path"],
                            "label": record.get("label") or "unlabeled",
                            "frame_index": frame_index,
                            "timestamp_sec": round(frame_index / fps, 6),
                            "landmark_id": landmark_id,
                            "landmark_name": mp.solutions.pose.PoseLandmark(
                                landmark_id
                            ).name.lower(),
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility,
                        }
                    )
                    rows_written += 1
            frame_index += 1
    finally:
        cap.release()

    if frame_index == 0:
        raise RuntimeError("Video has no readable frames.")
    if rows_written == 0:
        raise RuntimeError("No pose landmarks detected.")
    return rows_written, frame_index


def write_failures(failed_path: Path, failures: list[dict[str, str]]) -> None:
    """Write or remove the current failed-video report."""
    if not failures:
        failed_path.unlink(missing_ok=True)
        return
    failed_path.parent.mkdir(parents=True, exist_ok=True)
    with failed_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["video_path", "label", "error"])
        writer.writeheader()
        writer.writerows(failures)


def extract_custom_video_landmarks(
    metadata_path: Path,
    input_dir: Path,
    output_path: Path,
    failed_path: Path,
    max_frames: int | None = None,
) -> tuple[Path, int, list[dict[str, str]]]:
    """Extract all prepared custom videos into one combined landmark CSV."""
    records = load_video_records(metadata_path, input_dir)
    if not records:
        raise FileNotFoundError(
            f"No supported videos found under {input_dir}. Run prepare_custom_squat_videos.py first."
        )
    if max_frames is not None and max_frames <= 0:
        raise ValueError("max_frames must be positive when provided.")

    cv2, mp = load_pose_dependencies()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    failures: list[dict[str, str]] = []
    total_rows = 0

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        with mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:
            for record in records:
                try:
                    rows, frames = process_video(
                        record, writer, pose, cv2, mp, max_frames
                    )
                    total_rows += rows
                    LOGGER.info(
                        "Extracted %s rows from %s frames: %s",
                        rows,
                        frames,
                        record["video_path"],
                    )
                except Exception as exc:
                    failures.append(
                        {
                            "video_path": record["video_path"],
                            "label": record.get("label", "unlabeled"),
                            "error": str(exc),
                        }
                    )
                    LOGGER.error("Failed %s: %s", record["video_path"], exc)

    write_failures(failed_path, failures)
    if total_rows == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"No landmarks were extracted from {len(records)} video(s). See {failed_path}."
        )
    return output_path, total_rows, failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract combined MediaPipe landmarks from custom squat videos."
    )
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--failed-output", type=Path, default=DEFAULT_FAILED_PATH)
    parser.add_argument("--max-frames", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        output_path, rows, failures = extract_custom_video_landmarks(
            args.metadata,
            args.input_dir,
            args.output,
            args.failed_output,
            args.max_frames,
        )
    except Exception as exc:
        try:
            write_validation_report(
                args.metadata,
                DEFAULT_REPORT_PATH,
                args.output,
                args.failed_output,
            )
        except Exception as report_exc:
            LOGGER.warning("Could not refresh validation report: %s", report_exc)
        print(f"Video landmark extraction failed: {exc}", file=sys.stderr)
        return 1

    try:
        write_validation_report(
            args.metadata,
            DEFAULT_REPORT_PATH,
            output_path,
            args.failed_output,
        )
    except Exception as exc:
        LOGGER.warning("Could not refresh validation report: %s", exc)

    print(f"Saved {rows} custom squat landmark rows: {output_path}")
    if failures:
        print(f"Failed videos: {len(failures)}. See {args.failed_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
