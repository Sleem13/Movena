"""Compare the legacy threshold counter with the hardened state machine."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.rep_counting_service import count_squat_reps  # noqa: E402


def legacy_count(values: list[float]) -> int:
    reps = 0
    state = "standing"
    for angle in values:
        if state == "standing" and angle < 110:
            state = "depth"
        elif state == "depth" and angle > 160:
            reps += 1
            state = "standing"
    return reps


def main() -> int:
    path = REPO_ROOT / "data/processed/angle_features/custom_squat_videos_angle_features.csv"
    if not path.exists():
        print(f"Angle feature CSV not found: {path}")
        return 1
    data = pd.read_csv(path)
    print("label|video|legacy_reps|hardened_reps|ignored_partial_reps|rep_count_confidence")
    for (label, video_path), group in data.groupby(["label", "video_path"], sort=True):
        angles = ((group["left_knee_angle"] + group["right_knee_angle"]) / 2).tolist()
        result = count_squat_reps(
            angles,
            group["timestamp_sec"].tolist(),
            group["frame_index"].astype(int).tolist(),
        )
        print(
            f"{label}|{video_path}|{legacy_count(angles)}|{result.total_reps}|"
            f"{result.ignored_partial_reps}|{result.confidence:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
