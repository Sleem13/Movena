"""MediaPipe BlazePose adapter for offline pose-backbone benchmarks."""

from importlib.util import find_spec
from pathlib import Path
from time import perf_counter
from typing import Any

from app.services.pose_backends.base_pose_backend import (
    BasePoseBackend,
    PoseBackendError,
    PoseBackendResult,
    PoseBackendUnavailableError,
)


class MediaPipePoseBackend(BasePoseBackend):
    """Expose all 33 BlazePose landmarks using the benchmark contract."""

    name = "mediapipe"
    expected_landmark_count = 33

    @classmethod
    def is_available(cls) -> bool:
        return find_spec("cv2") is not None and find_spec("mediapipe") is not None

    def extract(self, video_path: Path) -> PoseBackendResult:
        if not self.is_available():
            raise PoseBackendUnavailableError(
                "MediaPipe/OpenCV is unavailable. Run: python -m pip install -r backend/requirements.txt"
            )

        import cv2
        import mediapipe as mp

        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise PoseBackendError(f"Unable to open video: {video_path}")

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
        processed_frames = 0
        detected_frames: list[dict[str, Any]] = []
        started = perf_counter()
        try:
            with mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            ) as pose:
                while True:
                    readable, frame = capture.read()
                    if not readable:
                        break
                    frame_index = processed_frames
                    processed_frames += 1
                    result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if not result.pose_landmarks:
                        continue

                    landmarks = {}
                    for index, point in enumerate(result.pose_landmarks.landmark):
                        name = mp.solutions.pose.PoseLandmark(index).name.lower()
                        landmarks[name] = {
                            "x": float(point.x),
                            "y": float(point.y),
                            "z": float(point.z),
                            "visibility": float(point.visibility),
                        }
                    confidence = sum(
                        point["visibility"] for point in landmarks.values()
                    ) / len(landmarks)
                    detected_frames.append(
                        {
                            "frame_index": frame_index,
                            "timestamp_sec": round(frame_index / fps, 6),
                            "landmarks": landmarks,
                            "average_visibility": confidence,
                            "low_confidence": confidence < 0.45,
                        }
                    )
        finally:
            capture.release()

        runtime_sec = perf_counter() - started
        if processed_frames == 0:
            raise PoseBackendError(f"Video contains no readable frames: {video_path}")
        return PoseBackendResult(
            backend_name=self.name,
            expected_landmark_count=self.expected_landmark_count,
            processed_frames=processed_frames,
            detected_frames=detected_frames,
            source_fps=fps,
            runtime_sec=runtime_sec,
        )
