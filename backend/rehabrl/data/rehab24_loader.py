"""Read-only adapter for Rehab24-6 motion-capture repetitions.

The source dataset remains outside this repository.  This module uses its 3D
joint geometry only to initialize simulated joint-angle state; source
correctness annotations are retained as metadata and are never used as a
clinical target or reward signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "video_id",
    "repetition_number",
    "exercise_id",
    "person_id",
    "first_frame",
    "last_frame",
    "mocap_erroneous",
    "correctness",
}

# Angle vertex and its two adjacent joints.
ANGLE_TRIPLETS = (
    (16, 0, 17),  # left hip
    (21, 0, 22),  # right hip
    (16, 17, 18),  # left knee
    (21, 22, 23),  # right knee
    (17, 18, 19),  # left ankle
    (22, 23, 24),  # right ankle
)


@dataclass(frozen=True)
class Rehab246Profile:
    """Geometry and provenance for one annotated exercise repetition."""

    source_id: str
    person_id: int
    exercise_id: int
    repetition_number: int
    correctness: bool
    joint_angles: np.ndarray


class Rehab246Loader:
    """Load validated Rehab24-6 repetition windows without copying raw data."""

    def __init__(self, raw_root: str | Path):
        supplied_root = Path(raw_root).expanduser().resolve()
        nested_root = supplied_root / "rehab24_6"
        self.root = nested_root if nested_root.is_dir() else supplied_root
        self.segmentation_path = self.root / "Segmentation.csv"
        self.joints_dir = self.root / "3d_joints"
        self._validate_layout()

        rows = pd.read_csv(self.segmentation_path, sep=";")
        missing = REQUIRED_COLUMNS.difference(rows.columns)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Rehab24-6 segmentation is missing columns: {names}")

        numeric_columns = [
            "repetition_number",
            "exercise_id",
            "person_id",
            "first_frame",
            "last_frame",
            "mocap_erroneous",
            "correctness",
        ]
        rows[numeric_columns] = rows[numeric_columns].apply(
            pd.to_numeric, errors="raise"
        )
        self.rows = rows.loc[rows["mocap_erroneous"] == 0].reset_index(drop=True)
        if self.rows.empty:
            raise ValueError("Rehab24-6 contains no usable mocap repetitions")

    def _validate_layout(self) -> None:
        if not self.segmentation_path.is_file():
            raise FileNotFoundError(
                f"Rehab24-6 segmentation not found: {self.segmentation_path}"
            )
        if not self.joints_dir.is_dir():
            raise FileNotFoundError(
                f"Rehab24-6 3D joint directory not found: {self.joints_dir}"
            )

    def __len__(self) -> int:
        return len(self.rows)

    def audit(self) -> dict[str, int]:
        """Return non-clinical inventory counts for provenance reporting."""
        return {
            "usable_repetitions": len(self.rows),
            "participants": int(self.rows["person_id"].nunique()),
            "exercises": int(self.rows["exercise_id"].nunique()),
            "correct_repetitions": int((self.rows["correctness"] == 1).sum()),
            "incorrect_repetitions": int((self.rows["correctness"] == 0).sum()),
        }

    def sample(self, rng: np.random.Generator) -> Rehab246Profile:
        """Sample one repetition and summarize its lower-limb joint angles."""
        index = int(rng.integers(0, len(self.rows)))
        return self.profile(index)

    def profile(self, index: int) -> Rehab246Profile:
        row = self.rows.iloc[index]
        source_id = str(row["video_id"])
        exercise_id = int(row["exercise_id"])
        recording_path = (
            self.joints_dir / f"Ex{exercise_id}" / f"{source_id}-120fps.npy"
        )
        if not recording_path.is_file():
            raise FileNotFoundError(
                f"3D joint recording referenced by segmentation is missing: "
                f"{recording_path}"
            )

        recording = np.load(recording_path, mmap_mode="r")
        if recording.ndim != 3 or recording.shape[1] < 25 or recording.shape[2] < 3:
            raise ValueError(
                f"Unexpected 3D joint shape {recording.shape} in {recording_path}"
            )

        first = max(0, int(row["first_frame"]))
        last_exclusive = min(len(recording), int(row["last_frame"]) + 1)
        if first >= last_exclusive:
            raise ValueError(
                f"Invalid frame window [{first}, {last_exclusive}) for {source_id}"
            )

        xyz = np.asarray(recording[first:last_exclusive, :, :3], dtype=np.float64)
        angles = np.array(
            [self._median_angle(xyz, *triplet) for triplet in ANGLE_TRIPLETS],
            dtype=np.float32,
        )
        normalized = np.clip(angles / 180.0, 0.0, 1.0)
        if not np.isfinite(normalized).all():
            raise ValueError(f"Non-finite joint angles in {recording_path}")

        return Rehab246Profile(
            source_id=source_id,
            person_id=int(row["person_id"]),
            exercise_id=exercise_id,
            repetition_number=int(row["repetition_number"]),
            correctness=bool(row["correctness"]),
            joint_angles=normalized,
        )

    @staticmethod
    def _median_angle(
        xyz: np.ndarray, first_joint: int, vertex_joint: int, third_joint: int
    ) -> float:
        first_vector = xyz[:, first_joint] - xyz[:, vertex_joint]
        second_vector = xyz[:, third_joint] - xyz[:, vertex_joint]
        denominator = np.linalg.norm(first_vector, axis=1) * np.linalg.norm(
            second_vector, axis=1
        )
        valid = denominator > np.finfo(np.float64).eps
        if not valid.any():
            raise ValueError("Cannot calculate an angle from zero-length joint vectors")
        cosine = np.sum(first_vector[valid] * second_vector[valid], axis=1)
        cosine = np.clip(cosine / denominator[valid], -1.0, 1.0)
        return float(np.nanmedian(np.degrees(np.arccos(cosine))))
