from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, JSONResponse

from app.schemas.analysis_schema import ErrorResponse
from app.services.artifact_service import artifact_download_filename, resolve_artifact, valid_artifact_signature
from app.api.dependencies.auth import AuthError, optional_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import AnalysisSession, ProgressReport
from app.services.care_service import user_can_access_patient
from sqlalchemy import or_, select
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1", tags=["artifacts"])


def artifact_not_found(kind: str) -> JSONResponse:
    payload = ErrorResponse(
        error_code="ARTIFACT_NOT_FOUND",
        message=f"{kind.capitalize()} artifact not found or expired.",
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump())


@router.get("/artifacts/reports/{report_id}")
def download_report(report_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user), db: Session = Depends(get_db)):
    authorize_artifact(report_id, "report", user, expires, signature, db)
    path = resolve_artifact(report_id, "report")
    if path is None:
        return artifact_not_found("report")
    return FileResponse(path, media_type="application/pdf", filename=artifact_download_filename(exercise, "report"))


def overlay_file_or_404(overlay_id: str):
    path = resolve_artifact(overlay_id, "overlay")
    if path is None:
        return artifact_not_found("overlay")
    return path


def authorize_artifact(artifact_id: str, kind: str, user, expires: int | None, signature: str | None, db: Session | None = None) -> None:
    normalized = artifact_id.removesuffix(".webm").removesuffix(".mp4").removesuffix(".pdf")
    if db is not None:
        field = AnalysisSession.report_id if kind == "report" else AnalysisSession.overlay_id
        linked = db.scalar(select(AnalysisSession).where(field == normalized, AnalysisSession.patient_id.is_not(None)))
        progress = db.scalar(select(ProgressReport).where(ProgressReport.artifact_id == normalized)) if kind == "report" else None
        if linked or progress:
            patient_id = linked.patient_id if linked else progress.patient_id
            permitted = user is not None and user_can_access_patient(db, user, patient_id)
            if progress and user and user.role == "patient" and not progress.shared_with_patient:
                permitted = False
            if not permitted:
                raise AuthError(403, "ARTIFACT_ACCESS_DENIED", "An active care connection or patient ownership is required.")
            return
    if not get_settings().require_auth_for_analysis:
        return
    normalized = artifact_id.removesuffix(".webm").removesuffix(".mp4").removesuffix(".pdf")
    if valid_artifact_signature(normalized, kind, expires, signature):
        return
    if user is None:
        raise AuthError(401, "AUTH_REQUIRED", "A valid login or unexpired artifact link is required.")
    if db is None:
        raise AuthError(403, "ARTIFACT_ACCESS_DENIED", "A signed artifact link is required outside an authenticated request.")
    field = AnalysisSession.report_id if kind == "report" else AnalysisSession.overlay_id
    session = db.scalar(select(AnalysisSession).where(field == normalized))
    if session and (
        user.user_id in {session.owner_user_id, session.created_by_user_id}
        or (session.patient_id and user_can_access_patient(db, user, session.patient_id))
    ):
        return
    if kind == "report":
        progress = db.scalar(select(ProgressReport).where(ProgressReport.artifact_id == normalized))
        if progress and (
            user.user_id == progress.created_by_user_id
            or (progress.shared_with_patient and user_can_access_patient(db, user, progress.patient_id))
        ):
            return
    raise AuthError(403, "ARTIFACT_ACCESS_DENIED", "You do not have access to this artifact.")


@router.get("/artifacts/overlays/{overlay_id}/preview")
def preview_overlay(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user), db: Session = Depends(get_db)):
    authorize_artifact(overlay_id, "overlay", user, expires, signature, db)
    path = overlay_file_or_404(overlay_id)
    if isinstance(path, JSONResponse):
        return path
    return FileResponse(
        path,
        media_type="video/webm",
        headers={
            "Content-Disposition": f'inline; filename="{artifact_download_filename(exercise, "overlay")}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/artifacts/overlays/{overlay_id}/download")
def download_overlay(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user), db: Session = Depends(get_db)):
    authorize_artifact(overlay_id, "overlay", user, expires, signature, db)
    path = overlay_file_or_404(overlay_id)
    if isinstance(path, JSONResponse):
        return path
    return FileResponse(
        path,
        media_type="video/webm",
        filename=artifact_download_filename(exercise, "overlay"),
    )


@router.get("/artifacts/overlays/{overlay_id}")
def download_overlay_legacy(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user), db: Session = Depends(get_db)):
    """Preserve the original download URL for existing clients."""
    return download_overlay(overlay_id, exercise, expires, signature, user, db)
