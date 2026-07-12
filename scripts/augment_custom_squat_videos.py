"""Generate conservative custom squat video augmentations and an audit registry."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np


LABELS = [
    "squat_correct", "squat_shallow_depth", "squat_knee_valgus",
    "squat_trunk_lean", "squat_fast_uncontrolled",
]
AUGMENTATION_PLAN = {
    "squat_correct": ["brightness", "contrast", "horizontal_flip"],
    "squat_shallow_depth": ["brightness", "contrast", "horizontal_flip", "slight_rotation"],
    "squat_knee_valgus": ["brightness", "contrast", "horizontal_flip", "slight_rotation"],
    "squat_trunk_lean": ["brightness", "contrast", "horizontal_flip", "slight_rotation"],
    "squat_fast_uncontrolled": ["brightness", "contrast"],
}
METADATA_COLUMNS = [
    "source_video_path", "augmented_video_path", "original_label", "augmented_label",
    "augmentation_type", "augmentation_parameters", "filename", "file_extension",
    "file_size_bytes", "duration_sec", "fps", "frame_count", "safe_for_training", "notes",
]
DEFAULT_INPUT = Path("data/raw/custom_videos")
DEFAULT_OUTPUT = Path("data/augmented/custom_videos")
DEFAULT_METADATA = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")


def augmentation_parameters(name: str) -> dict[str, float | int]:
    return {
        "horizontal_flip": {},
        "brightness": {"beta": 18},
        "contrast": {"alpha": 1.10},
        "slight_rotation": {"degrees": 4.0},
        "slight_zoom": {"scale": 0.95},
        "gaussian_noise": {"sigma": 3.0},
        "speed_variation": {"fps_multiplier": 1.15},
        "compression_variation": {"fourcc": "mp4v"},
    }[name]


def augment_frame(frame: np.ndarray, name: str, parameters: dict, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng(42)
    height, width = frame.shape[:2]
    if name == "horizontal_flip":
        return cv2.flip(frame, 1)
    if name == "brightness":
        return cv2.convertScaleAbs(frame, alpha=1.0, beta=float(parameters["beta"]))
    if name == "contrast":
        return cv2.convertScaleAbs(frame, alpha=float(parameters["alpha"]), beta=0)
    if name == "slight_rotation":
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), float(parameters["degrees"]), 1.0)
        return cv2.warpAffine(frame, matrix, (width, height), borderMode=cv2.BORDER_REFLECT_101)
    if name == "slight_zoom":
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 0, float(parameters["scale"]))
        return cv2.warpAffine(frame, matrix, (width, height), borderMode=cv2.BORDER_REFLECT_101)
    if name == "gaussian_noise":
        noise = rng.normal(0, float(parameters["sigma"]), frame.shape)
        return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if name in {"speed_variation", "compression_variation"}:
        return frame.copy()
    raise ValueError(f"Unsupported augmentation: {name}")


def video_metadata(path: Path) -> dict[str, float | int]:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video: {path}")
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    capture.release()
    return {
        "fps": round(fps, 6),
        "frame_count": frame_count,
        "duration_sec": round(frame_count / fps, 6) if fps > 0 else 0.0,
    }


def write_augmented_video(
    source: Path,
    destination: Path,
    name: str,
    parameters: dict,
    overwrite: bool = False,
) -> Path:
    if source.resolve() == destination.resolve():
        raise ValueError("Augmentation destination must not overwrite the source video.")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Augmented output already exists: {destination}")
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError(f"Unable to open source video: {source}")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    if name == "speed_variation":
        fps *= float(parameters["fps_multiplier"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(destination), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        capture.release()
        raise ValueError(f"Unable to create augmented video: {destination}")
    rng = np.random.default_rng(42)
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            writer.write(augment_frame(frame, name, parameters, rng))
    finally:
        capture.release()
        writer.release()
    if not destination.exists() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ValueError(f"Augmented output is empty: {destination}")
    return destination


def generate_augmentations(
    input_dir: Path,
    output_dir: Path,
    metadata_path: Path,
    max_per_source: int = 2,
    overwrite: bool = False,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label in LABELS:
        (output_dir / label).mkdir(parents=True, exist_ok=True)
        for source in sorted((input_dir / label).glob("*")) if (input_dir / label).exists() else []:
            if not source.is_file() or source.suffix.lower() not in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
                continue
            for name in AUGMENTATION_PLAN[label][:max_per_source]:
                parameters = augmentation_parameters(name)
                destination = output_dir / label / f"{source.stem}__{name}.mp4"
                write_augmented_video(source, destination, name, parameters, overwrite)
                meta = video_metadata(destination)
                notes = "Label preserved; synthetic robustness variant, not independent real data."
                if name == "horizontal_flip":
                    notes += " Left/right interpretation is reversed and must be handled during landmark use."
                rows.append({
                    "source_video_path": str(source).replace("\\", "/"),
                    "augmented_video_path": str(destination).replace("\\", "/"),
                    "original_label": label,
                    "augmented_label": label,
                    "augmentation_type": name,
                    "augmentation_parameters": json.dumps(parameters, sort_keys=True),
                    "filename": destination.name,
                    "file_extension": destination.suffix.lower(),
                    "file_size_bytes": destination.stat().st_size,
                    **meta,
                    "safe_for_training": "true",
                    "notes": notes,
                })
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--max-per-source", type=int, default=2)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_per_source < 0:
        print("max-per-source must be non-negative", file=sys.stderr)
        return 1
    try:
        rows = generate_augmentations(
            args.input_dir, args.output_dir, args.metadata, args.max_per_source, args.overwrite
        )
    except Exception as exc:
        print(f"Video augmentation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {len(rows)} conservative augmented videos. Metadata: {args.metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
