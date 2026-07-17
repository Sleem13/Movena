"""Base contract for audited dataset-specific adapters.

Adapters discover and normalize metadata.  They deliberately do not decide that
a dataset is suitable for model promotion or that an exercise is supported by
the application.
"""

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

    requires_manual_mapping = False

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
            "requires_manual_mapping": self.requires_manual_mapping,
            "inferred_exercises": self.infer_exercises(),
        }

    def infer_exercises(self) -> list[str]:
        return ["unknown"]

    def load_annotations(self) -> dict[str, object]:
        return {}

    def infer_modality(self, path: Path) -> str:
        return self.modality

    def infer_participant_session(self, path: Path) -> tuple[str | None, str | None]:
        return None, None

    def label_quality(self, raw_label: str, exercise_id: str, issue_label: str | None) -> str:
        return "low" if exercise_id in {"", "unknown", None} else "medium"

    def sample_notes(self, path: Path) -> str:
        return ""

    def normalize_sample_metadata(self, path: Path) -> dict[str, object]:
        raw_label = path.parent.name
        exercise_id, issue_label = self.normalize_labels(raw_label)
        exercise_id = exercise_id or "unknown"
        issue_label = None if issue_label in {"", "unknown", None} else issue_label
        quality = self.label_quality(raw_label, exercise_id, issue_label)
        needs_review = self.requires_manual_mapping or exercise_id == "unknown" or quality != "high"
        participant_id, session_id = self.infer_participant_session(path)
        return {
            "sample_id": f"{self.dataset_name}:{path.as_posix()}", "dataset_name": self.dataset_name,
            "source_path": str(self.source_path), "file_path": str(path), "modality": self.infer_modality(path),
            "exercise_id": exercise_id, "raw_label": raw_label,
            "normalized_label": exercise_id, "issue_label": issue_label,
            "participant_id": participant_id, "session_id": session_id, "view_type": "unknown",
            "recording_quality": "unknown", "duration_sec": None, "fps": None, "frame_count": None,
            "has_manual_rep_count": False, "expected_reps": None, "split": "unassigned",
            "is_augmented": False, "adapter_name": type(self).__name__,
            "processing_status": "ready" if not needs_review else "needs_manual_mapping",
            "requires_manual_review": needs_review, "label_quality": quality,
            "notes": self.sample_notes(path),
        }

    def validate_sample(self, sample: dict[str, object]) -> tuple[bool, list[str]]:
        errors = []
        if sample.get("modality") in {"unknown", "mixed", "missing_or_incomplete"}: errors.append("modality_requires_review")
        if sample.get("exercise_id") == "unknown": errors.append("exercise_requires_review")
        return not errors, errors

    def export_unified_metadata(self, limit: int | None = None) -> list[dict[str, object]]:
        return [self.normalize_sample_metadata(path) for path in self.list_samples(limit=limit)]

    def is_compatible_with_pipeline(self, pipeline_name: str) -> bool:
        from app.datasets.modality_guard import check_modality_compatibility
        return check_modality_compatibility(self.modality, pipeline_name).allowed

    @abstractmethod
    def list_samples(self, limit: int | None = None) -> list[Path]:
        """List candidate sample files without loading them."""

    @staticmethod
    def apply_limit(paths: list[Path], limit: int | None) -> list[Path]:
        return paths if limit is None else paths[: max(0, limit)]

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
