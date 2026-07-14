from __future__ import annotations

from pathlib import Path

from app.datasets.base_adapter import DatasetAdapter


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ISSUE_LABELS = {
    "squat_correct", "squat_knee_valgus", "squat_shallow_depth",
    "squat_trunk_lean", "squat_fast_uncontrolled",
}


class CustomVideosAdapter(DatasetAdapter):
    dataset_name = "custom_videos"
    modality = "video"

    def list_samples(self) -> list[Path]:
        if not self.source_path.exists():
            return []
        return sorted(item for item in self.source_path.rglob("*") if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS)

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        label = raw_label.strip().lower().replace("-", "_").replace(" ", "_")
        return ("bodyweight_squat", label) if label in ISSUE_LABELS else ("unknown", "unknown")

    def is_compatible_with_current_pipeline(self) -> bool:
        return bool(self.list_samples())

