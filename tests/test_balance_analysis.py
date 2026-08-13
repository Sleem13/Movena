import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.balance.analyzer import balance_analyzer


def _point(x, y, visibility=0.95):
    return {"x": x, "y": y, "z": 0.0, "visibility": visibility}


def _synthetic_balance_frames(count=150, sway=0.004):
    frames = []
    for index in range(count):
        offset = sway * math.sin(index / 9)
        landmarks = {
            "left_shoulder": _point(0.45 + offset, 0.18),
            "right_shoulder": _point(0.55 + offset, 0.18),
            "left_hip": _point(0.47 + offset * 0.7, 0.44),
            "right_hip": _point(0.53 + offset * 0.7, 0.44),
            "left_knee": _point(0.47 + offset * 0.4, 0.68),
            "right_knee": _point(0.53 + offset * 0.4, 0.68),
            "left_ankle": _point(0.46, 0.90),
            "right_ankle": _point(0.54, 0.90),
            "left_heel": _point(0.455, 0.92),
            "right_heel": _point(0.535, 0.92),
            "left_foot_index": _point(0.475, 0.92),
            "right_foot_index": _point(0.555, 0.92),
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


def test_balance_analyzer_reports_postural_sway_metrics():
    report = balance_analyzer.analyze_landmarks(_synthetic_balance_frames(), include_frame_data=True)

    assert report.status == "success"
    assert report.exercise == "balance"
    assert report.balance_metrics is not None
    assert report.balance_metrics.hold_duration_sec >= 3
    assert report.balance_metrics.sway_rms is not None
    assert report.score_breakdown.sway_control_score is not None
    assert report.frame_analysis


def test_balance_analyzer_rejects_short_hold():
    report = balance_analyzer.analyze_landmarks(_synthetic_balance_frames(count=45))

    assert report.status == "rejected"
    assert report.error_code == "INVALID_BALANCE_VIDEO"
    assert "short_balance_hold" in report.detected_issues

