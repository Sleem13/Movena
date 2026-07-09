import math
from collections.abc import Mapping
from typing import TypeAlias

Point: TypeAlias = tuple[float, float] | tuple[float, float, float] | Mapping[str, float]


def _xy(point: Point) -> tuple[float, float]:
    if isinstance(point, Mapping):
        return float(point["x"]), float(point["y"])
    return float(point[0]), float(point[1])


def calculate_angle(point_a: Point, point_b: Point, point_c: Point) -> float:
    """Return the interior angle ABC in degrees."""
    ax, ay = _xy(point_a)
    bx, by = _xy(point_b)
    cx, cy = _xy(point_c)

    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)
    magnitude_ba = math.hypot(*ba)
    magnitude_bc = math.hypot(*bc)

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cosine = (ba[0] * bc[0] + ba[1] * bc[1]) / (magnitude_ba * magnitude_bc)
    cosine = max(-1.0, min(1.0, cosine))
    return round(math.degrees(math.acos(cosine)), 2)


def calculate_knee_angle(hip: Point, knee: Point, ankle: Point) -> float:
    return calculate_angle(hip, knee, ankle)


def calculate_hip_angle(shoulder: Point, hip: Point, knee: Point) -> float:
    return calculate_angle(shoulder, hip, knee)


def calculate_trunk_angle(shoulder: Point, hip: Point) -> float:
    """Return trunk lean relative to vertical in degrees."""
    shoulder_x, shoulder_y = _xy(shoulder)
    hip_x, hip_y = _xy(hip)
    vector_x = shoulder_x - hip_x
    vector_y = shoulder_y - hip_y
    magnitude = math.hypot(vector_x, vector_y)
    if magnitude == 0:
        return 0.0

    vertical_dot = abs(vector_y)
    cosine = max(-1.0, min(1.0, vertical_dot / magnitude))
    return round(math.degrees(math.acos(cosine)), 2)
