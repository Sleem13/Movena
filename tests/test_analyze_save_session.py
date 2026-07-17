import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction
from app.api.dependencies.auth import analysis_current_user


client = TestClient(app)


def setup_route(monkeypatch, tmp_path, route):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr(get_settings(), "enable_public_demo_mode", True)
    monkeypatch.setattr(f"app.api.routes.{route}.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    if route == "squat_analysis":
        monkeypatch.setattr(
            f"app.api.routes.{route}.analyze_squat_landmarks",
            lambda _frames, include_frame_data=False: AnalysisResponse(total_reps=2, movement_score=85),
        )
    else:
        monkeypatch.setattr(
            f"app.api.routes.{route}.sit_to_stand_analyzer.analyze_landmarks",
            lambda _frames, include_frame_data=False: AnalysisResponse(
                exercise="sit_to_stand", total_reps=2, movement_score=82,
                ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="ML unavailable."),
            ),
        )


def test_save_session_false_does_not_call_persistence(monkeypatch, tmp_path):
    setup_route(monkeypatch, tmp_path, "squat_analysis")
    called = []
    monkeypatch.setattr("app.api.routes.squat_analysis.save_analysis_session", lambda *_a, **_k: called.append(True))
    response = client.post("/api/v1/analyze/squat", files={"video": ("a.mp4", b"video", "video/mp4")})
    assert response.status_code == 200 and response.json()["session_id"] is None
    assert called == []


def test_save_session_true_returns_ids_for_both_exercises(monkeypatch, tmp_path):
    for route, endpoint, identifier in (
        ("squat_analysis", "squat", "squat-session"),
        ("sit_to_stand_analysis", "sit-to-stand", "chair-session"),
    ):
        setup_route(monkeypatch, tmp_path, route)
        monkeypatch.setattr(
            f"app.api.routes.{route}.save_analysis_session",
            lambda *_a, _id=identifier, **_k: SimpleNamespace(session_id=_id),
        )
        response = client.post(
            f"/api/v1/analyze/{endpoint}?save_session=true",
            files={"video": ("a.mp4", b"video", "video/mp4")},
        )
        assert response.status_code == 200
        assert response.json()["session_id"] == identifier


def test_session_save_failure_does_not_break_analysis(monkeypatch, tmp_path):
    setup_route(monkeypatch, tmp_path, "squat_analysis")
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.save_analysis_session",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("database unavailable")),
    )
    response = client.post(
        "/api/v1/analyze/squat?save_session=true",
        files={"video": ("a.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert response.json()["session_id"] is None
    assert "Session could not be saved." in response.json()["validation_warnings"]


def test_analyze_can_pass_patient_id_and_invalid_profile_warning(monkeypatch, tmp_path):
    setup_route(monkeypatch, tmp_path, "squat_analysis")
    captured = {}
    def save(*_args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(session_id="saved-unassigned", patient_assignment_warning=True)
    monkeypatch.setattr("app.api.routes.squat_analysis.save_analysis_session", save)
    response = client.post(
        "/api/v1/analyze/squat?save_session=true&patient_id=missing-profile",
        files={"video": ("a.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert captured["patient_id"] == "missing-profile"
    assert "Patient profile was not found; session was saved unassigned." in response.json()["validation_warnings"]


def test_authenticated_save_attaches_owner(monkeypatch, tmp_path):
    setup_route(monkeypatch, tmp_path, "squat_analysis")
    monkeypatch.setattr(get_settings(), "enable_public_demo_mode", False)
    app.dependency_overrides[analysis_current_user] = lambda: SimpleNamespace(user_id="owner-1", role="patient")
    captured = {}
    monkeypatch.setattr("app.api.routes.squat_analysis.save_analysis_session", lambda *_a, **kwargs: (captured.update(kwargs) or SimpleNamespace(session_id="owned")))
    try:
        response = client.post("/api/v1/analyze/squat?save_session=true", files={"video": ("a.mp4", b"video", "video/mp4")})
        assert response.status_code == 200 and captured["owner_user_id"] == "owner-1"
        assert captured["created_by_user_id"] == "owner-1"
    finally:
        app.dependency_overrides.pop(analysis_current_user, None)
