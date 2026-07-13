import logging
from pathlib import Path
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


LANDMARK_NAMES = {
    11: "left_shoulder",
    12: "right_shoulder",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
    29: "left_heel",
    30: "right_heel",
    31: "left_foot_index",
    32: "right_foot_index",
}


class PoseEstimationError(RuntimeError):
    pass


def _landmark_to_dict(landmark: Any) -> dict[str, float]:
    return {
        "x": float(landmark.x),
        "y": float(landmark.y),
        "z": float(getattr(landmark, "z", 0.0)),
        "visibility": float(getattr(landmark, "visibility", 0.0)),
    }


def extract_pose_landmarks(video_path: Path) -> list[dict[str, Any]]:
    try:
        import cv2
    except ImportError as exc:
        raise PoseEstimationError(
            "OpenCV is not installed. Run pip install -r requirements.txt."
        ) from exc

    try:
        import mediapipe as mp
    except ImportError as exc:
        raise PoseEstimationError(
            "MediaPipe is not installed. Run pip install -r requirements.txt."
        ) from exc

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise PoseEstimationError("Unable to open uploaded video.")

    settings = get_settings()
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_landmarks: list[dict[str, Any]] = []
    processed_frames = 0
    detected_frames = 0

    with mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while True:
            success, frame = cap.read()
            if not success:
                break

            processed_frames += 1
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb_frame)
            if not result.pose_landmarks:
                continue

            detected_frames += 1
            landmarks = result.pose_landmarks.landmark
            selected = {
                name: _landmark_to_dict(landmarks[index])
                for index, name in LANDMARK_NAMES.items()
            }
            visible_values = [point["visibility"] for point in selected.values()]
            average_visibility = sum(visible_values) / len(visible_values)
            frame_landmarks.append(
                {
                    "frame_index": processed_frames - 1,
                    "timestamp_sec": round((processed_frames - 1) / fps, 6),
                    "landmarks": selected,
                    "average_visibility": average_visibility,
                    "low_confidence": average_visibility < settings.min_landmark_visibility,
                }
            )

    cap.release()
    for frame in frame_landmarks:
        frame["source_total_frames"] = processed_frames
        frame["source_pose_detected_frames"] = detected_frames
    logger.info(
        "Frames processed=%s, landmarks detected=%s",
        processed_frames,
        detected_frames,
    )

    if processed_frames == 0:
        raise PoseEstimationError("Uploaded video has no readable frames.")
    if processed_frames < settings.min_readable_video_frames:
        raise PoseEstimationError(
            f"Video is too short; at least {settings.min_readable_video_frames} readable frames are required."
        )
    if not frame_landmarks:
        raise PoseEstimationError("No pose detected in the uploaded video.")

    return frame_landmarks
