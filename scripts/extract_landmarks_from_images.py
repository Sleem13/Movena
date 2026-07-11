"""Extract MediaPipe Pose landmarks from prepared Zenodo squat images."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA_PATH = Path("data/processed/labels/zenodo_squat_dataset_labels.csv")
DEFAULT_OUTPUT_PATH = Path(
    "data/processed/pose_landmarks/zenodo_squat_dataset/zenodo_squat_landmarks.csv"
)
REQUIRED_METADATA_COLUMNS = {"source_dataset", "image_path", "label"}
OUTPUT_COLUMNS = [
    "source_dataset",
    "image_path",
    "label",
    "landmark_id",
    "landmark_name",
    "x",
    "y",
    "z",
    "visibility",
]


def resolve_image_path(value: str) -> Path:
    """Resolve metadata paths written either absolutely or from the project root."""
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return REPO_ROOT / path


def extract_landmarks(metadata_path: Path, output_path: Path) -> Path:
    """Extract all 33 MediaPipe landmarks for each decodable, detected image."""
    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV and MediaPipe are required. Activate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        ) from exc
    if not all(hasattr(cv2, name) for name in ("imread", "cvtColor", "COLOR_BGR2RGB")):
        raise RuntimeError(
            "The installed cv2 package is incomplete. Recreate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        )
    if not hasattr(mp, "solutions"):
        raise RuntimeError(
            "The installed MediaPipe package is incomplete. Recreate the project .venv and run "
            "python -m pip install -r requirements-dev.txt."
        )

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata CSV not found: {metadata_path}. Run prepare_zenodo_squat_dataset.py first."
        )

    with metadata_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = REQUIRED_METADATA_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Metadata CSV is missing columns: {', '.join(sorted(missing))}")
        metadata_rows = list(reader)

    if not metadata_rows:
        raise ValueError("Metadata CSV contains no image rows.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    images_detected = 0
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()

        with mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
        ) as pose:
            for metadata in metadata_rows:
                image_path = resolve_image_path(metadata["image_path"])
                image = cv2.imread(str(image_path))
                if image is None:
                    LOGGER.warning("Skipping unreadable image: %s", image_path)
                    continue

                result = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                if not result.pose_landmarks:
                    LOGGER.warning("No pose detected: %s", image_path)
                    continue

                images_detected += 1
                for landmark_id, landmark in enumerate(result.pose_landmarks.landmark):
                    writer.writerow(
                        {
                            "source_dataset": metadata["source_dataset"],
                            "image_path": metadata["image_path"],
                            "label": metadata["label"],
                            "landmark_id": landmark_id,
                            "landmark_name": mp.solutions.pose.PoseLandmark(landmark_id).name.lower(),
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility,
                        }
                    )
                    rows_written += 1

    if rows_written == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(
            "No pose landmarks were detected. Check image validity, side-view framing, and lighting."
        )

    LOGGER.info(
        "Saved %s landmarks from %s images to %s",
        rows_written,
        images_detected,
        output_path,
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract landmarks from Zenodo squat images.")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        output_path = extract_landmarks(args.metadata, args.output)
    except Exception as exc:
        print(f"Image landmark extraction failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved Zenodo squat image landmarks: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
