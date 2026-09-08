"""Validate the local Movena dataset folder structure."""

from __future__ import annotations

import argparse
from pathlib import Path


EXPECTED_DATA_DIRS = [
    "data/raw",
    "data/raw/custom_videos",
    "data/raw/custom_videos/squat_correct",
    "data/raw/custom_videos/squat_shallow_depth",
    "data/raw/custom_videos/squat_knee_valgus",
    "data/raw/custom_videos/squat_trunk_lean",
    "data/raw/custom_videos/squat_fast_uncontrolled",
    "data/augmented",
    "data/augmented/custom_videos",
    "data/augmented/custom_videos/squat_correct",
    "data/augmented/custom_videos/squat_shallow_depth",
    "data/augmented/custom_videos/squat_knee_valgus",
    "data/augmented/custom_videos/squat_trunk_lean",
    "data/augmented/custom_videos/squat_fast_uncontrolled",
    "data/raw/squat_kaggle",
    "data/raw/zenodo_squat_dataset",
    "data/raw/uci_physical_therapy_exercises",
    "data/raw/rehab24_6",
    "data/raw/uco_physical_rehab",
    "data/raw/dyntherapy",
    "data/raw/ui_prmd",
    "data/raw/kimore",
    "data/processed",
    "data/processed/pose_landmarks",
    "data/processed/pose_landmarks/zenodo_squat_dataset",
    "data/processed/angle_features",
    "data/processed/angle_features/zenodo_squat_dataset",
    "data/processed/sensor_features",
    "data/processed/merged_features",
    "data/processed/labels",
    "data/samples",
    "data/samples/squat_correct",
    "data/samples/squat_shallow_depth",
    "data/samples/squat_knee_valgus",
    "data/samples/squat_trunk_lean",
    "data/samples/squat_fast_uncontrolled",
]

RAW_DATASET_DIRS = [
    "data/raw/custom_videos",
    "data/augmented/custom_videos",
    "data/raw/squat_kaggle",
    "data/raw/zenodo_squat_dataset",
    "data/raw/uci_physical_therapy_exercises",
    "data/raw/rehab24_6",
    "data/raw/uco_physical_rehab",
    "data/raw/dyntherapy",
    "data/raw/ui_prmd",
    "data/raw/kimore",
]


def has_dataset_files(path: Path) -> bool:
    """Return True when a directory contains files other than .gitkeep."""
    if not path.exists():
        return False
    return any(item.is_file() and item.name != ".gitkeep" for item in path.rglob("*"))


def ensure_gitkeep(path: Path) -> None:
    """Create a .gitkeep file for empty dataset folders."""
    gitkeep = path / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


def check_structure(create: bool = False) -> int:
    """Print a dataset structure report and return a shell-friendly status code."""
    missing: list[Path] = []
    print("Movena dataset structure report")
    print("=" * 44)

    for directory in EXPECTED_DATA_DIRS:
        path = Path(directory)
        if path.exists():
            print(f"[ok]      {directory}")
            if create:
                ensure_gitkeep(path)
        else:
            missing.append(path)
            print(f"[missing] {directory}")
            if create:
                path.mkdir(parents=True, exist_ok=True)
                ensure_gitkeep(path)
                print(f"[created] {directory}")

    print("\nRaw dataset folder contents")
    print("=" * 44)
    for directory in RAW_DATASET_DIRS:
        path = Path(directory)
        if not path.exists():
            print(f"[missing] {directory}")
        elif has_dataset_files(path):
            print(f"[has files] {directory}")
        else:
            print(f"[empty]    {directory}")

    if missing and not create:
        print("\nWarning: missing folders found. Run with --create to create them.")
        return 1

    print("\nDataset folder validation complete.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Movena dataset folders.")
    parser.add_argument("--create", action="store_true", help="Create missing folders and .gitkeep files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return check_structure(create=args.create)


if __name__ == "__main__":
    raise SystemExit(main())
