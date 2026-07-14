"""Fail closed when a sample modality does not match its processing pipeline."""

from __future__ import annotations

from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
SENSOR_EXTENSIONS = {".txt", ".tsv", ".mat"}
SKELETON_EXTENSIONS = {".npy", ".npz", ".pkl"}
ALLOWED_MODALITIES = {
    "video": {"video"},
    "mediapipe_pose": {"video", "image"},
    "sensor_timeseries": {"sensor_timeseries"},
    "skeleton": {"skeleton_csv"},
}


class IncompatibleModalityError(ValueError):
    pass


def infer_file_modality(path: Path | str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in SENSOR_EXTENSIONS:
        return "sensor_timeseries"
    if suffix in SKELETON_EXTENSIONS:
        return "skeleton_csv"
    return "unknown"


def ensure_pipeline_compatible(path: Path | str, pipeline: str, declared_modality: str | None = None) -> str:
    if pipeline not in ALLOWED_MODALITIES:
        raise ValueError(f"Unknown pipeline: {pipeline}")
    modality = declared_modality or infer_file_modality(path)
    if modality in {"mixed", "unknown", "missing"} or modality not in ALLOWED_MODALITIES[pipeline]:
        raise IncompatibleModalityError(
            f"Modality '{modality}' is not accepted by the '{pipeline}' pipeline."
        )
    return modality
