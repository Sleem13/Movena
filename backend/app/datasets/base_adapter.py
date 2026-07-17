"""Base contract for audited dataset-specific adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path


class DatasetAdapter(ABC):
    dataset_name = "unknown"
    modality = "unknown"
    supported_modalities: tuple[str, ...] = ("unknown",)

    def __init__(self, source_path: Path | str):
        self.source_path = Path(source_path)

    def is_available(self) -> bool:
        return self.source_path.is_dir() and any(
            item.is_file() and item.name.lower() != ".gitkeep"
            for item in self.source_path.rglob("*")
        )

    def audit(self) -> dict[str, object]:
        samples = self.list_samples()
        return {
            "dataset_name": self.dataset_name,
            "source_path": str(self.source_path),
            "modality": self.modality,
            "available": self.is_available(),
            "sample_count": len(samples),
            "extension_counts": dict(Counter(path.suffix.lower() for path in samples)),
            "compatible_with_current_pipeline": self.is_compatible_with_current_pipeline(),
        }

    def infer_exercises(self) -> list[str]:
        return ["unknown"]

    def load_annotations(self) -> dict[str, object]:
        return {}

    def normalize_sample_metadata(self, path: Path) -> dict[str, object]:
        raw_label = path.parent.name
        exercise_id, issue_label = self.normalize_labels(raw_label)
        return {
            "sample_id": f"{self.dataset_name}:{path.as_posix()}", "dataset_name": self.dataset_name,
            "source_path": str(self.source_path), "file_path": str(path), "modality": self.modality,
            "exercise_id": exercise_id or "unknown", "raw_label": raw_label,
            "normalized_label": exercise_id or "unknown", "issue_label": issue_label or None,
            "participant_id": None, "session_id": None, "view_type": "unknown",
            "recording_quality": "unknown", "duration_sec": None, "fps": None, "frame_count": None,
            "has_manual_rep_count": False, "expected_reps": None, "split": "unassigned",
            "is_augmented": False, "adapter_name": type(self).__name__, "processing_status": "discovered",
            "requires_manual_review": exercise_id in {None, "unknown"}, "notes": "",
        }

    def validate_sample(self, sample: dict[str, object]) -> tuple[bool, list[str]]:
        errors = []
        if sample.get("modality") in {"unknown", "mixed", "missing_or_incomplete"}: errors.append("modality_requires_review")
        if sample.get("exercise_id") == "unknown": errors.append("exercise_requires_review")
        return not errors, errors

    def export_unified_metadata(self) -> list[dict[str, object]]:
        return [self.normalize_sample_metadata(path) for path in self.list_samples()]

    def is_compatible_with_pipeline(self, pipeline_name: str) -> bool:
        from app.datasets.modality_guard import check_modality_compatibility
        return check_modality_compatibility(self.modality, pipeline_name).allowed

    @abstractmethod
    def list_samples(self) -> list[Path]:
        """List candidate sample files without loading them."""

    def extract_metadata(self) -> list[dict[str, object]]:
        return [
            {
                "dataset_name": self.dataset_name,
                "sample_path": str(path),
                "raw_label": path.parent.name,
                "file_extension": path.suffix.lower(),
                "file_size_bytes": path.stat().st_size,
            }
            for path in self.list_samples()
        ]

    @abstractmethod
    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        """Return normalized exercise and issue labels, or unknown values."""

    @abstractmethod
    def is_compatible_with_current_pipeline(self) -> bool:
        """Return true only for explicitly supported squat-video inputs."""
