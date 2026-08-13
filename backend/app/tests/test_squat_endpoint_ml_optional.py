from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def setup_success(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.extract_pose_landmarks",
        lambda _path: [{"landmarks": {}}],
    )
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.analyze_squat_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(total_reps=2, movement_score=85),
    )


def test_include_ml_false_keeps_optional_output_absent(monkeypatch, tmp_path):
    setup_success(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert response.json()["total_reps"] == 2
    assert response.json()["ml_prediction"] is None


def test_include_ml_true_adds_experimental_second_opinion(monkeypatch, tmp_path):
    setup_success(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "app.services.ml_second_opinion_service.predict_experimental_quality",
        lambda _frames: MLPrediction(
            enabled=True,
            predicted_label="squat_trunk_lean",
            confidence=0.61,
            model_name="svc_rbf",
            warning="Experimental baseline model. Not clinically validated.",
        ),
    )
    response = client.post(
        "/api/v1/analyze/squat?include_ml=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert response.json()["total_reps"] == 2
    assert response.json()["ml_prediction"]["enabled"] is True
    assert "not clinically validated" in response.json()["ml_prediction"]["warning"].lower()


def test_ml_failure_still_returns_rule_based_result(monkeypatch, tmp_path):
    setup_success(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "app.services.ml_second_opinion_service.predict_experimental_quality",
        lambda _frames: MLPrediction(
            enabled=False,
            warning="ML baseline unavailable. Rule-based analysis is still available.",
        ),
    )
    response = client.post(
        "/api/v1/analyze/squat?include_ml=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert response.json()["movement_score"] == 85
    assert response.json()["ml_prediction"]["enabled"] is False
