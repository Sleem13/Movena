import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.datasets.modality_guard import IncompatibleModalityError, ensure_pipeline_compatible


def test_modality_guard_blocks_sensor_from_video_pipeline():
    with pytest.raises(IncompatibleModalityError):
        ensure_pipeline_compatible("signals.txt", "video")
    assert ensure_pipeline_compatible("squat.mp4", "video") == "video"
    assert ensure_pipeline_compatible("frame.jpg", "mediapipe_pose") == "image"
    with pytest.raises(IncompatibleModalityError):
        ensure_pipeline_compatible("mixed.bin", "video", declared_modality="mixed")

