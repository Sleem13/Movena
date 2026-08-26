from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, JSONResponse

from app.schemas.analysis_schema import ErrorResponse
from app.services.artifact_service import artifact_download_filename, resolve_artifact, valid_artifact_signature
from app.api.dependencies.auth import AuthError, optional_current_user
from app.core.config import get_settings


router = APIRouter(prefix="/api/v1", tags=["artifacts"])


def artifact_not_found(kind: str) -> JSONResponse:
    payload = ErrorResponse(
        error_code="ARTIFACT_NOT_FOUND",
        message=f"{kind.capitalize()} artifact not found or expired.",
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump())


@router.get("/artifacts/reports/{report_id}")
def download_report(report_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user)):
    authorize_artifact(report_id, "report", user, expires, signature)
    path = resolve_artifact(report_id, "report")
    if path is None:
        return artifact_not_found("report")
    return FileResponse(path, media_type="application/pdf", filename=artifact_download_filename(exercise, "report"))


def overlay_file_or_404(overlay_id: str):
    path = resolve_artifact(overlay_id, "overlay")
    if path is None:
        return artifact_not_found("overlay")
    return path


def authorize_artifact(artifact_id: str, kind: str, user, expires: int | None, signature: str | None) -> None:
    if not get_settings().require_auth_for_analysis or user is not None:
        return
    if not valid_artifact_signature(artifact_id.removesuffix(".webm").removesuffix(".mp4").removesuffix(".pdf"), kind, expires, signature):
        raise AuthError(401, "AUTH_REQUIRED", "A valid login or unexpired artifact link is required.")


@router.get("/artifacts/overlays/{overlay_id}/preview")
def preview_overlay(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user)):
    authorize_artifact(overlay_id, "overlay", user, expires, signature)
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
def download_overlay(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user)):
    authorize_artifact(overlay_id, "overlay", user, expires, signature)
    path = overlay_file_or_404(overlay_id)
    if isinstance(path, JSONResponse):
        return path
    return FileResponse(
        path,
        media_type="video/webm",
        filename=artifact_download_filename(exercise, "overlay"),
    )


@router.get("/artifacts/overlays/{overlay_id}")
def download_overlay_legacy(overlay_id: str, exercise: str = Query("movement"), expires: int | None = Query(None), signature: str | None = Query(None), user=Depends(optional_current_user)):
    """Preserve the original download URL for existing clients."""
    return download_overlay(overlay_id, exercise, expires, signature, user)
