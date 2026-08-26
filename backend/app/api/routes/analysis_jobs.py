"""Authenticated durable background-analysis API."""

from uuid import uuid4

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from app.api.dependencies.auth import get_current_user
from app.api.routes.squat_analysis import error_response
from app.db.models import User
from app.schemas.analysis_job_schema import AnalysisJobCancelResponse, AnalysisJobResponse
from app.services.analysis_job_service import (
    ANALYSIS_ENDPOINTS,
    analysis_job_response,
    cancel_analysis_job,
    create_analysis_job,
    get_owned_job,
    launch_analysis_job,
    save_queued_upload,
)
from app.services.upload_validation_service import UploadValidationError


router = APIRouter(prefix="/api/v1/analysis-jobs", tags=["analysis jobs"])


@router.post("/{exercise_id}", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    exercise_id: str,
    video: UploadFile = File(...),
    include_overlay: bool = Query(False),
    include_frame_data: bool = Query(False),
    generate_report: bool = Query(False),
    include_ml: bool = Query(False),
    continue_on_subject_warning: bool = Query(False),
    save_session: bool = Query(False),
    patient_id: str | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    if exercise_id not in ANALYSIS_ENDPOINTS:
        return error_response(status.HTTP_404_NOT_FOUND, "UNSUPPORTED_EXERCISE", "The selected exercise is not supported.")
    job_id = str(uuid4())
    try:
        source_path = await save_queued_upload(video, job_id)
    except UploadValidationError as exc:
        return error_response(status.HTTP_400_BAD_REQUEST, exc.error_code, exc.message)
    job = create_analysis_job(
        user=current_user,
        exercise_id=exercise_id,
        source_path=source_path,
        source_filename=video.filename or "video.mp4",
        content_type=video.content_type,
        options={
            "include_overlay": include_overlay,
            "include_frame_data": include_frame_data,
            "generate_report": generate_report,
            "include_ml": include_ml,
            "continue_on_subject_warning": continue_on_subject_warning,
            "save_session": save_session,
            "patient_id": patient_id,
        },
        job_id=job_id,
    )
    launch_analysis_job(job.job_id)
    return analysis_job_response(job)


@router.get("/{job_id}", response_model=AnalysisJobResponse)
def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    job = get_owned_job(job_id, current_user)
    if job is None:
        return error_response(status.HTTP_404_NOT_FOUND, "JOB_NOT_FOUND", "Analysis job not found.")
    return analysis_job_response(job)


@router.post("/{job_id}/cancel", response_model=AnalysisJobCancelResponse)
def cancel_job(job_id: str, current_user: User = Depends(get_current_user)):
    job = cancel_analysis_job(job_id, current_user)
    if job is None:
        return error_response(status.HTTP_404_NOT_FOUND, "JOB_NOT_FOUND", "Analysis job not found.")
    message = "Analysis cancelled." if job.status == "cancelled" else "The analysis has already finished."
    return AnalysisJobCancelResponse(job_id=job.job_id, status=job.status, message=message)
