import math

from app.exercises.bicep_curl import bicep_curl_analyzer, count_bicep_curl_reps, hammer_curl_analyzer


CURL_CYCLE = [165] * 5 + [155, 140, 120, 95, 75, 60, 55, 55, 58] + [72, 92, 118, 140, 155, 165, 165, 165]


def _frames(upright=True):
    frames = []
    for index, angle in enumerate(CURL_CYCLE):
        landmarks = {}
        for side, x in (("left", 0.4), ("right", 0.6)):
            shoulder = {"x": x, "y": 0.30 if upright else 0.5, "visibility": 0.95}
            elbow = {"x": x, "y": 0.48 if upright else 0.5, "visibility": 0.95}
            radians = math.radians(-90 + angle)
            landmarks[f"{side}_shoulder"] = shoulder
            landmarks[f"{side}_elbow"] = elbow
            landmarks[f"{side}_wrist"] = {"x": elbow["x"] + 0.16 * math.cos(radians), "y": elbow["y"] + 0.16 * math.sin(radians), "visibility": 0.95}
            hip = {"x": x if upright else x + 0.25, "y": 0.65 if upright else 0.5, "visibility": 0.95}
            landmarks[f"{side}_hip"] = hip
            landmarks[f"{side}_knee"] = {"x": hip["x"], "y": 0.78, "visibility": 0.95}
            landmarks[f"{side}_ankle"] = {"x": hip["x"], "y": 0.90, "visibility": 0.95}
            landmarks[f"{side}_heel"] = {"x": hip["x"], "y": 0.91, "visibility": 0.95}
            landmarks[f"{side}_foot_index"] = {"x": hip["x"] + 0.02, "y": 0.91, "visibility": 0.95}
        frames.append({"frame_index": index, "timestamp_sec": index * 0.1, "source_total_frames": len(CURL_CYCLE), "landmarks": landmarks})
    return frames


def test_extended_flexed_extended_cycle_counts_and_partial_is_ignored():
    complete = count_bicep_curl_reps(CURL_CYCLE, [index * 0.1 for index in range(len(CURL_CYCLE))])
    partial = count_bicep_curl_reps([165] * 5 + [150, 130, 110, 100, 115, 140, 160, 165, 165])
    assert complete.total_reps == 1
    assert complete.rep_events[0].minimum_angle <= 75
    assert partial.total_reps == 0
    assert partial.ignored_partial_reps >= 1


def test_bicep_curl_analyzer_succeeds_for_upright_cycle():
    response = bicep_curl_analyzer.analyze_landmarks(_frames(), include_frame_data=True)
    assert response.status == "success"
    assert response.total_reps == 1
    assert response.average_elbow_angle is not None
    assert response.frame_analysis[0].elbow_angle is not None
    assert any("grip" in limitation.lower() for limitation in response.limitations)


def test_bicep_curl_analyzer_rejects_horizontal_position():
    response = bicep_curl_analyzer.analyze_landmarks(_frames(upright=False))
    assert response.status == "rejected"
    assert "upright_curl_position_not_visible" in response.detected_issues


def test_hammer_curl_analyzer_uses_curl_mechanics_with_grip_limitation():
    response = hammer_curl_analyzer.analyze_landmarks(_frames(), include_frame_data=True)
    assert response.status == "success"
    assert response.exercise_id == "hammer_curl"
    assert response.exercise_name == "Hammer Curl"
    assert response.total_reps == 1
    assert any("grip" in limitation.lower() for limitation in response.limitations)
