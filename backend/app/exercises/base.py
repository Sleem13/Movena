"""Shared interface for independently versioned rule-based exercise analyzers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ExerciseAnalyzer(ABC):
    exercise_id: str

    @abstractmethod
    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def count_reps(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def score_movement(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
