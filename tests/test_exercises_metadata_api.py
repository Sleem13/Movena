from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_exercises_returns_supported_exercises():
    response = client.get("/api/v1/exercises")
    assert response.status_code == 200
    items = response.json()
    supported = [item for item in items if item["supported_in_app"]]
    assert {item["exercise_id"] for item in supported} == {
        "bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction",
        "walking_gait_screen", "balance", "push_up", "shoulder_press", "bicep_curl", "shoulder_flexion", "hammer_curl"
    }
    assert all(item["endpoint_path"] for item in supported)
    assert all(item["ml_model_status"] == "optional_experimental_second_opinion" for item in supported)


def test_planned_exercises_are_not_supported():
    items = client.get("/api/v1/exercises").json()
    planned = {"heel_raise", "lunge", "step_up", "hip_flexion"}
    assert planned <= {item["exercise_id"] for item in items}
    assert all(not item["supported_in_app"] for item in items if item["exercise_id"] in planned)


def test_coaching_candidates_expose_analyzer_readiness_individually():
    items = client.get("/api/v1/exercises").json()
    candidates = {"push_up", "shoulder_press", "bicep_curl", "hammer_curl"}
    selected = [item for item in items if item["exercise_id"] in candidates]
    assert {item["exercise_id"] for item in selected} == candidates
    by_id = {item["exercise_id"]: item for item in selected}
    assert all(by_id[item]["supported_in_app"] and by_id[item]["endpoint_path"] for item in candidates)
    assert all(by_id[item]["recognition_status"] == "experimental_suggestion_only_analyzer_available" for item in candidates)


def test_exercise_detail_and_unknown_error_contract():
    response = client.get("/api/v1/exercises/bodyweight_squat")
    assert response.status_code == 200
    assert response.json()["display_name"] == "Bodyweight Squat"
    missing = client.get("/api/v1/exercises/not_real")
    assert missing.status_code == 404
    assert missing.json()["error_code"] == "EXERCISE_NOT_FOUND"
