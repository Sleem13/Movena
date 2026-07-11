from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.services.artifact_service import resolve_artifact


router = APIRouter(prefix="/api/v1", tags=["artifacts"])


@router.get("/artifacts/reports/{report_id}")
def download_report(report_id: str):
    path = resolve_artifact(report_id, "report")
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or expired.",
        )
    return FileResponse(path, media_type="application/pdf", filename="physiovision-squat-report.pdf")


@router.get("/artifacts/overlays/{overlay_id}")
def download_overlay(overlay_id: str):
    path = resolve_artifact(overlay_id, "overlay")
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Overlay not found or expired.",
        )
    return FileResponse(path, media_type="video/mp4", filename="physiovision-squat-overlay.mp4")
