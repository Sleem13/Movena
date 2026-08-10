import logging

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse

from app.schemas.analysis_schema import AnalysisResponse, ErrorResponse
from app.core.config import get_settings
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.services.artifact_service import build_artifact_url, create_artifact
from app.services.overlay_video_service import create_overlay_video
from app.services.ml_prediction_service import invalid_squat_prediction, predict_experimental_quality
from app.services.analysis_confidence_service import (
    apply_ml_confidence_context,
    enrich_ml_prediction,
)
from app.services.report_service import generate_session_report
from app.services.squat_analysis_service import analyze_squat_landmarks, create_frame_analysis
from app.services.session_persistence_service import save_analysis_session
from app.utils.file_utils import UploadValidationError, remove_file, save_upload_file
from app.api.dependencies.auth import analysis_current_user
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


def error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: list[str] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(error_code=error_code, message=message, details=details or [])
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def pose_error_code(error: str | Exception) -> str:
    explicit_code = getattr(error, "error_code", None)
    if explicit_code:
        return str(explicit_code)
    message = str(error)
    lowered = message.lower()
    if "no pose" in lowered:
        return "NO_POSE_DETECTED"
    if "open" in lowered or "readable frames" in lowered or "too short" in lowered:
        return "VIDEO_OPEN_FAILED"
    return "PROCESSING_ERROR"


def pose_error_details(error: Exception) -> list[str]:
    return list(getattr(error, "details", []) or [])


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
    include_ml: bool = Query(False),
    save_session: bool = Query(False),
    patient_id: str | None = Query(None),
    current_user: User | None = Depends(analysis_current_user),
):
    settings = get_settings()
    logger.info("Video upload received: content_type=%s", video.content_type)
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
        if include_ml and settings.enable_ml_second_opinion:
            if report.status == "rejected":
                report.ml_prediction = invalid_squat_prediction()
            else:
                report.ml_prediction = enrich_ml_prediction(
                    predict_experimental_quality(landmarks), report.detected_issues
                )
                report.analysis_confidence = apply_ml_confidence_context(
                    report.analysis_confidence, report.ml_prediction
                )
        elif include_ml:
            report.validation_warnings.append("ML second opinion is disabled by deployment configuration.")
        if generate_report and settings.enable_report_generation and report.status == "success":
            report_id, report_path = create_artifact("report")
            generated_artifacts.append(report_path)
            generate_session_report(report, report_path)
            report.report_id = report_id
            report.report_download_url = build_artifact_url(f"/api/v1/artifacts/reports/{report_id}", report_id, "report")

        elif generate_report and not settings.enable_report_generation:
            report.limitations.append("PDF report generation is disabled by deployment configuration.")

        if include_overlay and settings.enable_overlay_generation and report.status == "success":
            try:
                overlay = create_overlay_video(
                    video_path, landmarks, create_frame_analysis(landmarks)
                )
                if not overlay.overlay_path.is_file() or overlay.overlay_path.stat().st_size <= 0:
                    raise RuntimeError("Overlay service returned a missing or empty artifact.")
                generated_artifacts.append(overlay.overlay_path)
                report.overlay_id = overlay.overlay_id
                report.overlay_preview_url = overlay.overlay_preview_url
                report.overlay_download_url = overlay.overlay_download_url
            except Exception as exc:
                logger.warning("Overlay generation failed; returning analysis without preview: %s", exc)
                report.limitations.append(
                    "Annotated movement preview could not be generated for this analysis."
                )
        elif include_overlay and not settings.enable_overlay_generation:
            report.limitations.append("Annotated overlays are disabled by deployment configuration.")
        can_save = current_user is not None or settings.enable_public_demo_mode
        if save_session and settings.enable_session_history and can_save:
            try:
                saved = save_analysis_session(
                    report, source_filename=video.filename,
                    media_metadata={
                        "content_type": video.content_type,
                        "size_bytes": video_path.stat().st_size if video_path.exists() else None,
                    }, patient_id=patient_id,
                    owner_user_id=current_user.user_id if current_user else None,
                    created_by_user_id=current_user.user_id if current_user else None,
                )
                report.session_id = saved.session_id
                if getattr(saved, "patient_assignment_warning", False):
                    report.validation_warnings.append("Patient profile was not found; session was saved unassigned.")
            except Exception as exc:
                logger.warning("Session persistence failed; analysis remains available: %s", exc)
                report.validation_warnings.append("Session could not be saved.")
        elif save_session:
            report.validation_warnings.append(
                "Log in to save this session." if not can_save else "Session history is disabled by deployment configuration."
            )
        logger.info("Analysis completed: reps=%s score=%s", report.total_reps, report.movement_score)
        return report
    except PoseEstimationError as exc:
        logger.warning("Pose estimation failed: %s", exc)
        return error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            pose_error_code(exc),
            str(exc),
            pose_error_details(exc),
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
