"""Optional pose-estimation backends used by offline benchmarks."""

from app.services.pose_backends.base_pose_backend import (
    BasePoseBackend,
    PoseBackendError,
    PoseBackendResult,
    PoseBackendUnavailableError,
)
from app.services.pose_backends.mediapipe_pose_backend import MediaPipePoseBackend
from app.services.pose_backends.movenet_pose_backend import MoveNetPoseBackend


def create_pose_backend(name: str) -> BasePoseBackend:
    """Build a benchmark backend without changing the production API backend."""
    normalized = name.strip().lower().replace("-", "_")
    if normalized in {"mediapipe", "blazepose"}:
        return MediaPipePoseBackend()
    if normalized in {"movenet_lightning", "lightning"}:
        return MoveNetPoseBackend("lightning")
    if normalized in {"movenet_thunder", "thunder"}:
        return MoveNetPoseBackend("thunder")
    raise ValueError(
        f"Unknown pose backend '{name}'. Choose mediapipe, movenet_lightning, or movenet_thunder."
    )


__all__ = [
    "BasePoseBackend",
    "MediaPipePoseBackend",
    "MoveNetPoseBackend",
    "PoseBackendResult",
    "PoseBackendError",
    "PoseBackendUnavailableError",
    "create_pose_backend",
]
