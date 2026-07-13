"""Generate CPU-friendly, temporary annotated squat videos."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.schemas.analysis_schema import FrameAnalysis
from app.services.artifact_service import create_artifact

logger = logging.getLogger(__name__)


SKELETON_CONNECTIONS = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]


class OverlayGenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class OverlayArtifact:
    overlay_id: str
    overlay_path: Path
    overlay_preview_url: str
    overlay_download_url: str


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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    codec = "mp4v"
    writer = cv2.VideoWriter(
        str(output_path), cv2.VideoWriter_fourcc(*codec), fps, (width, height)
    )
    writer_opened = writer.isOpened()
    logger.info("Overlay codec=%s video writer opened=%s", codec, writer_opened)
    if not writer_opened:
        capture.release()
        raise OverlayGenerationError("Unable to create MP4 annotated video.")

    poses = {int(frame["frame_index"]): frame["landmarks"] for frame in pose_frames}
    metrics = {row.frame_index: row for row in frame_analysis}
    frame_index = 0
    frames_written = 0
    try:
        while True:
            ok, image = capture.read()
            if not ok:
                break
            landmarks = poses.get(frame_index)
            if landmarks:
                points = {
                    name: (int(point["x"] * width), int(point["y"] * height))
                    for name, point in landmarks.items()
                }
                for start, end in SKELETON_CONNECTIONS:
                    if start in points and end in points:
                        cv2.line(image, points[start], points[end], (40, 210, 180), 3)
                for name, point in points.items():
                    color = (0, 170, 255) if "knee" in name else (255, 180, 40)
                    cv2.circle(image, point, 6, color, -1)
                detail = metrics.get(frame_index)
                if detail:
                    label = f"{detail.phase} | knee {detail.knee_angle:.0f} deg"
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
        "Overlay frames written=%s final file exists=%s final file size bytes=%s",
        frames_written,
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
        overlay_preview_url=f"/api/v1/artifacts/overlays/{overlay_id}/preview",
        overlay_download_url=f"/api/v1/artifacts/overlays/{overlay_id}/download",
    )
