"""CPU-friendly OpenCV skeleton overlay generation."""

from pathlib import Path

from app.schemas.analysis_schema import FrameAnalysis


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
    writer = cv2.VideoWriter(
        str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        capture.release()
        raise OverlayGenerationError("Unable to create annotated video.")

    poses = {int(frame["frame_index"]): frame["landmarks"] for frame in pose_frames}
    metrics = {row.frame_index: row for row in frame_analysis}
    frame_index = 0
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
                    cv2.line(image, points[start], points[end], (40, 210, 180), 3)
                for name, point in points.items():
                    color = (0, 170, 255) if "knee" in name else (255, 180, 40)
                    cv2.circle(image, point, 6, color, -1)
                detail = metrics.get(frame_index)
                if detail:
                    label = f"{detail.phase} | knee {detail.knee_angle:.0f} deg"
                    cv2.putText(image, label, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    if detail.detected_issue:
                        warning = "Possible issue: " + detail.detected_issue.replace("_", " ")
                        cv2.putText(image, warning, (20, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 50, 240), 2)
            writer.write(image)
            frame_index += 1
    finally:
        capture.release()
        writer.release()

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise OverlayGenerationError("Annotated video output is empty.")
    return output_path
