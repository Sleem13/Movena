import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.gait.analyzer import gait_analyzer


def _visibility_point(x, y, visibility=0.95):
    return {"x": x, "y": y, "z": 0.0, "visibility": visibility}


def _foot_wave(frame_index, period=40, amplitude=0.11, phase_offset=0.0):
    phase = ((frame_index / period) + phase_offset) % 1.0
    if phase <= 0.6:
        return amplitude * math.cos(math.pi * phase / 0.6)
    return -amplitude * math.cos(math.pi * (phase - 0.6) / 0.4)


def _synthetic_gait_frames(count=150):
    frames = []
    for index in range(count):
        left_x = _foot_wave(index)
        right_x = _foot_wave(index, phase_offset=0.5)
        landmarks = {
            "left_shoulder": _visibility_point(0.47, 0.18),
            "right_shoulder": _visibility_point(0.53, 0.18),
            "left_hip": _visibility_point(0.48, 0.43),
            "right_hip": _visibility_point(0.52, 0.43),
            "left_knee": _visibility_point(0.50 + left_x * 0.45, 0.67),
            "right_knee": _visibility_point(0.50 + right_x * 0.45, 0.67),
            "left_ankle": _visibility_point(0.50 + left_x * 0.9, 0.88),
            "right_ankle": _visibility_point(0.50 + right_x * 0.9, 0.88),
            "left_heel": _visibility_point(0.50 + left_x, 0.91),
            "right_heel": _visibility_point(0.50 + right_x, 0.91),
            "left_foot_index": _visibility_point(0.50 + left_x + 0.025, 0.91),
            "right_foot_index": _visibility_point(0.50 + right_x + 0.025, 0.91),
        }
        frames.append(
            {
                "frame_index": index,
                "timestamp_sec": index / 30,
                "source_total_frames": count,
                "landmarks": landmarks,
                "average_visibility": 0.95,
                "low_confidence": False,
            }
        )
    return frames


def test_gait_analyzer_reports_spatiotemporal_metrics():
    report = gait_analyzer.analyze_landmarks(_synthetic_gait_frames(), include_frame_data=True)

    assert report.status == "success"
    assert report.exercise == "walking_gait_screen"
    assert report.gait_metrics is not None
    assert report.gait_metrics.gait_cycles >= 2
    assert report.gait_metrics.step_count >= 4
    assert report.gait_metrics.average_stance_percent is not None
    assert 45 <= report.gait_metrics.average_stance_percent <= 75
    assert report.score_breakdown.gait_phase_score is not None
    assert report.frame_analysis


def test_gait_analyzer_rejects_short_non_cyclic_input():
    frames = _synthetic_gait_frames(20)
    report = gait_analyzer.analyze_landmarks(frames)

    assert report.status == "rejected"
    assert report.error_code == "INVALID_GAIT_VIDEO"
    assert "insufficient_gait_cycles" in report.detected_issues

