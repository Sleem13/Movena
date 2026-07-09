from pathlib import Path
from typing import Any

import pandas as pd


UNIFIED_SCHEMA_COLUMNS = [
    "source_dataset",
    "subject_id",
    "session_id",
    "exercise_name",
    "video_path",
    "frame_index",
    "timestamp",
    "landmark_name",
    "x",
    "y",
    "z",
    "visibility",
    "left_knee_angle",
    "right_knee_angle",
    "left_hip_angle",
    "right_hip_angle",
    "trunk_angle",
    "rep_id",
    "phase",
    "correctness_label",
    "detected_issue",
    "quality_score",
]

REQUIRED_COLUMNS = [
    "source_dataset",
    "exercise_name",
    "frame_index",
    "landmark_name",
    "x",
    "y",
]

COLUMN_ALIASES = {
    "dataset": "source_dataset",
    "source": "source_dataset",
    "subject": "subject_id",
    "participant_id": "subject_id",
    "patient_id": "subject_id",
    "session": "session_id",
    "trial_id": "session_id",
    "exercise": "exercise_name",
    "activity": "exercise_name",
    "video": "video_path",
    "file_path": "video_path",
    "frame": "frame_index",
    "frame_id": "frame_index",
    "time": "timestamp",
    "landmark": "landmark_name",
    "joint": "landmark_name",
    "keypoint": "landmark_name",
    "visibility_score": "visibility",
    "confidence": "visibility",
    "label": "correctness_label",
    "class": "correctness_label",
    "issue": "detected_issue",
    "score": "quality_score",
}

NUMERIC_COLUMNS = [
    "frame_index",
    "timestamp",
    "x",
    "y",
    "z",
    "visibility",
    "left_knee_angle",
    "right_knee_angle",
    "left_hip_angle",
    "right_hip_angle",
    "trunk_angle",
    "rep_id",
    "quality_score",
]


class DatasetSchemaError(ValueError):
    pass


def _clean_column_name(column: str) -> str:
    cleaned = (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
    )
    return COLUMN_ALIASES.get(cleaned, cleaned)


def _read_json(path: Path) -> pd.DataFrame:
    try:
        return pd.read_json(path)
    except ValueError:
        return pd.read_json(path, lines=True)


def load_landmark_file(path: str | Path) -> pd.DataFrame:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {source_path}")

    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source_path)
    if suffix == ".json":
        return _read_json(source_path)

    raise DatasetSchemaError(f"Unsupported dataset file type: {suffix}")


def normalize_landmark_dataframe(
    dataframe: pd.DataFrame,
    *,
    source_dataset: str | None = None,
    exercise_name: str | None = None,
    video_path: str | None = None,
) -> pd.DataFrame:
    if dataframe.empty:
        raise DatasetSchemaError("Dataset file is empty.")

    normalized = dataframe.copy()
    normalized.columns = [_clean_column_name(column) for column in normalized.columns]

    defaults: dict[str, Any] = {
        "source_dataset": source_dataset or "unknown",
        "subject_id": "unknown",
        "session_id": "unknown",
        "exercise_name": exercise_name or "unknown",
        "video_path": video_path or "",
        "timestamp": pd.NA,
        "z": 0.0,
        "visibility": 1.0,
        "left_knee_angle": pd.NA,
        "right_knee_angle": pd.NA,
        "left_hip_angle": pd.NA,
        "right_hip_angle": pd.NA,
        "trunk_angle": pd.NA,
        "rep_id": pd.NA,
        "phase": "unknown",
        "correctness_label": "unlabeled",
        "detected_issue": "",
        "quality_score": pd.NA,
    }

    for column, default_value in defaults.items():
        if column not in normalized.columns:
            normalized[column] = default_value
        elif default_value is not pd.NA:
            normalized[column] = normalized[column].fillna(default_value)

    missing_required = [column for column in REQUIRED_COLUMNS if column not in normalized.columns]
    if missing_required:
        raise DatasetSchemaError(
            f"Missing required columns after normalization: {', '.join(missing_required)}"
        )

    for column in NUMERIC_COLUMNS:
        if column in normalized.columns:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized["frame_index"] = normalized["frame_index"].fillna(0).astype(int)
    normalized["x"] = normalized["x"].fillna(0.0)
    normalized["y"] = normalized["y"].fillna(0.0)
    normalized["z"] = normalized["z"].fillna(0.0)
    normalized["visibility"] = normalized["visibility"].fillna(0.0).clip(0.0, 1.0)

    text_columns = [
        "source_dataset",
        "subject_id",
        "session_id",
        "exercise_name",
        "video_path",
        "landmark_name",
        "phase",
        "correctness_label",
        "detected_issue",
    ]
    for column in text_columns:
        normalized[column] = normalized[column].fillna("").astype(str)

    extra_columns = [column for column in normalized.columns if column not in UNIFIED_SCHEMA_COLUMNS]
    ordered_columns = UNIFIED_SCHEMA_COLUMNS + extra_columns
    return normalized[ordered_columns]


def validate_unified_schema(dataframe: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        raise DatasetSchemaError(f"Missing required columns: {', '.join(missing)}")

    invalid_coordinates = dataframe[["x", "y"]].isna().any(axis=1)
    if invalid_coordinates.any():
        count = int(invalid_coordinates.sum())
        raise DatasetSchemaError(f"{count} rows have missing x/y coordinates.")


def save_processed_dataframe(
    dataframe: pd.DataFrame,
    output_path: str | Path = Path("data/processed/landmarks/unified_landmarks.csv"),
) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(destination, index=False)
    return destination


def load_and_normalize_dataset(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    source_dataset: str | None = None,
    exercise_name: str | None = None,
    video_path: str | None = None,
) -> pd.DataFrame:
    dataframe = load_landmark_file(input_path)
    normalized = normalize_landmark_dataframe(
        dataframe,
        source_dataset=source_dataset,
        exercise_name=exercise_name,
        video_path=video_path,
    )
    validate_unified_schema(normalized)

    if output_path:
        save_processed_dataframe(normalized, output_path)

    return normalized
