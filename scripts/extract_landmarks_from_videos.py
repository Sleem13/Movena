"""Extract MediaPipe Pose landmarks from local sample or custom videos.

TODO: Place consented local videos under data/samples/ or data/raw/custom_videos/ before running.
This script does not download videos or public datasets.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_INPUT_DIRS = [Path("data/samples"), Path("data/raw/custom_videos")]
DEFAULT_OUTPUT_DIR = Path("data/processed/pose_landmarks")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def infer_label(video_path: Path) -> str:
    """Infer a simple exercise issue label from the parent folder."""
    folder_name = video_path.parent.name.lower()
    if folder_name.startswith("squat_"):
        return folder_name.replace("squat_", "")
    return "unlabeled"


def infer_exercise(video_path: Path) -> str:
    """Infer exercise name from folder or file text."""
    text = f"{video_path.parent.name}_{video_path.stem}".lower()
    if "squat" in text:
        return "bodyweight_squat"
    return "unknown"


def iter_videos(input_dirs: list[Path]) -> list[Path]:
    """Find supported videos under one or more local folders."""
    videos: list[Path] = []
    for input_dir in input_dirs:
        if not input_dir.exists():
            continue
        videos.extend(
            path
            for path in input_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
        )
    return sorted(set(videos))


def extract_video_landmarks(video_path: Path, output_path: Path, max_frames: int | None = None) -> int:
    """Extract all 33 MediaPipe landmarks for each readable video frame."""
    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV and MediaPipe are required. Run pip install -r backend/requirements.txt."
        ) from exc

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Unable to open video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    source_dataset = "physiovision_samples"
    exercise_name = infer_exercise(video_path)
    exercise_label = infer_label(video_path)
    rows_written = 0
    frame_index = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "source_dataset",
                "subject_id",
                "session_id",
                "exercise_name",
                "video_path",
                "frame_index",
                "timestamp",
                "exercise_label",
                "landmark_name",
                "landmark_id",
                "x",
                "y",
                "z",
                "visibility",
                "correctness_label",
            ],
        )
        writer.writeheader()

        with mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:
            while True:
                success, frame = cap.read()
                if not success:
                    break
                if max_frames is not None and frame_index >= max_frames:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb_frame)
                if result.pose_landmarks:
                    for index, landmark in enumerate(result.pose_landmarks.landmark):
                        writer.writerow(
                            {
                                "source_dataset": source_dataset,
                                "subject_id": "unknown",
                                "session_id": "unknown",
                                "exercise_name": exercise_name,
                                "video_path": str(video_path),
                                "frame_index": frame_index,
                                "timestamp": round(frame_index / fps, 4),
                                "exercise_label": exercise_label,
                                "landmark_name": mp.solutions.pose.PoseLandmark(index).name.lower(),
                                "landmark_id": index,
                                "x": landmark.x,
                                "y": landmark.y,
                                "z": landmark.z,
                                "visibility": landmark.visibility,
                                "correctness_label": exercise_label,
                            }
                        )
                        rows_written += 1

                frame_index += 1

    cap.release()
    if rows_written == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("No pose landmarks detected.")
    return rows_written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract MediaPipe landmarks from local videos.")
    parser.add_argument(
        "--input-dir",
        action="append",
        type=Path,
        default=None,
        help="Input directory. Can be passed multiple times. Defaults to data/samples and data/raw/custom_videos.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-frames", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dirs = args.input_dir or DEFAULT_INPUT_DIRS
    videos = iter_videos(input_dirs)
    if not videos:
        searched = ", ".join(str(path) for path in input_dirs)
        print(f"No videos found under {searched}. Add local sample videos first.", file=sys.stderr)
        return 1

    failed: list[dict[str, str]] = []
    for video_path in videos:
        output_path = args.output_dir / f"{video_path.stem}_landmarks.csv"
        try:
            rows = extract_video_landmarks(video_path, output_path, args.max_frames)
            print(f"Extracted {rows} landmark rows: {output_path}")
        except Exception as exc:
            failed.append({"video_path": str(video_path), "error": str(exc)})
            print(f"Failed {video_path}: {exc}", file=sys.stderr)

    if failed:
        failed_path = args.output_dir / "failed_videos.csv"
        failed_path.parent.mkdir(parents=True, exist_ok=True)
        with failed_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["video_path", "error"])
            writer.writeheader()
            writer.writerows(failed)
        print(f"Saved failed video list: {failed_path}")

    return 0 if len(failed) < len(videos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
