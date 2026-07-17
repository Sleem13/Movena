"""Join recognition metadata to existing lightweight processed feature tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = Path("data/processed/recognition/exercise_recognition_samples.csv")
DEFAULT_OUTPUT = Path("data/processed/recognition/exercise_recognition_features.csv")
DEFAULT_REPORT = Path("reports/model_reliability/exercise_recognition_feature_report.md")
TRACK_CHOICES = [
    "all", "video_pose_recognition", "skeleton_sequence_recognition",
    "sensor_timeseries_recognition", "image_pose_recognition", "tabular_feature_recognition",
]
FEATURE_SOURCES = {
    "video_pose_recognition": [
        Path("data/processed/features/squat_video_training_features_v2.csv"),
        Path("data/processed/features/squat_video_training_features.csv"),
        Path("data/processed/features/video_pose_features.csv"),
    ],
    "skeleton_sequence_recognition": [Path("data/processed/features/skeleton_sequence_features.csv")],
    "sensor_timeseries_recognition": [
        Path("data/processed/features/sensor_timeseries_features.csv"),
        Path("data/processed/features/sensor_features.csv"),
    ],
    "image_pose_recognition": [Path("data/processed/features/image_pose_features.csv")],
    "tabular_feature_recognition": [Path("data/processed/features/tabular_features.csv")],
}
METADATA_COLUMNS = {
    "sample_id", "dataset_name", "exercise_id", "recognition_track", "participant_id", "split",
    "file_path", "video_path", "source_dataset", "label", "feature_status", "training_ready",
    "raw_label", "normalized_label", "requires_manual_review", "label_quality",
}


def _canonical_path(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    path = Path(str(value))
    return str((path if path.is_absolute() else ROOT / path).resolve()).replace("\\", "/").lower()


def _load_source(track: str) -> tuple[pd.DataFrame | None, Path | None]:
    for path in FEATURE_SOURCES.get(track, []):
        if path.exists():
            return pd.read_csv(path), path
    return None, None


def build_recognition_features(
    samples_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    track: str = "all",
    limit: int | None = None,
    dry_run: bool = False,
) -> pd.DataFrame:
    samples = pd.read_csv(samples_path)
    if track != "all":
        samples = samples[samples["recognition_track"] == track]
    if limit is not None:
        samples = samples.head(max(0, limit))

    source_cache: dict[str, tuple[pd.DataFrame | None, Path | None]] = {}
    rows: list[dict[str, object]] = []
    feature_columns: set[str] = set()
    source_used: dict[str, str] = {}

    for sample in samples.to_dict("records"):
        sample_track = str(sample["recognition_track"])
        if sample_track not in source_cache:
            source_cache[sample_track] = _load_source(sample_track)
        source, source_path = source_cache[sample_track]
        matched: dict[str, object] | None = None
        if source is not None:
            source_used[sample_track] = str(source_path)
            if "sample_id" in source.columns:
                match = source[source["sample_id"].astype(str) == str(sample["sample_id"])]
            else:
                path_column = "video_path" if "video_path" in source.columns else "file_path" if "file_path" in source.columns else None
                match = source[source[path_column].map(_canonical_path) == _canonical_path(sample["file_path"])] if path_column else source.iloc[0:0]
            if not match.empty:
                matched = match.iloc[0].to_dict()

        row = {
            "sample_id": sample["sample_id"],
            "dataset_name": sample["dataset_name"],
            "exercise_id": sample["exercise_id"],
            "recognition_track": sample_track,
            "participant_id": sample.get("participant_id"),
            "split": sample.get("split", "unassigned"),
            "feature_status": "available_features" if matched else "missing_features",
        }
        if matched:
            for key, value in matched.items():
                if key not in METADATA_COLUMNS and isinstance(value, (int, float)) and not pd.isna(value):
                    row[key] = value
                    feature_columns.add(key)
        rows.append(row)

    base_columns = ["sample_id", "dataset_name", "exercise_id", "recognition_track", "participant_id", "split", "feature_status"]
    result = pd.DataFrame(rows)
    if result.empty:
        result = pd.DataFrame(columns=base_columns)
    else:
        result = result.reindex(columns=base_columns + sorted(feature_columns))

    available = int((result.feature_status == "available_features").sum()) if len(result) else 0
    report = (
        "# Exercise Recognition Feature Report\n\n"
        "Existing processed features are reused; raw videos are not reprocessed by this command.\n\n"
        f"- Requested track: {track}\n"
        f"- Rows inspected: {len(result)}\n"
        f"- Rows with features: {available}\n"
        f"- Missing feature rows: {len(result) - available}\n"
        f"- Numeric feature columns: {len(feature_columns)}\n"
        f"- Feature sources used: {source_used}\n"
        f"- Dry run: {dry_run}\n\n"
        "Missing features are reported rather than triggering expensive extraction.\n"
    )
    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--track", choices=TRACK_CHOICES, default="all")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = build_recognition_features(args.samples, args.output, args.report, track=args.track, limit=args.limit, dry_run=args.dry_run)
    available = int((result.feature_status == "available_features").sum()) if len(result) else 0
    print(f"Recognition feature rows: {len(result)}; available: {available}; dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

