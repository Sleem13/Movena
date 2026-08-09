import math

from app.exercises.upper_body_cyclic import (
    PUSH_UP_CONFIG,
    SHOULDER_PRESS_CONFIG,
    count_elbow_extension_cycles,
    push_up_analyzer,
    shoulder_press_analyzer,
)


ANGLE_CYCLE = [95] * 5 + [105, 120, 138, 155, 165, 170, 170, 168] + [150, 132, 115, 102, 95, 95, 95]


def _common_lower_landmarks(landmarks, side, x, horizontal):
    hip = {"x": x + (0.26 if horizontal else 0), "y": 0.5 if horizontal else 0.62, "visibility": 0.95}
    ankle = {"x": x + (0.52 if horizontal else 0), "y": 0.5 if horizontal else 0.88, "visibility": 0.95}
    landmarks[f"{side}_hip"] = hip
    landmarks[f"{side}_knee"] = {"x": (hip["x"] + ankle["x"]) / 2, "y": (hip["y"] + ankle["y"]) / 2, "visibility": 0.95}
    landmarks[f"{side}_ankle"] = ankle
    landmarks[f"{side}_heel"] = {**ankle}
    landmarks[f"{side}_foot_index"] = {"x": ankle["x"] + 0.02, "y": ankle["y"], "visibility": 0.95}


def _push_up_frames():
    frames = []
    for index, angle in enumerate(ANGLE_CYCLE):
        landmarks = {}
        for side, offset in (("left", 0.0), ("right", 0.025)):
            elbow = {"x": 0.40 + offset, "y": 0.50, "visibility": 0.95}
            shoulder = {"x": 0.28 + offset, "y": 0.50, "visibility": 0.95}
            radians = math.radians(180 - angle)
            landmarks[f"{side}_shoulder"] = shoulder
            landmarks[f"{side}_elbow"] = elbow
            landmarks[f"{side}_wrist"] = {"x": elbow["x"] + 0.12 * math.cos(radians), "y": elbow["y"] + 0.12 * math.sin(radians), "visibility": 0.95}
            _common_lower_landmarks(landmarks, side, shoulder["x"], True)
        frames.append({"frame_index": index, "timestamp_sec": index * 0.1, "source_total_frames": len(ANGLE_CYCLE), "landmarks": landmarks})
    return frames


def _shoulder_press_frames():
    frames = []
    for index, angle in enumerate(ANGLE_CYCLE):
        landmarks = {}
        for side, x in (("left", 0.4), ("right", 0.6)):
            elbow = {"x": x, "y": 0.32, "visibility": 0.95}
            radians = math.radians(90 + angle)
            landmarks[f"{side}_shoulder"] = {"x": x, "y": 0.45, "visibility": 0.95}
            landmarks[f"{side}_elbow"] = elbow
            landmarks[f"{side}_wrist"] = {"x": elbow["x"] + 0.13 * math.cos(radians), "y": elbow["y"] + 0.13 * math.sin(radians), "visibility": 0.95}
            _common_lower_landmarks(landmarks, side, x, False)
        frames.append({"frame_index": index, "timestamp_sec": index * 0.1, "source_total_frames": len(ANGLE_CYCLE), "landmarks": landmarks})
    return frames


def test_elbow_cycle_state_machine_counts_complete_cycle_and_rejects_partial():
    complete = count_elbow_extension_cycles(ANGLE_CYCLE, [index * 0.1 for index in range(len(ANGLE_CYCLE))], config=PUSH_UP_CONFIG)
    partial = count_elbow_extension_cycles([95] * 5 + [110, 125, 138, 130, 110, 95, 95, 95], config=PUSH_UP_CONFIG)
    assert complete.total_reps == 1
    assert complete.rep_events[0].maximum_angle >= PUSH_UP_CONFIG.extended_angle_min
    assert partial.total_reps == 0
    assert partial.ignored_partial_reps >= 1


def test_push_up_analyzer_requires_horizontal_support_geometry():
    response = push_up_analyzer.analyze_landmarks(_push_up_frames(), include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.average_elbow_angle is not None
    assert response.frame_analysis[0].elbow_angle is not None
    upright = _shoulder_press_frames()
    rejected = push_up_analyzer.analyze_landmarks(upright)
    assert rejected.status == "rejected"
    assert "upright_or_incompatible_push_up_position" in rejected.detected_issues


def test_shoulder_press_analyzer_requires_visible_overhead_extension():
    response = shoulder_press_analyzer.analyze_landmarks(_shoulder_press_frames(), include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.score_breakdown.extension_range_score > 0
    no_overhead = _shoulder_press_frames()
    for frame in no_overhead:
        for side in ("left", "right"):
            frame["landmarks"][f"{side}_wrist"]["y"] += 0.5
    rejected = shoulder_press_analyzer.analyze_landmarks(no_overhead)
    assert rejected.status == "rejected"
    assert "no_visible_overhead_press_position" in rejected.detected_issues
