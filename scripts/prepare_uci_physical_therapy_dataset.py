"""Prepare the local UCI Physical Therapy Exercises sensor dataset.

TODO: Manually download the dataset into data/raw/uci_physical_therapy_exercises/.
This script does not download UCI data and does not require external credentials.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


DEFAULT_INPUT_DIR = Path("data/raw/uci_physical_therapy_exercises")
DEFAULT_OUTPUT_PATH = Path(
    "data/processed/sensor_features/uci_physical_therapy_exercises_processed.csv"
)
SOURCE_DATASET = "uci_physical_therapy_exercises"
SUPPORTED_EXTENSIONS = {".csv", ".txt", ".data"}


def clean_column_name(column: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(column).strip().lower())
    return cleaned.strip("_") or "signal"


def has_header(path: Path) -> bool:
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                return bool(re.search(r"[A-Za-z]", stripped))
    return False


def discover_sensor_files(input_dir: Path) -> list[Path]:
    """Find local UCI sensor files without downloading anything."""
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def infer_path_metadata(path: Path, input_dir: Path) -> dict[str, str]:
    relative_parts = path.relative_to(input_dir).parts
    tokens = [part.lower() for part in relative_parts]
    joined = "_".join(tokens)

    subject_id = "unknown"
    exercise_id = "unknown"
    execution_type = "unknown"
    split = "unknown"

    for token in tokens:
        token_stem = Path(token).stem
        if re.fullmatch(r"s\d+", token_stem) or token_stem.startswith("subject"):
            subject_id = token_stem
        if re.fullmatch(r"e\d+", token_stem) or token_stem.startswith("exercise"):
            exercise_id = token_stem
        if token_stem in {"train", "training", "template"}:
            split = "train"
        elif token_stem in {"test", "testing"}:
            split = "test"

    if "correct" in joined:
        execution_type = "correct"
    elif "fast" in joined:
        execution_type = "fast"
    elif "low_amplitude" in joined or "low-amplitude" in joined or "lowamp" in joined:
        execution_type = "low_amplitude"
    else:
        execution_match = re.search(r"(?:^|[_\\/])(u\d+)(?:[_\\/.]|$)", joined)
        if execution_match:
            execution_code = execution_match.group(1)
            # TODO: Verify u-code label mapping against UCI Description.pdf before model training.
            execution_type = execution_code

    if split == "unknown":
        if "train" in joined or "template" in joined:
            split = "train"
        elif "test" in joined:
            split = "test"

    return {
        "subject_id": subject_id,
        "exercise_id": exercise_id,
        "execution_type": execution_type,
        "split": split,
        "source_file": str(path),
    }


def read_sensor_file(path: Path) -> pd.DataFrame:
    """Read comma, tab, semicolon, or whitespace-delimited sensor files."""
    header = 0 if has_header(path) else None
    try:
        dataframe = pd.read_csv(path, sep=None, engine="python", header=header)
    except Exception:
        dataframe = pd.read_csv(path, sep=r"\s+", engine="python", header=header)

    if dataframe.shape[1] == 1:
        dataframe = pd.read_csv(path, sep=r"\s+", engine="python", header=header)

    if header is None:
        dataframe.columns = [f"signal_{index:03d}" for index in range(dataframe.shape[1])]
    else:
        dataframe.columns = [clean_column_name(column) for column in dataframe.columns]

    dataframe = dataframe.dropna(axis=1, how="all")
    return dataframe


def prepare_file(path: Path, input_dir: Path) -> pd.DataFrame:
    dataframe = read_sensor_file(path)
    dataframe.columns = [clean_column_name(column) for column in dataframe.columns]
    dataframe.insert(0, "sample_index", range(len(dataframe)))

    metadata = infer_path_metadata(path, input_dir)
    dataframe["source_dataset"] = SOURCE_DATASET
    for column, value in metadata.items():
        dataframe[column] = value

    return dataframe


def validate_processed_sensor_data(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise ValueError("Processed UCI sensor dataframe is empty.")

    required_columns = [
        "source_dataset",
        "subject_id",
        "exercise_id",
        "execution_type",
        "split",
        "source_file",
        "sample_index",
    ]
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing required processed columns: {', '.join(missing)}")

    missing_values = dataframe.isna().sum()
    columns_with_missing = missing_values[missing_values > 0]
    if not columns_with_missing.empty:
        print("Warning: missing values detected after load:", file=sys.stderr)
        for column, count in columns_with_missing.items():
            print(f"- {column}: {count}", file=sys.stderr)
        dataframe.fillna(0, inplace=True)


def prepare_dataset(input_dir: Path, output_path: Path) -> Path:
    sensor_files = discover_sensor_files(input_dir)
    if not sensor_files:
        raise FileNotFoundError(
            f"No .txt, .csv, or .data files found under {input_dir}. Download the UCI dataset manually first."
        )

    frames = [prepare_file(path, input_dir) for path in sensor_files]
    processed = pd.concat(frames, ignore_index=True, sort=False)
    validate_processed_sensor_data(processed)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare local UCI Physical Therapy Exercises sensor files."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_path = prepare_dataset(args.input_dir, args.output)
    except Exception as exc:
        print(f"UCI dataset preparation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Saved processed UCI sensor data: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
