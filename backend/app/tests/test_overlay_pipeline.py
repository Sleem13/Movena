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


def test_include_overlay_returns_id_and_download_url(monkeypatch, tmp_path):
    setup_analysis(monkeypatch, tmp_path)
    overlay_path = tmp_path / "artifacts/overlays/abc.mp4"
    overlay_path.parent.mkdir(parents=True)
    overlay_path.write_bytes(b"video")
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.create_overlay_video",
        lambda *_args: OverlayArtifact(
            overlay_id="abc",
            overlay_path=overlay_path,
            overlay_download_url="/api/v1/artifacts/overlays/abc",
        ),
    )

    response = client.post(
        "/api/v1/analyze/squat?include_overlay=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["total_reps"] == 1
    assert response.json()["overlay_id"] == "abc"
    assert response.json()["overlay_download_url"] == "/api/v1/artifacts/overlays/abc"


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
    assert response.json()["overlay_download_url"] is None
    assert any("preview could not be generated" in item.lower() for item in response.json()["limitations"])


def test_overlay_route_returns_mp4_and_clean_404(monkeypatch, tmp_path):
    artifact_root = tmp_path / "artifacts"
    monkeypatch.setattr(get_settings(), "artifact_dir", artifact_root)
    overlay_id = "0123456789abcdef0123456789abcdef"
    overlay = artifact_root / "overlays" / f"{overlay_id}.mp4"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"mp4-test")

    valid = client.get(f"/api/v1/artifacts/overlays/{overlay_id}")
    missing = client.get("/api/v1/artifacts/overlays/not-a-uuid")

    assert valid.status_code == 200
    assert valid.headers["content-type"].startswith("video/mp4")
    assert valid.content == b"mp4-test"
    assert missing.status_code == 404
    assert missing.json() == {
        "status": "error",
        "error_code": "ARTIFACT_NOT_FOUND",
        "message": "Overlay artifact not found or expired.",
        "details": [],
    }
