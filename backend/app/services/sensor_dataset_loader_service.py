from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SENSOR_FEATURES_PATH = Path(
    REPO_ROOT / "data/processed/sensor_features/uci_sensor_window_features.csv"
)

REQUIRED_SENSOR_METADATA_COLUMNS = [
    "source_dataset",
    "subject_id",
    "exercise_id",
    "execution_type",
    "split",
]

REQUIRED_WINDOW_COLUMNS = [
    "window_index",
    "window_start",
    "window_end",
]

NON_FEATURE_COLUMNS = set(
    REQUIRED_SENSOR_METADATA_COLUMNS
    + REQUIRED_WINDOW_COLUMNS
    + [
        "source_file",
        "sample_index",
        "timestamp",
    ]
)


class SensorDatasetSchemaError(ValueError):
    pass


def clean_sensor_column_name(column: str) -> str:
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("/", "_")
    )


def load_sensor_features(path: str | Path = DEFAULT_SENSOR_FEATURES_PATH) -> pd.DataFrame:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Sensor feature file not found: {source_path}")

    dataframe = pd.read_csv(source_path)
    dataframe.columns = [clean_sensor_column_name(column) for column in dataframe.columns]
    validate_sensor_features(dataframe)
    return dataframe


def validate_sensor_features(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise SensorDatasetSchemaError("Sensor feature dataframe is empty.")

    required_columns = REQUIRED_SENSOR_METADATA_COLUMNS + REQUIRED_WINDOW_COLUMNS
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        raise SensorDatasetSchemaError(
            f"Missing required sensor feature columns: {', '.join(missing)}"
        )

    feature_columns = get_sensor_feature_columns(dataframe)
    if not feature_columns:
        raise SensorDatasetSchemaError("No numeric sensor feature columns found.")

    missing_values = dataframe[feature_columns].isna().sum()
    columns_with_missing = missing_values[missing_values > 0]
    if not columns_with_missing.empty:
        details = ", ".join(
            f"{column}={count}" for column, count in columns_with_missing.items()
        )
        raise SensorDatasetSchemaError(f"Sensor feature columns contain missing values: {details}")


def get_sensor_feature_columns(dataframe: pd.DataFrame) -> list[str]:
    feature_columns: list[str] = []
    for column in dataframe.columns:
        if column in NON_FEATURE_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(dataframe[column]):
            feature_columns.append(column)
    return feature_columns


def load_sensor_training_data(
    path: str | Path = DEFAULT_SENSOR_FEATURES_PATH,
    target_column: str = "execution_type",
) -> tuple[pd.DataFrame, pd.Series]:
    dataframe = load_sensor_features(path)
    if target_column not in dataframe.columns:
        raise SensorDatasetSchemaError(f"Target column not found: {target_column}")

    feature_columns = get_sensor_feature_columns(dataframe)
    features = dataframe[feature_columns].copy()
    target = dataframe[target_column].copy()
    return features, target
