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
    supported_modalities = ("video",)

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        paths = sorted(item for item in self.source_path.rglob("*") if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS)
        return self.apply_limit(paths, limit)

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        label = raw_label.strip().lower().replace("-", "_").replace(" ", "_")
        return ("bodyweight_squat", label) if label in ISSUE_LABELS else ("unknown", "unknown")

    def is_compatible_with_current_pipeline(self) -> bool:
        return bool(self.list_samples())

    def infer_exercises(self) -> list[str]:
        exercises = {self.normalize_labels(path.parent.name)[0] for path in self.list_samples()}
        return sorted(exercise for exercise in exercises if exercise != "unknown") or ["unknown"]

    def label_quality(self, raw_label: str, exercise_id: str, issue_label: str | None) -> str:
        return "high" if raw_label.strip().lower().replace("-", "_").replace(" ", "_") in ISSUE_LABELS else "low"

    def sample_notes(self, path: Path) -> str:
        if path.parent.name not in ISSUE_LABELS:
            return "Folder label is not in the reviewed custom squat label set."
        return "Label comes from the reviewed custom-video folder convention."
