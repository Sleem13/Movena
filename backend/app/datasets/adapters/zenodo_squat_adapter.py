from __future__ import annotations

from pathlib import Path

from app.datasets.base_adapter import DatasetAdapter


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


class ZenodoSquatAdapter(DatasetAdapter):
    dataset_name = "zenodo_squat_dataset"
    modality = "image"
    supported_modalities = ("image",)
    requires_manual_mapping = True

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        paths = sorted(item for item in self.source_path.rglob("*") if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS)
        return self.apply_limit(paths, limit)

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "bodyweight_squat", raw_label.strip().lower().replace(" ", "_")

    def infer_exercises(self) -> list[str]:
        return ["bodyweight_squat"] if self.list_samples() else ["unknown"]

    def label_quality(self, raw_label: str, exercise_id: str, issue_label: str | None) -> str:
        return "medium"

    def sample_notes(self, path: Path) -> str:
        return "Squat exercise identity is clear; issue-folder mapping requires human approval. Static images are not suitable for rep counting."

    def is_compatible_with_current_pipeline(self) -> bool:
        # Useful for a separate image benchmark, not the temporal squat video model.
        return False
