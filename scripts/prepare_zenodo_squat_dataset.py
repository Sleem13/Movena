"""Create image metadata for the manually downloaded Zenodo Squat Dataset."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)
DEFAULT_INPUT_DIR = Path("data/raw/zenodo_squat_dataset")
DEFAULT_OUTPUT_PATH = Path("data/processed/labels/zenodo_squat_dataset_labels.csv")
SOURCE_DATASET = "zenodo_squat_dataset"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
LABEL_MAP = {
    "good": "good",
    "bad_back": "bad_back",
    "bad_heel": "bad_heel",
}
OUTPUT_COLUMNS = [
    "source_dataset",
    "image_path",
    "label",
    "original_label",
    "filename",
    "file_extension",
    "image_width",
    "image_height",
    "file_size_bytes",
]


def normalize_folder_label(folder_name: str) -> str | None:
    """Map a source class folder to the stable PhysioVision label taxonomy."""
    key = "_".join(folder_name.strip().lower().replace("-", " ").split())
    return LABEL_MAP.get(key)


def infer_label(image_path: Path, input_dir: Path) -> tuple[str, str] | None:
    """Infer a supported label from the nearest labeled parent directory."""
    try:
        relative = image_path.relative_to(input_dir)
    except ValueError:
        relative = image_path

    for parent in reversed(relative.parents):
        if parent == Path("."):
            continue
        original = parent.name
        normalized = normalize_folder_label(original)
        if normalized:
            return normalized, original
    return None


def discover_images(input_dir: Path) -> list[Path]:
    """Return supported image files recursively, excluding placeholders."""
    if not input_dir.exists():
        return []
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def read_image_dimensions(image_path: Path) -> tuple[int, int]:
    """Read image width and height without loading the full image into memory."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required to inspect images. Install requirements-dev.txt first."
        ) from exc

    try:
        with Image.open(image_path) as image:
            width, height = image.size
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("Image cannot be decoded.") from exc
    return int(width), int(height)


def prepare_dataset(input_dir: Path, output_path: Path) -> Path:
    """Scan labeled image folders and write normalized metadata CSV."""
    images = discover_images(input_dir)
    if not images:
        raise FileNotFoundError(
            f"No supported images found under {input_dir}. Manually download and extract "
            "Dataset.zip into Good, Bad Back, and Bad Heel class folders first."
        )

    rows: list[dict[str, object]] = []
    skipped = 0
    for image_path in images:
        inferred = infer_label(image_path, input_dir)
        if inferred is None:
            LOGGER.warning("Skipping image outside a recognized class folder: %s", image_path)
            skipped += 1
            continue

        try:
            width, height = read_image_dimensions(image_path)
        except ValueError as exc:
            LOGGER.warning("Skipping unreadable image %s: %s", image_path, exc)
            skipped += 1
            continue

        label, original_label = inferred
        rows.append(
            {
                "source_dataset": SOURCE_DATASET,
                "image_path": str(image_path),
                "label": label,
                "original_label": original_label,
                "filename": image_path.name,
                "file_extension": image_path.suffix.lower(),
                "image_width": width,
                "image_height": height,
                "file_size_bytes": image_path.stat().st_size,
            }
        )

    if not rows:
        raise ValueError(
            "Images were found, but none were readable inside Good, Bad Back, or Bad Heel folders."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    LOGGER.info("Saved %s image records to %s (%s skipped)", len(rows), output_path, skipped)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Zenodo squat image metadata.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        output_path = prepare_dataset(args.input_dir, args.output)
    except Exception as exc:
        print(f"Zenodo squat dataset preparation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved Zenodo squat image metadata: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
