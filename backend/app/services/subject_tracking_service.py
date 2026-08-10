"""Fail-closed continuity checks for the single-subject pose pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Any


CORE_LANDMARKS = ("left_shoulder", "right_shoulder", "left_hip", "right_hip")


@dataclass(frozen=True)
class SubjectContinuityEvent:
    previous_frame: int
    current_frame: int
    timestamp_sec: float
    centroid_jump: float
    allowed_jump: float
    scale_ratio: float
    severe: bool
    reasons: tuple[str, ...]

    def detail(self) -> str:
        reason = " and ".join(self.reasons)
        return (
            f"Possible subject switch near {self.timestamp_sec:.2f}s "
            f"(frames {self.previous_frame}-{self.current_frame}; {reason})."
        )


@dataclass(frozen=True)
class SubjectContinuityReport:
    checked_transitions: int
    suspicious_events: tuple[SubjectContinuityEvent, ...] = field(default_factory=tuple)
    max_centroid_jump: float = 0.0
    max_scale_ratio: float = 1.0
    suspected_subject_switch: bool = False

    @property
    def severe_event_count(self) -> int:
        return sum(1 for event in self.suspicious_events if event.severe)

    def details(self, limit: int = 3) -> list[str]:
        return [event.detail() for event in self.suspicious_events[:limit]]


def _subject_signature(frame: dict[str, Any], min_visibility: float) -> tuple[float, float, float] | None:
    landmarks = frame.get("landmarks", {})
    points = [landmarks.get(name) for name in CORE_LANDMARKS]
    if any(point is None for point in points):
        return None
    if any(float(point.get("visibility", 0.0)) < min_visibility for point in points):
        return None

    xs = [float(point["x"]) for point in points]
    ys = [float(point["y"]) for point in points]
    centroid_x = sum(xs) / len(xs)
    centroid_y = sum(ys) / len(ys)
    scale = max(hypot(max(xs) - min(xs), max(ys) - min(ys)), 1e-6)
    return centroid_x, centroid_y, scale


def evaluate_subject_continuity(
    frames: list[dict[str, Any]],
    *,
    min_visibility: float = 0.5,
    max_centroid_jump: float = 0.16,
    severe_centroid_jump: float = 0.24,
    max_scale_ratio: float = 1.85,
    suspicious_event_limit: int = 2,
    max_tracking_gap_frames: int = 10,
) -> SubjectContinuityReport:
    """Detect implausible inter-frame pose changes that suggest identity switching.

    Coordinates are normalized to the video frame. The allowance grows slightly
    across short pose-detection gaps, while severe jumps still fail closed.
    """

    previous: tuple[dict[str, Any], tuple[float, float, float]] | None = None
    events: list[SubjectContinuityEvent] = []
    checked = 0
    max_jump = 0.0
    observed_max_scale_ratio = 1.0

    for frame in frames:
        signature = _subject_signature(frame, min_visibility)
        if signature is None:
            continue
        if previous is None:
            previous = (frame, signature)
            continue

        previous_frame, previous_signature = previous
        frame_gap = max(1, int(frame["frame_index"]) - int(previous_frame["frame_index"]))
        gap_allowance = min(max(frame_gap - 1, 0), max_tracking_gap_frames) * 0.015
        allowed_jump = max_centroid_jump + gap_allowance
        centroid_jump = hypot(
            signature[0] - previous_signature[0],
            signature[1] - previous_signature[1],
        )
        scale_ratio = max(signature[2], previous_signature[2]) / min(signature[2], previous_signature[2])
        checked += 1
        max_jump = max(max_jump, centroid_jump)
        observed_max_scale_ratio = max(observed_max_scale_ratio, scale_ratio)

        reasons: list[str] = []
        if centroid_jump > allowed_jump:
            reasons.append(f"pose center jumped {centroid_jump:.3f} frame widths")
        if scale_ratio > max_scale_ratio:
            reasons.append(f"body scale changed {scale_ratio:.2f}x")
        severe = centroid_jump > severe_centroid_jump or scale_ratio > max_scale_ratio
        if reasons:
            events.append(
                SubjectContinuityEvent(
                    previous_frame=int(previous_frame["frame_index"]),
                    current_frame=int(frame["frame_index"]),
                    timestamp_sec=float(frame.get("timestamp_sec", 0.0)),
                    centroid_jump=round(centroid_jump, 6),
                    allowed_jump=round(allowed_jump, 6),
                    scale_ratio=round(scale_ratio, 6),
                    severe=severe,
                    reasons=tuple(reasons),
                )
            )
        previous = (frame, signature)

    suspected = any(event.severe for event in events) or len(events) >= suspicious_event_limit
    return SubjectContinuityReport(
        checked_transitions=checked,
        suspicious_events=tuple(events),
        max_centroid_jump=round(max_jump, 6),
        max_scale_ratio=round(observed_max_scale_ratio, 6),
        suspected_subject_switch=suspected,
    )
