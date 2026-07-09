"""Extract sliding-window features from processed UCI wearable-sensor data."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import pandas as pd


DEFAULT_INPUT_PATH = Path(
    "data/processed/sensor_features/uci_physical_therapy_exercises_processed.csv"
)
DEFAULT_OUTPUT_PATH = Path("data/processed/sensor_features/uci_sensor_window_features.csv")
METADATA_COLUMNS = {
    "source_dataset",
    "subject_id",
    "exercise_id",
    "execution_type",
    "split",
    "source_file",
    "sample_index",
}


def numeric_signal_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return numeric columns that are not metadata fields."""
    columns: list[str] = []
    for column in dataframe.columns:
        if column in METADATA_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(dataframe[column]):
            columns.append(column)
    return columns


def rms(series: pd.Series) -> float:
    """Calculate root mean square for a sensor signal."""
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return 0.0
    return math.sqrt(float((values**2).mean()))


def signal_energy(series: pd.Series) -> float:
    """Calculate sum-of-squares signal energy for a sensor signal."""
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return 0.0
    return float((values**2).sum())


def window_feature_row(
    window: pd.DataFrame,
    signal_columns: list[str],
    window_index: int,
    window_start: int,
    window_end: int,
) -> dict[str, object]:
    first = window.iloc[0]
    row: dict[str, object] = {
        "source_dataset": first["source_dataset"],
        "subject_id": first["subject_id"],
        "exercise_id": first["exercise_id"],
        "execution_type": first["execution_type"],
        "split": first["split"],
        "source_file": first["source_file"],
        "window_index": window_index,
        "window_start": window_start,
        "window_end": window_end,
    }

    for column in signal_columns:
        values = pd.to_numeric(window[column], errors="coerce").dropna()
        if values.empty:
            row[f"{column}_mean"] = 0.0
            row[f"{column}_std"] = 0.0
            row[f"{column}_min"] = 0.0
            row[f"{column}_max"] = 0.0
            row[f"{column}_median"] = 0.0
            row[f"{column}_energy"] = 0.0
            row[f"{column}_range"] = 0.0
            row[f"{column}_rms"] = 0.0
            continue

        row[f"{column}_mean"] = float(values.mean())
        row[f"{column}_std"] = float(values.std(ddof=0))
        row[f"{column}_min"] = float(values.min())
        row[f"{column}_max"] = float(values.max())
        row[f"{column}_median"] = float(values.median())
        row[f"{column}_energy"] = signal_energy(values)
        row[f"{column}_range"] = float(values.max() - values.min())
        row[f"{column}_rms"] = rms(values)

    return row


def extract_features(
    input_path: Path,
    output_path: Path,
    window_size: int = 50,
    step_size: int = 25,
) -> Path:
    """Create sliding-window time-series features from processed sensor rows."""
    if window_size <= 0:
        raise ValueError("window_size must be positive.")
    if step_size <= 0:
        raise ValueError("step_size must be positive.")
    if not input_path.exists():
        raise FileNotFoundError(f"Processed sensor file not found: {input_path}")

    dataframe = pd.read_csv(input_path)
    required = METADATA_COLUMNS
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing required sensor columns: {', '.join(sorted(missing))}")

    signals = numeric_signal_columns(dataframe)
    if not signals:
        raise ValueError("No numeric sensor signal columns found.")

    feature_rows: list[dict[str, object]] = []
    group_columns = ["source_file", "subject_id", "exercise_id", "execution_type", "split"]
    for _, group in dataframe.groupby(group_columns, dropna=False):
        group = group.sort_values("sample_index").reset_index(drop=True)
        if len(group) < window_size:
            continue

        window_index = 0
        for start in range(0, len(group) - window_size + 1, step_size):
            end = start + window_size
            window = group.iloc[start:end]
            feature_rows.append(
                window_feature_row(window, signals, window_index, start, end - 1)
            )
            window_index += 1

    if not feature_rows:
        raise ValueError(
            "No windows were created. Use a smaller --window-size or check the processed dataset."
        )

    features = pd.DataFrame(feature_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract sliding-window sensor features.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--window-size", type=int, default=50)
    parser.add_argument("--step-size", type=int, default=25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_path = extract_features(
            args.input,
            args.output,
            window_size=args.window_size,
            step_size=args.step_size,
        )
    except Exception as exc:
        print(f"Sensor feature extraction failed: {exc}", file=sys.stderr)
        return 1

    print(f"Saved sensor window features: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
