from app.services.subject_tracking_service import evaluate_subject_continuity


def _frame(frame_index: int, x: float, y: float = 0.25, scale: float = 1.0) -> dict:
    half_width = 0.08 * scale
    torso_height = 0.20 * scale
    return {
        "frame_index": frame_index,
        "timestamp_sec": frame_index / 30,
        "landmarks": {
            "left_shoulder": {"x": x - half_width, "y": y, "visibility": 0.95},
            "right_shoulder": {"x": x + half_width, "y": y, "visibility": 0.95},
            "left_hip": {"x": x - half_width * 0.75, "y": y + torso_height, "visibility": 0.95},
            "right_hip": {"x": x + half_width * 0.75, "y": y + torso_height, "visibility": 0.95},
        },
    }


def test_gradual_single_subject_motion_is_stable():
    frames = [_frame(index, 0.45 + index * 0.005, y=0.24 + index * 0.002) for index in range(20)]

    report = evaluate_subject_continuity(frames)

    assert report.suspected_subject_switch is False
    assert report.suspicious_events == ()
    assert report.checked_transitions == 19


def test_severe_pose_center_jump_fails_closed():
    frames = [_frame(0, 0.45), _frame(1, 0.46), _frame(2, 0.78)]

    report = evaluate_subject_continuity(frames)

    assert report.suspected_subject_switch is True
    assert report.severe_event_count == 1
    assert report.max_centroid_jump > 0.24
    assert "Possible subject switch" in report.details()[0]


def test_repeated_nonsevere_jumps_reach_event_limit():
    frames = [_frame(0, 0.40), _frame(1, 0.58), _frame(2, 0.40)]

    report = evaluate_subject_continuity(frames)

    assert report.suspected_subject_switch is True
    assert report.severe_event_count == 0
    assert len(report.suspicious_events) == 2


def test_large_body_scale_change_is_suspicious():
    frames = [_frame(0, 0.50, scale=1.0), _frame(1, 0.50, scale=2.1)]

    report = evaluate_subject_continuity(frames)

    assert report.suspected_subject_switch is True
    assert report.max_scale_ratio > 1.85
