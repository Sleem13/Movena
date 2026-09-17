"""Unpromoted pose/signal primitives. Never connected to patient-facing analysis.

Task thresholds must come from a versioned, reviewed protocol. This module has
no default clinical thresholds, treatment feedback or movement-quality score.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import acos, degrees, isfinite, sqrt
from typing import Literal, Sequence

ENGINE_VERSION = 'recovery-primitives-2.0.0-experimental'


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    z: float
    visibility: float


@dataclass(frozen=True)
class PoseFrame:
    timestamp: float
    landmarks: Sequence[Landmark | None]


@dataclass(frozen=True)
class CycleProtocol:
    protocol_version: str
    low: float
    high: float
    dwell_seconds: float
    min_cycle_seconds: float
    max_cycle_seconds: float
    max_frame_gap_seconds: float
    min_visibility: float
    max_missing_fraction: float
    min_duration_seconds: float
    direction: Literal['low_high_low', 'high_low_high']

    def __post_init__(self):
        values = (self.low, self.high, self.dwell_seconds, self.min_cycle_seconds,
                  self.max_cycle_seconds, self.max_frame_gap_seconds, self.min_visibility,
                  self.max_missing_fraction, self.min_duration_seconds)
        if (not self.protocol_version or not all(isfinite(x) for x in values)
            or not 0 <= self.low < self.high <= 180 or self.dwell_seconds <= 0
            or not 0 < self.min_cycle_seconds < self.max_cycle_seconds
            or self.max_frame_gap_seconds <= 0 or not 0 <= self.min_visibility <= 1
            or not 0 <= self.max_missing_fraction < 1 or self.min_duration_seconds <= 0
            or self.direction not in {'low_high_low', 'high_low_high'}):
            raise ValueError('Invalid cycle protocol')


def angle(frame: PoseFrame, triplet: tuple[int, int, int], *, min_visibility: float,
          coordinate_space: Literal['world', 'image'], image_size: tuple[int, int] | None = None) -> float | None:
    """Return a 3D world angle or aspect-corrected 2D image angle, never mixed.

    An invisible/degenerate/nonfinite landmark is unavailable, not angle zero.
    Image depth is deliberately excluded; normalized z is not a measured depth.
    """
    if len(frame.landmarks) != 33 or len(set(triplet)) != 3 or any(not 0 <= i < 33 for i in triplet):
        raise ValueError('Expected 33 landmarks and three distinct landmark indices')
    if coordinate_space not in {'world', 'image'} or not 0 <= min_visibility <= 1:
        raise ValueError('Explicit coordinate space and bounded visibility are required')
    if coordinate_space == 'image' and (image_size is None or len(image_size) != 2
                                      or any(not isfinite(v) or v <= 0 for v in image_size)):
        raise ValueError('Image coordinates require positive source dimensions')
    points = [frame.landmarks[i] for i in triplet]
    if any(p is None or not all(isfinite(v) for v in (p.x, p.y, p.z, p.visibility))
           or not min_visibility <= p.visibility <= 1 for p in points):
        return None
    coordinates = [(p.x, p.y, p.z) if coordinate_space == 'world'
                   else (p.x * image_size[0], p.y * image_size[1], 0.) for p in points]
    first, vertex, last = coordinates
    a, b = [x-y for x,y in zip(first,vertex)], [x-y for x,y in zip(last,vertex)]
    norm = sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    if not isfinite(norm) or norm <= 1e-12:
        return None
    cosine = sum(x*y for x,y in zip(a,b)) / norm
    return degrees(acos(max(-1., min(1., cosine))))


class CycleCounter:
    """Streaming hysteresis with stable endpoint dwell and complete return cycles."""
    def __init__(self, protocol: CycleProtocol):
        self.protocol = protocol
        self.count = 0
        self.last_timestamp: float | None = None
        self.reset_phase()

    def reset_phase(self):
        self.phase = 'start'
        self.candidate_since: float | None = None
        self.cycle_started: float | None = None

    def step(self, timestamp: float, value: float | None) -> None:
        if not isfinite(timestamp) or (self.last_timestamp is not None and timestamp <= self.last_timestamp):
            raise ValueError('Timestamps must be finite and strictly increasing')
        if self.last_timestamp is not None and timestamp-self.last_timestamp > self.protocol.max_frame_gap_seconds:
            self.reset_phase()
        self.last_timestamp = timestamp
        if value is None or not isfinite(value):
            self.reset_phase()
            return
        if not 0 <= value <= 180:
            raise ValueError('Angle outside supported range')
        p = self.protocol
        start = value <= p.low if p.direction == 'low_high_low' else value >= p.high
        opposite = value >= p.high if p.direction == 'low_high_low' else value <= p.low
        if self.cycle_started is not None and timestamp-self.cycle_started > p.max_cycle_seconds:
            self.reset_phase()
        target = opposite if self.phase == 'opposite' else start
        if not target:
            self.candidate_since = None
            return
        if self.candidate_since is None:
            self.candidate_since = timestamp
        if timestamp-self.candidate_since + 1e-9 < p.dwell_seconds:
            return
        if self.phase == 'start':
            self.cycle_started = self.candidate_since
            self.phase = 'opposite'
        elif self.phase == 'opposite':
            self.phase = 'return'
        else:
            duration = timestamp-self.cycle_started
            if p.min_cycle_seconds <= duration <= p.max_cycle_seconds:
                self.count += 1
            # Re-use the stable return as the start of a possible next cycle.
            self.cycle_started = self.candidate_since
            self.phase = 'opposite'
        self.candidate_since = None


@dataclass(frozen=True)
class SignalResult:
    status: Literal['success', 'rejected', 'error']
    repetition_count: int | None
    reason_codes: tuple[str, ...]
    protocol_version: str
    duration_seconds: float | None
    missing_fraction: float | None
    engine_version: str = ENGINE_VERSION
    model_version: str | None = None
    quality_score: float | None = None


def process(frames: Sequence[PoseFrame], triplet: tuple[int,int,int], protocol: CycleProtocol,
            *, coordinate_space: Literal['world','image'], image_size: tuple[int,int] | None = None) -> SignalResult:
    """Research-only measurement; `success` is signal acceptance, not clinical validity."""
    counter = CycleCounter(protocol)
    missing = 0
    gaps = False
    previous = None
    try:
        for frame in frames:
            value = angle(frame,triplet,min_visibility=protocol.min_visibility,
                          coordinate_space=coordinate_space,image_size=image_size)
            if previous is not None and frame.timestamp-previous > protocol.max_frame_gap_seconds:
                gaps = True
            counter.step(frame.timestamp,value)
            previous = frame.timestamp
            missing += value is None
    except (ValueError, TypeError, AttributeError, IndexError):
        return SignalResult('error',None,('INVALID_POSE_INPUT',),protocol.protocol_version,None,None)
    if len(frames) < 2:
        return SignalResult('rejected',None,('INSUFFICIENT_DURATION',),protocol.protocol_version,None,None)
    duration = frames[-1].timestamp-frames[0].timestamp
    fraction = missing / len(frames)
    reasons = []
    if duration < protocol.min_duration_seconds:
        reasons.append('INSUFFICIENT_DURATION')
    if fraction > protocol.max_missing_fraction:
        reasons.append('INSUFFICIENT_VISIBILITY')
    if gaps:
        reasons.append('INTERRUPTED_TRACKING')
    return SignalResult('rejected' if reasons else 'success',None if reasons else counter.count,
                        tuple(reasons),protocol.protocol_version,duration,fraction)
