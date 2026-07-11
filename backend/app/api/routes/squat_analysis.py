import logging

from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import JSONResponse

from app.schemas.analysis_schema import AnalysisResponse, ErrorResponse
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.services.artifact_service import create_artifact
from app.services.overlay_service import generate_skeleton_overlay
from app.services.report_service import generate_session_report
from app.services.squat_analysis_service import analyze_squat_landmarks, create_frame_analysis
from app.utils.file_utils import UploadValidationError, remove_file, save_upload_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


def error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(error_code=error_code, message=message)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def pose_error_code(message: str) -> str:
    lowered = message.lower()
    if "no pose" in lowered:
        return "NO_POSE_DETECTED"
    if "open" in lowered or "readable frames" in lowered or "too short" in lowered:
        return "VIDEO_OPEN_FAILED"
    return "PROCESSING_ERROR"


@router.post(
    "/squat",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid upload or video content"},
        422: {"model": ErrorResponse, "description": "No usable pose detected"},
        500: {"model": ErrorResponse, "description": "Internal processing error"},
    },
)
async def analyze_squat(
    video: UploadFile = File(...),
    include_overlay: bool = Query(False),
    include_frame_data: bool = Query(False),
    generate_report: bool = Query(False),
):
    logger.info("Video received: filename=%s content_type=%s", video.filename, video.content_type)
    try:
        video_path = await save_upload_file(video)
    except UploadValidationError as exc:
        return error_response(status.HTTP_400_BAD_REQUEST, exc.error_code, exc.message)

    generated_artifacts = []
    try:
        landmarks = extract_pose_landmarks(video_path)
        logger.info("Landmarks detected in %s frames", len(landmarks))
        report = analyze_squat_landmarks(
            landmarks, include_frame_data=include_frame_data
        )
        if generate_report:
            report_id, report_path = create_artifact("report")
            generated_artifacts.append(report_path)
            generate_session_report(report, report_path)
            report.report_id = report_id
            report.report_download_url = f"/api/v1/artifacts/reports/{report_id}"

        if include_overlay:
            overlay_id, overlay_path = create_artifact("overlay")
            generated_artifacts.append(overlay_path)
            generate_skeleton_overlay(
                video_path,
                overlay_path,
                landmarks,
                create_frame_analysis(landmarks),
            )
            report.overlay_id = overlay_id
            report.overlay_download_url = f"/api/v1/artifacts/overlays/{overlay_id}"
        logger.info("Analysis completed: reps=%s score=%s", report.total_reps, report.movement_score)
        return report
    except PoseEstimationError as exc:
        logger.warning("Pose estimation failed: %s", exc)
        return error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            pose_error_code(str(exc)),
            str(exc),
        )
    except Exception as exc:
        logger.exception("Internal processing error")
        for artifact_path in generated_artifacts:
            artifact_path.unlink(missing_ok=True)
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "PROCESSING_ERROR",
            "Unable to complete squat analysis.",
        )
    finally:
        remove_file(video_path)
