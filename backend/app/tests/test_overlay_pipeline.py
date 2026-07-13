from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse
from app.services.overlay_video_service import OverlayArtifact, OverlayGenerationError


client = TestClient(app)


def setup_analysis(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path / "uploads")
    monkeypatch.setattr(get_settings(), "artifact_dir", tmp_path / "artifacts")
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.extract_pose_landmarks",
        lambda _path: [{"frame_index": 0, "landmarks": {}}],
    )
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.analyze_squat_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(total_reps=1, movement_score=90),
    )
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.create_frame_analysis", lambda _frames: []
    )


def test_include_overlay_returns_preview_and_download_urls(monkeypatch, tmp_path):
    setup_analysis(monkeypatch, tmp_path)
    overlay_path = tmp_path / "artifacts/overlays/abc.mp4"
    overlay_path.parent.mkdir(parents=True)
    overlay_path.write_bytes(b"video")
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.create_overlay_video",
        lambda *_args: OverlayArtifact(
            overlay_id="abc",
            overlay_path=overlay_path,
            overlay_preview_url="/api/v1/artifacts/overlays/abc/preview",
            overlay_download_url="/api/v1/artifacts/overlays/abc/download",
        ),
    )

    response = client.post(
        "/api/v1/analyze/squat?include_overlay=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["total_reps"] == 1
    assert response.json()["overlay_id"] == "abc"
    assert response.json()["overlay_preview_url"] == "/api/v1/artifacts/overlays/abc/preview"
    assert response.json()["overlay_download_url"] == "/api/v1/artifacts/overlays/abc/download"


def test_include_overlay_does_not_return_urls_when_file_is_missing(monkeypatch, tmp_path):
    setup_analysis(monkeypatch, tmp_path)
    missing_path = tmp_path / "artifacts/overlays/missing.mp4"
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.create_overlay_video",
        lambda *_args: OverlayArtifact(
            overlay_id="missing",
            overlay_path=missing_path,
            overlay_preview_url="/api/v1/artifacts/overlays/missing/preview",
            overlay_download_url="/api/v1/artifacts/overlays/missing/download",
        ),
    )

    response = client.post(
        "/api/v1/analyze/squat?include_overlay=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["overlay_id"] is None
    assert response.json()["overlay_preview_url"] is None
    assert response.json()["overlay_download_url"] is None


def test_overlay_failure_does_not_break_rule_analysis(monkeypatch, tmp_path):
    setup_analysis(monkeypatch, tmp_path)

    def fail_overlay(*_args):
        raise OverlayGenerationError("codec unavailable")

    monkeypatch.setattr("app.api.routes.squat_analysis.create_overlay_video", fail_overlay)
    response = client.post(
        "/api/v1/analyze/squat?include_overlay=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["movement_score"] == 90
    assert response.json()["overlay_id"] is None
    assert response.json()["overlay_preview_url"] is None
    assert response.json()["overlay_download_url"] is None
    assert any("preview could not be generated" in item.lower() for item in response.json()["limitations"])


def test_overlay_preview_and_download_routes_return_mp4(monkeypatch, tmp_path):
    artifact_root = tmp_path / "artifacts"
    monkeypatch.setattr(get_settings(), "artifact_dir", artifact_root)
    overlay_id = "0123456789abcdef0123456789abcdef"
    overlay = artifact_root / "overlays" / f"{overlay_id}.mp4"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"mp4-test")

    preview = client.get(f"/api/v1/artifacts/overlays/{overlay_id}/preview")
    download = client.get(f"/api/v1/artifacts/overlays/{overlay_id}/download")
    suffix_preview = client.get(f"/api/v1/artifacts/overlays/{overlay_id}.mp4/preview")
    missing = client.get("/api/v1/artifacts/overlays/not-a-uuid")

    assert preview.status_code == 200
    assert preview.headers["content-type"].startswith("video/mp4")
    assert preview.headers["content-disposition"].startswith("inline")
    assert preview.content == b"mp4-test"
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("video/mp4")
    assert download.headers["content-disposition"].startswith("attachment")
    assert suffix_preview.status_code == 200
    assert missing.status_code == 404
    assert missing.json() == {
        "status": "error",
        "error_code": "ARTIFACT_NOT_FOUND",
        "message": "Overlay artifact not found or expired.",
        "details": [],
    }
