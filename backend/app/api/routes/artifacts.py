from fastapi import APIRouter, status
from fastapi.responses import FileResponse, JSONResponse

from app.schemas.analysis_schema import ErrorResponse
from app.services.artifact_service import resolve_artifact


router = APIRouter(prefix="/api/v1", tags=["artifacts"])


def artifact_not_found(kind: str) -> JSONResponse:
    payload = ErrorResponse(
        error_code="ARTIFACT_NOT_FOUND",
        message=f"{kind.capitalize()} artifact not found or expired.",
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump())


@router.get("/artifacts/reports/{report_id}")
def download_report(report_id: str):
    path = resolve_artifact(report_id, "report")
    if path is None:
        return artifact_not_found("report")
    return FileResponse(path, media_type="application/pdf", filename="physiovision-squat-report.pdf")


def overlay_file_or_404(overlay_id: str):
    path = resolve_artifact(overlay_id, "overlay")
    if path is None:
        return artifact_not_found("overlay")
    return path


@router.get("/artifacts/overlays/{overlay_id}/preview")
def preview_overlay(overlay_id: str):
    path = overlay_file_or_404(overlay_id)
    if isinstance(path, JSONResponse):
        return path
    return FileResponse(
        path,
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'inline; filename="{path.name}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/artifacts/overlays/{overlay_id}/download")
def download_overlay(overlay_id: str):
    path = overlay_file_or_404(overlay_id)
    if isinstance(path, JSONResponse):
        return path
    return FileResponse(
        path,
        media_type="video/mp4",
        filename="physiovision-squat-overlay.mp4",
    )


@router.get("/artifacts/overlays/{overlay_id}")
def download_overlay_legacy(overlay_id: str):
    """Preserve the original download URL for existing clients."""
    return download_overlay(overlay_id)
