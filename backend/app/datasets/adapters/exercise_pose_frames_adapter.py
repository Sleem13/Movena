"""Conservative adapter for externally stored exercise-pose frame tables."""

from __future__ import annotations

import csv
from pathlib import Path

from app.datasets.base_adapter import DatasetAdapter


LABEL_MAP = {
    "squat": "bodyweight_squat",
    "push-up": "push_up",
    "shoulder press": "shoulder_press",
    "hammer curl": "hammer_curl",
    "barbell biceps curl": "bicep_curl",
}


class ExercisePoseFramesAdapter(DatasetAdapter):
    dataset_name = "exercise_pose_frames"
    modality = "skeleton_2d"
    supported_modalities = ("skeleton_2d", "tabular_features")
    requires_manual_mapping = True

    def is_available(self) -> bool:
        return self.source_path.is_file() and self.source_path.suffix.lower() == ".csv"

    def list_samples(self, limit: int | None = None) -> list[Path]:
        paths = [self.source_path] if self.is_available() else []
        return self.apply_limit(paths, limit)

    def load_annotations(self) -> dict[str, object]:
        if not self.is_available():
            return {"row_count": 0, "labels": {}, "video_count": 0}
        labels: dict[str, int] = {}
        videos: set[str] = set()
        row_count = 0
        with self.source_path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            for row in reader:
                row_count += 1
                raw_label = str(row.get("workout_type", "")).strip().lower()
                labels[raw_label] = labels.get(raw_label, 0) + 1
                if row.get("video_name"):
                    videos.add(str(row["video_name"]))
        return {"row_count": row_count, "labels": labels, "video_count": len(videos)}

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return LABEL_MAP.get(raw_label.strip().lower(), "unknown"), "unknown"

    def infer_exercises(self) -> list[str]:
        if not self.is_available():
            return ["unknown"]
        return sorted({LABEL_MAP.get(label, "unknown") for label in self.load_annotations()["labels"]})

    def normalize_sample_metadata(self, path: Path) -> dict[str, object]:
        annotations = self.load_annotations()
        return {
            "sample_id": f"{self.dataset_name}:{path.name}",
            "dataset_name": self.dataset_name,
            "source_path": str(path),
            "file_path": str(path),
            "modality": self.modality,
            "exercise_id": "multi_exercise_recognition",
            "raw_label": "multiple",
            "normalized_label": "multi_exercise_recognition",
            "issue_label": None,
            "participant_id": None,
            "session_id": None,
            "view_type": "unknown",
            "recording_quality": "unknown",
            "duration_sec": None,
            "fps": None,
            "frame_count": annotations["row_count"],
            "has_manual_rep_count": False,
            "expected_reps": None,
            "split": "unassigned",
            "is_augmented": False,
            "adapter_name": type(self).__name__,
            "processing_status": "needs_manual_mapping",
            "requires_manual_review": True,
            "label_quality": "medium",
            "notes": "Frame labels are mapped, but participant identity, source provenance, view, and licensing require review.",
        }

    def is_compatible_with_current_pipeline(self) -> bool:
        return False

