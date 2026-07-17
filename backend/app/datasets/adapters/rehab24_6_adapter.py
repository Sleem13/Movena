"""Mixed-modality discovery adapter for Rehab24-6."""

from __future__ import annotations

import re
from pathlib import Path

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


class Rehab246Adapter(ManualMappingAdapter):
    dataset_name = "rehab24_6"
    modality = "mixed"
    supported_modalities = ("video", "skeleton_2d", "skeleton_3d", "mixed")
    sample_extensions = frozenset(VIDEO_EXTENSIONS | {".npy"})

    def infer_modality(self, path: Path) -> str:
        lowered = {part.lower() for part in path.parts}
        if path.suffix.lower() in VIDEO_EXTENSIONS:
            return "video"
        if "2d_joints" in lowered or "2d_markers" in lowered:
            return "skeleton_2d"
        if "3d_joints" in lowered or "3d_markers" in lowered:
            return "skeleton_3d"
        return "mixed"

    def normalize_sample_metadata(self, path: Path) -> dict[str, object]:
        sample = super().normalize_sample_metadata(path)
        exercise_code = next((part for part in path.parts if re.fullmatch(r"Ex\d+", part, re.IGNORECASE)), "unknown")
        participant = re.search(r"(PM_\d+)", path.stem, re.IGNORECASE)
        sample["raw_label"] = exercise_code
        sample["participant_id"] = participant.group(1).upper() if participant else None
        sample["session_id"] = exercise_code if exercise_code != "unknown" else None
        sample["notes"] = "Modality is inferred from the verified folder/file type; Ex-code mapping remains pending."
        return sample

