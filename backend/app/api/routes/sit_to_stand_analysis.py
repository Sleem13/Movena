"""Upload endpoint for the rule-based sit-to-stand analyzer."""

import logging

from fastapi import APIRouter, File, Query, UploadFile, status

from app.api.routes.squat_analysis import error_response, pose_error_code
from app.exercises.sit_to_stand.analyzer import sit_to_stand_analyzer
from app.services.artifact_service import create_artifact
from app.services.overlay_video_service import create_overlay_video
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.services.report_service import generate_session_report
from app.schemas.analysis_schema import AnalysisResponse, ErrorResponse
from app.utils.file_utils import UploadValidationError, remove_file, save_upload_file


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


@router.post(
    "/sit-to-stand",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid upload or video content"},
        422: {"model": ErrorResponse, "description": "No usable pose detected"},
        500: {"model": ErrorResponse, "description": "Internal processing error"},
    },
)
async def analyze_sit_to_stand(
    video: UploadFile = File(...),
    include_overlay: bool = Query(False),
    include_frame_data: bool = Query(False),
    generate_report: bool = Query(False),
    include_ml: bool = Query(False),
):
    del include_ml  # Explicitly unavailable for this exercise in Sprint 9.
    try:
        video_path = await save_upload_file(video)
    except UploadValidationError as exc:
        return error_response(status.HTTP_400_BAD_REQUEST, exc.error_code, exc.message)
    generated_artifacts = []
    try:
        landmarks = extract_pose_landmarks(video_path)
        report = sit_to_stand_analyzer.analyze_landmarks(
            landmarks, include_frame_data=include_frame_data or include_overlay
        )
        if generate_report and report.status == "success":
            report_id, report_path = create_artifact("report")
            generated_artifacts.append(report_path)
            generate_session_report(report, report_path)
            report.report_id = report_id
            report.report_download_url = f"/api/v1/artifacts/reports/{report_id}"
        if include_overlay and report.status == "success" and report.frame_analysis:
            try:
                overlay = create_overlay_video(video_path, landmarks, report.frame_analysis)
                generated_artifacts.append(overlay.overlay_path)
                report.overlay_id = overlay.overlay_id
                report.overlay_preview_url = overlay.overlay_preview_url
                report.overlay_download_url = overlay.overlay_download_url
            except Exception as exc:
                logger.warning("Sit-to-stand overlay generation failed: %s", exc)
                report.limitations.append("Annotated movement preview could not be generated for this analysis.")
        if not include_frame_data:
            report.frame_analysis = None
        return report
    except PoseEstimationError as exc:
        return error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, pose_error_code(str(exc)), str(exc))
    except Exception:
        logger.exception("Unable to complete sit-to-stand analysis")
        for artifact_path in generated_artifacts:
            artifact_path.unlink(missing_ok=True)
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "PROCESSING_ERROR", "Unable to complete sit-to-stand analysis.",
        )
    finally:
        remove_file(video_path)
