from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_production_container_includes_recognition_artifacts():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert "COPY models/recognition /app/models/recognition" in dockerfile
    assert "!models/recognition/**" in dockerignore
    assert "**/venv" in dockerignore
    assert (
        PROJECT_ROOT
        / "models/recognition/exercise_pose_xgb_20260809T154328Z/model.json"
    ).is_file()
