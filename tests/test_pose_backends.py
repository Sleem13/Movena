import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for path in (REPO_ROOT / "backend", REPO_ROOT / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.services.pose_backends import (  # noqa: E402
    BasePoseBackend,
    MediaPipePoseBackend,
    MoveNetPoseBackend,
    PoseBackendResult,
    PoseBackendUnavailableError,
)
from benchmark_pose_backends import (  # noqa: E402
    METRIC_COLUMNS,
    metrics_from_result,
    write_outputs,
)


def _point(x, y, visibility=0.9):
    return {"x": x, "y": y, "z": 0.0, "visibility": visibility}


def _frames():
    frames = []
    for index, knee_y in enumerate((0.55, 0.6, 0.55)):
        frames.append(
            {
                "frame_index": index,
                "timestamp_sec": index / 30,
                "landmarks": {
                    "left_shoulder": _point(0.4, 0.2),
                    "right_shoulder": _point(0.6, 0.2),
                    "left_hip": _point(0.42, 0.45),
                    "right_hip": _point(0.58, 0.45),
                    "left_knee": _point(0.42, knee_y),
                    "right_knee": _point(0.58, knee_y),
                    "left_ankle": _point(0.42, 0.85),
                    "right_ankle": _point(0.58, 0.85),
                },
                "average_visibility": 0.9,
                "low_confidence": False,
            }
        )
    return frames


class DummyPoseBackend(BasePoseBackend):
    name = "dummy"
    expected_landmark_count = 8

    @classmethod
    def is_available(cls):
        return True

    def extract(self, video_path):
        return PoseBackendResult(self.name, 8, 3, _frames(), 30.0, 0.1)


def test_pose_backend_interface_contract():
    backend = DummyPoseBackend()
    result = backend.extract(Path("sample.mp4"))
    assert isinstance(backend, BasePoseBackend)
    assert result.backend_name == "dummy"
    assert result.processed_frames == 3
    assert len(result.detected_frames) == 3


def test_mediapipe_backend_is_available_or_skips_cleanly():
    if not MediaPipePoseBackend.is_available():
        pytest.skip("MediaPipe/OpenCV are optional in this test environment.")
    assert MediaPipePoseBackend().expected_landmark_count == 33


def test_movenet_backend_is_explicitly_deferred():
    backend = MoveNetPoseBackend("thunder")
    assert backend.is_available() is False
    with pytest.raises(PoseBackendUnavailableError, match="not enabled"):
        backend.extract(Path("sample.mp4"))


def test_benchmark_output_shape_with_mocked_result(tmp_path):
    result = DummyPoseBackend().extract(Path("sample.mp4"))
    row = metrics_from_result(
        result, Path("data/raw/custom_videos/squat_correct/sample.mp4")
    )
    metrics_path, summary_path = write_outputs([row], tmp_path)
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    assert list(records[0]) == METRIC_COLUMNS
    assert records[0]["backend"] == "dummy"
    assert records[0]["status"] == "success"
    assert float(records[0]["pose_detection_success_rate"]) == 1.0
    assert summary_path.exists()
    assert "Videos attempted: 1" in summary_path.read_text(encoding="utf-8")
