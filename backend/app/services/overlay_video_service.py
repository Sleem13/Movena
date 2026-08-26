"""Generate CPU-friendly, temporary annotated movement videos."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.schemas.analysis_schema import FrameAnalysis
from app.services.artifact_service import build_artifact_url, create_artifact

logger = logging.getLogger(__name__)


SKELETON_CONNECTIONS = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]

OVERLAY_SMOOTHING_ALPHA = 0.32
MAX_INTERPOLATION_GAP_SECONDS = 0.8
POSE_EDGE_HOLD_SECONDS = 0.25
OVERLAY_TARGET_FPS = 15.0
OVERLAY_MAX_DIMENSION = 720


class OverlayGenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class OverlayArtifact:
    overlay_id: str
    overlay_path: Path
    overlay_preview_url: str
    overlay_download_url: str


def _interpolate_landmarks(
    start: dict,
    end: dict,
    progress: float,
) -> dict:
    """Blend two sampled poses so the overlay is present on source frames between them."""
    blended = {}
    for name in start.keys() & end.keys():
        start_point = start[name]
        end_point = end[name]
        blended[name] = {
            axis: float(start_point.get(axis, 0.0))
            + (float(end_point.get(axis, 0.0)) - float(start_point.get(axis, 0.0))) * progress
            for axis in ("x", "y", "z", "visibility")
        }
    return blended


def _smooth_landmarks(current: dict, previous: dict | None) -> dict:
    if not previous:
        return current
    smoothed = {}
    for name, point in current.items():
        previous_point = previous.get(name)
        if not previous_point:
            smoothed[name] = point
            continue
        smoothed[name] = {
            axis: OVERLAY_SMOOTHING_ALPHA * float(point.get(axis, 0.0))
            + (1.0 - OVERLAY_SMOOTHING_ALPHA) * float(previous_point.get(axis, 0.0))
            for axis in ("x", "y", "z", "visibility")
        }
    return smoothed


def build_stable_pose_frames(
    pose_frames: list[dict],
    total_frames: int,
    fps: float,
) -> dict[int, dict]:
    """Create a stable per-source-frame pose without carrying stale poses through long gaps."""
    samples = sorted(
        (
            (int(frame["frame_index"]), frame.get("landmarks") or {})
            for frame in pose_frames
            if frame.get("landmarks")
        ),
        key=lambda item: item[0],
    )
    if not samples or total_frames <= 0:
        return {}

    sample_stride = max(
        1,
        int(pose_frames[0].get("source_sample_stride", 1)),
    )
    max_gap = max(sample_stride * 2, int(round(fps * MAX_INTERPOLATION_GAP_SECONDS)))
    edge_hold = max(sample_stride, int(round(fps * POSE_EDGE_HOLD_SECONDS)))
    stable: dict[int, dict] = {}
    right_index = 0
    previous_smoothed = None

    for frame_index in range(total_frames):
        while right_index < len(samples) and samples[right_index][0] < frame_index:
            right_index += 1

        left = samples[right_index - 1] if right_index > 0 else None
        right = samples[right_index] if right_index < len(samples) else None
        landmarks = None

        if right and right[0] == frame_index:
            landmarks = right[1]
        elif left and right and right[0] - left[0] <= max_gap:
            progress = (frame_index - left[0]) / (right[0] - left[0])
            landmarks = _interpolate_landmarks(left[1], right[1], progress)
        elif left and frame_index - left[0] <= edge_hold:
            landmarks = left[1]
        elif right and right[0] - frame_index <= edge_hold:
            landmarks = right[1]

        if landmarks:
            previous_smoothed = _smooth_landmarks(landmarks, previous_smoothed)
            stable[frame_index] = previous_smoothed
        else:
            previous_smoothed = None

    return stable


def generate_skeleton_overlay(
    input_path: Path,
    output_path: Path,
    pose_frames: list[dict],
    frame_analysis: list[FrameAnalysis],
) -> Path:
    try:
        import cv2
    except ImportError as exc:
        raise OverlayGenerationError("OpenCV is required for overlay generation.") from exc

    logger.info("Overlay input video path: %s", input_path.resolve())
    logger.info("Overlay output path: %s", output_path.resolve())
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise OverlayGenerationError("Unable to reopen video for overlay generation.")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    if width <= 0 or height <= 0:
        capture.release()
        raise OverlayGenerationError("Video dimensions are invalid.")

    scale = min(1.0, OVERLAY_MAX_DIMENSION / max(width, height))
    output_width = max(2, int(round(width * scale)) // 2 * 2)
    output_height = max(2, int(round(height * scale)) // 2 * 2)
    frame_step = max(1, int(round(fps / OVERLAY_TARGET_FPS)))
    output_fps = fps / frame_step

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # OpenCV's mp4v output is MPEG-4 Part 2, which Chromium-based browsers do
    # not reliably decode despite the .mp4 container. VP8 in WebM is supported
    # by modern browsers and by the FFmpeg backend bundled with opencv-python.
    codec = "VP80"
    writer = cv2.VideoWriter(
        str(output_path), cv2.VideoWriter_fourcc(*codec), output_fps, (output_width, output_height)
    )
    writer_opened = writer.isOpened()
    logger.info("Overlay codec=%s video writer opened=%s", codec, writer_opened)
    if not writer_opened:
        capture.release()
        raise OverlayGenerationError("Unable to create MP4 annotated video.")

    source_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if source_frame_count <= 0 and pose_frames:
        source_frame_count = max(int(frame["frame_index"]) for frame in pose_frames) + 1
    poses = build_stable_pose_frames(pose_frames, source_frame_count, fps)
    metrics = {row.frame_index: row for row in frame_analysis}
    frame_index = 0
    frames_written = 0
    last_detail = None
    try:
        while True:
            ok, image = capture.read()
            if not ok:
                break
            if frame_index % frame_step:
                frame_index += 1
                continue
            if output_width != width or output_height != height:
                image = cv2.resize(image, (output_width, output_height), interpolation=cv2.INTER_AREA)
            landmarks = poses.get(frame_index)
            if landmarks:
                points = {
                    name: (int(point["x"] * output_width), int(point["y"] * output_height))
                    for name, point in landmarks.items()
                }
                for start, end in SKELETON_CONNECTIONS:
                    if start in points and end in points:
                        cv2.line(image, points[start], points[end], (40, 210, 180), 3)
                for name, point in points.items():
                    color = (0, 170, 255) if "knee" in name else (255, 180, 40)
                    cv2.circle(image, point, 6, color, -1)
                detail = metrics.get(frame_index)
                if detail is not None:
                    last_detail = detail
                else:
                    detail = last_detail
                if detail:
                    label = (
                        f"{detail.phase} | hip abduction {detail.hip_abduction_angle:.0f} deg"
                        if detail.hip_abduction_angle is not None
                        else f"{detail.phase} | shoulder {detail.shoulder_angle:.0f} deg"
                        if detail.shoulder_angle is not None
                        else f"{detail.phase} | elbow {detail.elbow_angle:.0f} deg"
                        if detail.elbow_angle is not None
                        else f"{detail.phase} | knee {detail.knee_angle:.0f} deg"
                    )
                    cv2.putText(
                        image, label, (20, 32), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2,
                    )
                    if detail.detected_issue:
                        warning = "Possible issue: " + detail.detected_issue.replace("_", " ")
                        cv2.putText(
                            image, warning, (20, 62), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, (20, 50, 240), 2,
                        )
            writer.write(image)
            frames_written += 1
            frame_index += 1
    finally:
        capture.release()
        writer.release()

    file_exists = output_path.is_file()
    file_size = output_path.stat().st_size if file_exists else 0
    logger.info(
        "Overlay frames written=%s output=%sx%s@%.2ffps final file exists=%s final file size bytes=%s",
        frames_written,
        output_width,
        output_height,
        output_fps,
        file_exists,
        file_size,
    )
    if frames_written == 0 or not file_exists or file_size <= 0:
        output_path.unlink(missing_ok=True)
        raise OverlayGenerationError("Annotated MP4 output is empty.")
    return output_path


def create_overlay_video(
    input_path: Path,
    pose_frames: list[dict],
    frame_analysis: list[FrameAnalysis],
    exercise_id: str | None = None,
) -> OverlayArtifact:
    overlay_id, overlay_path = create_artifact("overlay")
    try:
        generate_skeleton_overlay(input_path, overlay_path, pose_frames, frame_analysis)
    except Exception:
        overlay_path.unlink(missing_ok=True)
        raise
    if not overlay_path.is_file() or overlay_path.stat().st_size <= 0:
        overlay_path.unlink(missing_ok=True)
        raise OverlayGenerationError("Annotated MP4 was not created successfully.")
    return OverlayArtifact(
        overlay_id=overlay_id,
        overlay_path=overlay_path,
        overlay_preview_url=build_artifact_url(f"/api/v1/artifacts/overlays/{overlay_id}/preview", overlay_id, "overlay", exercise_id=exercise_id),
        overlay_download_url=build_artifact_url(f"/api/v1/artifacts/overlays/{overlay_id}/download", overlay_id, "overlay", exercise_id=exercise_id),
    )
