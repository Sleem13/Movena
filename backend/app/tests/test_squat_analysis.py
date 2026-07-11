import math

from app.services.squat_analysis_service import analyze_squat_landmarks


def point(x, y, visibility=0.95):
    return {"x": x, "y": y, "z": 0.0, "visibility": visibility}


def leg_points(knee_x, knee_y, knee_angle, side=1):
    length = 0.18
    hip = point(knee_x, knee_y - length)
    radians = math.radians(270 + (side * knee_angle))
    ankle = point(
        knee_x + (math.cos(radians) * length),
        knee_y + (math.sin(radians) * length),
    )
    return hip, point(knee_x, knee_y), ankle


def frame(knee_angle=170, knee_x_offset=0.0, shoulder_x_offset=0.0, low_confidence=False):
    visibility = 0.2 if low_confidence else 0.95
    left_hip, left_knee, left_ankle = leg_points(0.43 + knee_x_offset, 0.62, knee_angle, side=1)
    right_hip, right_knee, right_ankle = leg_points(0.57 - knee_x_offset, 0.62, knee_angle, side=-1)
    for landmark in [left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle]:
        landmark["visibility"] = visibility

    landmarks = {
        "left_shoulder": point(0.42 + shoulder_x_offset, 0.2, visibility),
        "right_shoulder": point(0.58 + shoulder_x_offset, 0.2, visibility),
        "left_hip": left_hip,
        "right_hip": right_hip,
        "left_knee": left_knee,
        "right_knee": right_knee,
        "left_ankle": left_ankle,
        "right_ankle": right_ankle,
    }
    return {
        "frame_index": 0,
        "landmarks": landmarks,
        "average_visibility": visibility,
        "low_confidence": low_confidence,
    }


def test_analyze_squat_counts_repetition_and_returns_report():
    frames = [
        frame(knee_angle=170),
        frame(knee_angle=140),
        frame(knee_angle=95),
        frame(knee_angle=140),
        frame(knee_angle=170),
    ]

    report = analyze_squat_landmarks(frames)

    assert report.exercise == "bodyweight_squat"
    assert report.status == "success"
    assert report.total_reps == 1
    assert report.movement_score >= 80
    assert report.average_knee_angle > 0
    assert report.feedback
    assert "licensed physiotherapist" in report.feedback[-1]


def test_analyze_squat_detects_poor_depth_when_no_depth_frames():
    frames = [frame(knee_angle=170), frame(knee_angle=145), frame(knee_angle=170)]

    report = analyze_squat_landmarks(frames)

    assert report.total_reps == 0
    assert "poor_depth" in report.detected_issues
    assert report.movement_score < 100


def test_analyze_squat_detects_trunk_lean_valgus_and_low_confidence():
    frames = [
        frame(knee_angle=95, knee_x_offset=0.08, shoulder_x_offset=0.35, low_confidence=True),
        frame(knee_angle=95, knee_x_offset=0.08, shoulder_x_offset=0.35, low_confidence=True),
        frame(knee_angle=170, knee_x_offset=0.08, shoulder_x_offset=0.35, low_confidence=True),
    ]
    for item in frames:
        landmarks = item["landmarks"]
        landmarks["left_hip"]["x"] = 0.43
        landmarks["left_ankle"]["x"] = 0.43
        landmarks["left_knee"]["x"] = 0.51
        landmarks["right_hip"]["x"] = 0.57
        landmarks["right_ankle"]["x"] = 0.57
        landmarks["right_knee"]["x"] = 0.49

    report = analyze_squat_landmarks(frames)

    assert "excessive_trunk_lean" in report.detected_issues
    assert "possible_knee_valgus" in report.detected_issues
    assert "low_landmark_confidence" in report.detected_issues
    assert 0 <= report.movement_score <= 100


def test_good_squat_does_not_produce_severe_movement_warnings():
    frames = [
        frame(knee_angle=170),
        frame(knee_angle=135),
        frame(knee_angle=95),
        frame(knee_angle=135),
        frame(knee_angle=170),
    ]

    report = analyze_squat_landmarks(frames)

    assert "poor_depth" not in report.detected_issues
    assert "excessive_trunk_lean" not in report.detected_issues
    assert "possible_knee_valgus" not in report.detected_issues
    assert 0 <= report.movement_score <= 100
