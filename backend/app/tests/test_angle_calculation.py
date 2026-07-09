from app.services.angle_calculation_service import (
    calculate_angle,
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_trunk_angle,
)


def test_calculate_angle_returns_right_angle():
    angle = calculate_angle((0, 0), (0, 1), (1, 1))

    assert angle == 90.0


def test_calculate_angle_handles_straight_line():
    angle = calculate_angle((0, 0), (1, 0), (2, 0))

    assert angle == 180.0


def test_calculate_knee_angle_uses_hip_knee_ankle_order():
    angle = calculate_knee_angle((0, 0), (0, 1), (1, 1))

    assert angle == 90.0


def test_calculate_hip_angle_uses_shoulder_hip_knee_order():
    angle = calculate_hip_angle((0, 0), (0, 1), (1, 1))

    assert angle == 90.0


def test_calculate_trunk_angle_relative_to_vertical():
    upright = calculate_trunk_angle({"x": 0.5, "y": 0.2}, {"x": 0.5, "y": 0.7})
    leaning = calculate_trunk_angle({"x": 0.8, "y": 0.2}, {"x": 0.5, "y": 0.7})

    assert upright == 0.0
    assert leaning > 25


def test_calculate_angle_handles_zero_length_vector():
    angle = calculate_angle((0, 0), (0, 0), (1, 1))

    assert angle == 0.0
