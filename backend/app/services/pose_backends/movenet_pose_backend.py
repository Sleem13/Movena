"""Deferred MoveNet adapter preserving a stable benchmark interface."""

from importlib.util import find_spec
from pathlib import Path

from app.services.pose_backends.base_pose_backend import (
    BasePoseBackend,
    PoseBackendResult,
    PoseBackendUnavailableError,
)


class MoveNetPoseBackend(BasePoseBackend):
    """Placeholder for MoveNet; heavy TensorFlow dependencies remain optional."""

    expected_landmark_count = 17

    def __init__(self, variant: str = "lightning") -> None:
        normalized = variant.strip().lower()
        if normalized not in {"lightning", "thunder"}:
            raise ValueError("MoveNet variant must be 'lightning' or 'thunder'.")
        self.variant = normalized
        self.name = f"movenet_{normalized}"

    @classmethod
    def is_available(cls) -> bool:
        return False

    def extract(self, video_path: Path) -> PoseBackendResult:
        dependency_hint = (
            " TensorFlow is not installed."
            if find_spec("tensorflow") is None
            else " TensorFlow is present, but the reviewed adapter is deferred."
        )
        raise PoseBackendUnavailableError(
            f"{self.name} is a benchmark placeholder and is not enabled.{dependency_hint} "
            "See docs/pretrained_pose_model_strategy.md."
        )
