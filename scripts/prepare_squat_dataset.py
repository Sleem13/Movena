"""Prepare a locally downloaded Kaggle squat pose dataset.

TODO: Manually download the Kaggle squat dataset into data/raw/squat_kaggle/.
This script does not download data and does not use Kaggle credentials.
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

import pandas as pd


DEFAULT_INPUT_DIR = Path("data/raw/squat_kaggle")
DEFAULT_OUTPUT_DIR = Path("data/processed/features/squat_kaggle")
VALID_LABELS = {
    "correct",
    "incorrect",
    "shallow_depth",
    "knee_valgus",
    "excessive_trunk_lean",
    "unstable_balance",
    "fast_uncontrolled",
}
LABEL_ALIASES = {
    "good": "correct",
    "proper": "correct",
    "right": "correct",
    "bad": "incorrect",
    "wrong": "incorrect",
    "improper": "incorrect",
    "shallow": "shallow_depth",
    "depth": "shallow_depth",
    "valgus": "knee_valgus",
    "trunk": "excessive_trunk_lean",
    "lean": "excessive_trunk_lean",
    "unstable": "unstable_balance",
    "fast": "fast_uncontrolled",
}


def clean_column_name(column: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(column).strip().lower())
    return cleaned.strip("_")


def find_first_csv(input_dir: Path) -> Path:
    csv_files = sorted(input_dir.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {input_dir}. Manually download and extract the Kaggle dataset first."
        )
    return csv_files[0]


def detect_label_column(dataframe: pd.DataFrame) -> str:
    candidates = [
        "correctness_label",
        "label",
        "class",
        "target",
        "form",
        "squat_label",
        "issue",
    ]
    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate
    raise ValueError(
        "Could not find a label column. Expected one of: "
        + ", ".join(candidates)
    )


def normalize_label(value: object) -> str:
    raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if raw in VALID_LABELS:
        return raw
    if raw in {"0", "false", "no"}:
        return "incorrect"
    if raw in {"1", "true", "yes"}:
        return "correct"
    for key, mapped in LABEL_ALIASES.items():
        if key in raw:
            return mapped
    return "unknown"


def split_dataframe(
    dataframe: pd.DataFrame,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    seed: int = 42,
) -> dict[str, pd.DataFrame]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")
    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1.")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("train_ratio + validation_ratio must be less than 1.")

    indexes = list(dataframe.index)
    random.Random(seed).shuffle(indexes)
    train_end = int(len(indexes) * train_ratio)
    validation_end = train_end + int(len(indexes) * validation_ratio)

    return {
        "train": dataframe.loc[indexes[:train_end]].reset_index(drop=True),
        "validation": dataframe.loc[indexes[train_end:validation_end]].reset_index(drop=True),
        "test": dataframe.loc[indexes[validation_end:]].reset_index(drop=True),
    }


def prepare_dataset(input_path: Path, output_dir: Path) -> dict[str, Path]:
    dataframe = pd.read_csv(input_path)
    if dataframe.empty:
        raise ValueError(f"Dataset is empty: {input_path}")

    dataframe.columns = [clean_column_name(column) for column in dataframe.columns]
    label_column = detect_label_column(dataframe)
    dataframe["correctness_label"] = dataframe[label_column].map(normalize_label)
    unknown_count = int((dataframe["correctness_label"] == "unknown").sum())
    if unknown_count:
        raise ValueError(
            f"{unknown_count} rows have unknown labels. Review label mapping before training."
        )

    dataframe["source_dataset"] = dataframe.get("source_dataset", "squat_kaggle")
    dataframe["exercise_name"] = dataframe.get("exercise_name", "bodyweight_squat")

    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / "squat_kaggle_cleaned.csv"
    dataframe.to_csv(cleaned_path, index=False)

    output_paths = {"cleaned": cleaned_path}
    for split_name, split_frame in split_dataframe(dataframe).items():
        split_path = output_dir / f"squat_kaggle_{split_name}.csv"
        split_frame.to_csv(split_path, index=False)
        output_paths[split_name] = split_path

    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare local Kaggle squat dataset CSV files.")
    parser.add_argument("--input", type=Path, default=None, help="Specific Kaggle CSV file.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        input_path = args.input or find_first_csv(args.input_dir)
        output_paths = prepare_dataset(input_path, args.output_dir)
    except Exception as exc:
        print(f"Dataset preparation failed: {exc}", file=sys.stderr)
        return 1

    print("Prepared squat dataset:")
    for name, path in output_paths.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
