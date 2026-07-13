"""Backend-neutral contract for offline pose model benchmarking."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PoseBackendError(RuntimeError):
    """Raised when a backend cannot process an otherwise valid request."""


class PoseBackendUnavailableError(PoseBackendError):
    """Raised when an optional backend or its model assets are unavailable."""


@dataclass(frozen=True)
class PoseBackendResult:
    """Normalized result shared by all benchmark backends.

    Each frame uses the existing PhysioVision landmark dictionary shape so the
    rule-based analyzer can consume candidate outputs without being replaced.
    """

    backend_name: str
    expected_landmark_count: int
    processed_frames: int
    detected_frames: list[dict[str, Any]]
    source_fps: float
    runtime_sec: float


class BasePoseBackend(ABC):
    """Contract implemented by pretrained pose-estimation adapters."""

    name: str
    expected_landmark_count: int

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Return whether this backend can run in the active environment."""

    @abstractmethod
    def extract(self, video_path: Path) -> PoseBackendResult:
        """Extract normalized landmarks from a video."""
