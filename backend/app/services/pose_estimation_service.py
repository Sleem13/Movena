import logging
import math
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.services.subject_tracking_service import SubjectContinuityReport, evaluate_subject_continuity

logger = logging.getLogger(__name__)


LANDMARK_NAMES = {
    0: "nose",
    2: "left_eye",
    5: "right_eye",
    7: "left_ear",
    8: "right_ear",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
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

QUALITY_LANDMARK_NAMES = {
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee",
    "right_knee", "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
}


class PoseEstimationError(RuntimeError):
    def __init__(self, message: str, *, error_code: str | None = None, details: list[str] | None = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or []


class SubjectContinuityError(PoseEstimationError):
    def __init__(self, report: SubjectContinuityReport):
        details = report.details()
        details.append("Record only the person being analyzed, with coaches and bystanders outside the frame.")
        super().__init__(
            "The tracked pose appears to switch between people. Analysis was stopped to avoid mixing subjects.",
            error_code="SUBJECT_SWITCH_DETECTED",
            details=details,
        )
        self.report = report


def subject_continuity_warning(frames: list[dict[str, Any]]) -> str | None:
    return next((str(frame["subject_continuity_warning"]) for frame in frames if frame.get("subject_continuity_warning")), None)


def _subject_continuity_warning(report: SubjectContinuityReport) -> str:
    details = report.details()
    return "Subject-continuity warning overridden by user request. " + " ".join(details)


def _landmark_to_dict(landmark: Any) -> dict[str, float]:
    return {
        "x": float(landmark.x),
        "y": float(landmark.y),
        "z": float(getattr(landmark, "z", 0.0)),
        "visibility": float(getattr(landmark, "visibility", 0.0)),
    }


def extract_pose_landmarks(video_path: Path, *, continue_on_subject_warning: bool = False) -> list[dict[str, Any]]:
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
    sample_stride = max(1, math.ceil(fps / settings.pose_target_fps))
    frame_landmarks: list[dict[str, Any]] = []
    processed_frames = 0
    analyzed_frames = 0
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
            if (processed_frames - 1) % sample_stride != 0:
                continue

            analyzed_frames += 1
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
            visible_values = [
                point["visibility"] for name, point in selected.items()
                if name in QUALITY_LANDMARK_NAMES
            ]
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
        frame["source_analyzed_frames"] = analyzed_frames
        frame["source_sample_stride"] = sample_stride
        frame["source_pose_detected_frames"] = detected_frames
    logger.info(
        "Frames decoded=%s, pose frames analyzed=%s, landmarks detected=%s, source_fps=%.2f, target_fps=%.2f, stride=%s",
        processed_frames,
        analyzed_frames,
        detected_frames,
        fps,
        settings.pose_target_fps,
        sample_stride,
    )

    if processed_frames == 0:
        raise PoseEstimationError("Uploaded video has no readable frames.")
    if processed_frames < settings.min_readable_video_frames:
        raise PoseEstimationError(
            f"Video is too short; at least {settings.min_readable_video_frames} readable frames are required."
        )
    if not frame_landmarks:
        raise PoseEstimationError("No pose detected in the uploaded video.")

    if settings.enable_subject_continuity_guard:
        continuity = evaluate_subject_continuity(
            frame_landmarks,
            min_visibility=settings.subject_min_visibility,
            max_centroid_jump=settings.subject_max_centroid_jump,
            severe_centroid_jump=settings.subject_severe_centroid_jump,
            max_scale_ratio=settings.subject_max_scale_ratio,
            suspicious_event_limit=settings.subject_switch_event_limit,
            max_tracking_gap_frames=settings.subject_max_tracking_gap_frames,
        )
        if continuity.suspected_subject_switch:
            logger.warning(
                "Subject continuity %s video: events=%s severe=%s max_jump=%.3f max_scale_ratio=%.2f",
                "warning override accepted for" if continue_on_subject_warning else "rejected",
                len(continuity.suspicious_events),
                continuity.severe_event_count,
                continuity.max_centroid_jump,
                continuity.max_scale_ratio,
            )
            if not continue_on_subject_warning:
                raise SubjectContinuityError(continuity)
            warning = _subject_continuity_warning(continuity)
            for frame in frame_landmarks:
                frame["subject_continuity_warning"] = warning

    return frame_landmarks
