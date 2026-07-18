"""Upload endpoint for the rule-based hip-abduction analyzer."""

import logging

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.dependencies.auth import analysis_current_user
from app.api.routes.squat_analysis import error_response, pose_error_code
from app.core.config import get_settings
from app.db.models import User
from app.exercises.hip_abduction.analyzer import hip_abduction_analyzer
from app.schemas.analysis_schema import AnalysisResponse, ErrorResponse
from app.services.artifact_service import build_artifact_url, create_artifact
from app.services.overlay_video_service import create_overlay_video
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.services.report_service import generate_session_report
from app.services.session_persistence_service import save_analysis_session
from app.utils.file_utils import UploadValidationError, remove_file, save_upload_file


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


@router.post("/hip-abduction", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_hip_abduction(video: UploadFile = File(...), include_overlay: bool = Query(False), include_frame_data: bool = Query(False), generate_report: bool = Query(False), include_ml: bool = Query(False), save_session: bool = Query(False), patient_id: str | None = Query(None), current_user: User | None = Depends(analysis_current_user)):
    settings = get_settings()
    del include_ml
    try:
        video_path = await save_upload_file(video)
    except UploadValidationError as exc:
        return error_response(status.HTTP_400_BAD_REQUEST, exc.error_code, exc.message)
    generated_artifacts = []
    try:
        landmarks = extract_pose_landmarks(video_path)
        report = hip_abduction_analyzer.analyze_landmarks(landmarks, include_frame_data=include_frame_data or include_overlay)
        if generate_report and settings.enable_report_generation and report.status == "success":
            report_id, report_path = create_artifact("report")
            generated_artifacts.append(report_path)
            generate_session_report(report, report_path)
            report.report_id, report.report_download_url = report_id, build_artifact_url(f"/api/v1/artifacts/reports/{report_id}", report_id, "report")
        elif generate_report and not settings.enable_report_generation:
            report.limitations.append("PDF report generation is disabled by deployment configuration.")
        if include_overlay and settings.enable_overlay_generation and report.status == "success" and report.frame_analysis:
            try:
                overlay = create_overlay_video(video_path, landmarks, report.frame_analysis)
                generated_artifacts.append(overlay.overlay_path)
                report.overlay_id, report.overlay_preview_url, report.overlay_download_url = overlay.overlay_id, overlay.overlay_preview_url, overlay.overlay_download_url
            except Exception as exc:
                logger.warning("Hip-abduction overlay generation failed: %s", exc)
                report.limitations.append("Annotated movement preview could not be generated for this analysis.")
        elif include_overlay and not settings.enable_overlay_generation:
            report.limitations.append("Annotated overlays are disabled by deployment configuration.")
        if not include_frame_data:
            report.frame_analysis = None
        can_save = current_user is not None or settings.enable_public_demo_mode
        if save_session and settings.enable_session_history and can_save:
            try:
                saved = save_analysis_session(report, source_filename=video.filename, media_metadata={"content_type": video.content_type, "size_bytes": video_path.stat().st_size if video_path.exists() else None}, patient_id=patient_id, owner_user_id=current_user.user_id if current_user else None, created_by_user_id=current_user.user_id if current_user else None)
                report.session_id = saved.session_id
                if getattr(saved, "patient_assignment_warning", False):
                    report.validation_warnings.append("Patient profile was not found; session was saved unassigned.")
            except Exception as exc:
                logger.warning("Session persistence failed; analysis remains available: %s", exc)
                report.validation_warnings.append("Session could not be saved.")
        elif save_session:
            report.validation_warnings.append("Log in to save this session." if not can_save else "Session history is disabled by deployment configuration.")
        return report
    except PoseEstimationError as exc:
        return error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, pose_error_code(str(exc)), str(exc))
    except Exception:
        logger.exception("Unable to complete hip-abduction analysis")
        for artifact_path in generated_artifacts:
            artifact_path.unlink(missing_ok=True)
        return error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "PROCESSING_ERROR", "Unable to complete hip-abduction analysis.")
    finally:
        remove_file(video_path)
