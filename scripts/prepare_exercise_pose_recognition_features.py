"""Build the versioned 40-feature exercise-pose recognition table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.datasets.adapters.exercise_pose_frames_adapter import LABEL_MAP  # noqa: E402
from app.ml.exercise_pose_features import KEYPOINT_COUNT, extract_pose_features, feature_columns  # noqa: E402


REQUIRED_COLUMNS = {
    "workout_type", "video_name",
    *(f"joint_{index}_{axis}" for index in range(KEYPOINT_COUNT) for axis in ("x", "y", "conf")),
}


def build_features(source: Path, output: Path | None = None) -> tuple[pd.DataFrame, dict[str, object]]:
    raw = pd.read_csv(source)
    missing = sorted(REQUIRED_COLUMNS - set(raw.columns))
    if missing:
        raise ValueError(f"Pose frame table is missing required columns: {', '.join(missing[:10])}")

    records: list[dict[str, object]] = []
    rejected = 0
    for row_index, row in raw.iterrows():
        raw_label = str(row.workout_type).strip().lower()
        exercise_id = LABEL_MAP.get(raw_label)
        if exercise_id is None:
            rejected += 1
            continue
        xy = np.asarray([[row[f"joint_{index}_x"], row[f"joint_{index}_y"]] for index in range(KEYPOINT_COUNT)])
        confidence = np.asarray([row[f"joint_{index}_conf"] for index in range(KEYPOINT_COUNT)])
        features = extract_pose_features(xy, confidence)
        if features is None:
            rejected += 1
            continue
        records.append({
            "sample_id": f"{row.video_name}:{row_index}",
            "dataset_name": "exercise_pose_frames",
            "exercise_id": exercise_id,
            "recognition_track": "video_pose_recognition",
            "participant_id": None,
            "group_id": str(row.video_name),
            "split": "unassigned",
            "feature_status": "available_features",
            "label": raw_label,
            "file_path": "",
            **features,
        })
    result = pd.DataFrame(records)
    ordered = [
        "sample_id", "dataset_name", "exercise_id", "recognition_track", "participant_id",
        "group_id", "split", "feature_status", "label", "file_path", *feature_columns(),
    ]
    result = result.reindex(columns=ordered)
    summary = {
        "source_rows": len(raw),
        "feature_rows": len(result),
        "rejected_rows": rejected,
        "source_unique_videos": int(raw.video_name.nunique()),
        "feature_unique_videos": int(result.group_id.nunique()),
        "class_counts": result.exercise_id.value_counts().sort_index().to_dict(),
        "feature_count": len(feature_columns()),
        "participant_ids_available": False,
        "status": "candidate_features",
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output, index=False)
        output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return result, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/processed/recognition/exercise_pose_features.csv"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    _, summary = build_features(args.source, None if args.dry_run else args.output)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
