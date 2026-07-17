from __future__ import annotations

from pathlib import Path

from app.datasets.adapters.custom_videos_adapter import VIDEO_EXTENSIONS
from app.datasets.adapters.zenodo_squat_adapter import IMAGE_EXTENSIONS
from app.datasets.base_adapter import DatasetAdapter


class SquatKaggleAdapter(DatasetAdapter):
    dataset_name = "squat_kaggle"
    modality = "tabular_features"
    supported_modalities = ("video", "image", "tabular_features")
    requires_manual_mapping = True

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        supported = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | {".csv", ".parquet"}
        paths = sorted(item for item in self.source_path.rglob("*") if item.is_file() and item.suffix.lower() in supported)
        return self.apply_limit(paths, limit)

    def infer_modality(self, path: Path) -> str:
        if path.suffix.lower() in VIDEO_EXTENSIONS:
            return "video"
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            return "image"
        return "tabular_features"

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "bodyweight_squat", "unknown"

    def infer_exercises(self) -> list[str]:
        return ["bodyweight_squat"] if self.list_samples() else ["unknown"]

    def sample_notes(self, path: Path) -> str:
        return "Dataset identity is squat-related, but row-level class semantics and provenance require review."

    def is_compatible_with_current_pipeline(self) -> bool:
        # Reviewed row-level labels are required before current-app use.
        return False
