import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.analysis_schema import AnalysisResponse
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.services.squat_analysis_service import analyze_squat_landmarks
from app.utils.file_utils import remove_file, save_upload_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


@router.post(
    "/squat",
    response_model=AnalysisResponse,
    responses={
        400: {"description": "Invalid upload or video content"},
        422: {"description": "No usable pose detected"},
        500: {"description": "Internal processing error"},
    },
)
async def analyze_squat(video: UploadFile = File(...)) -> AnalysisResponse:
    logger.info("Video received: filename=%s content_type=%s", video.filename, video.content_type)
    video_path = await save_upload_file(video)

    try:
        landmarks = extract_pose_landmarks(video_path)
        logger.info("Landmarks detected in %s frames", len(landmarks))
        report = analyze_squat_landmarks(landmarks)
        logger.info("Analysis completed: reps=%s score=%s", report.total_reps, report.movement_score)
        return report
    except PoseEstimationError as exc:
        logger.warning("Pose estimation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Internal processing error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error while analyzing squat video.",
        ) from exc
    finally:
        remove_file(video_path)
