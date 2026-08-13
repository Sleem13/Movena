from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine
from app.db.models import AnalysisSession, User
from app.main import app
from app.services.realtime_coaching_service import RealtimeCurlSession, RealtimeExerciseSession


def pose(angle_state: str) -> list[dict]:
    points = [{"x": 0.0, "y": 0.0, "visibility": 0.0} for _ in range(33)]
    points[12] = {"x": 0.5, "y": 0.2, "visibility": 0.95}
    points[14] = {"x": 0.5, "y": 0.5, "visibility": 0.95}
    points[16] = ({"x": 0.5, "y": 0.8, "visibility": 0.95} if angle_state == "extended"
                  else {"x": 0.72, "y": 0.32, "visibility": 0.95})
    return points


def neutral_hand() -> list[dict]:
    points = [{"x": 0.5, "y": 0.8} for _ in range(21)]
    points[5] = {"x": 0.49, "y": 0.7}
    points[17] = {"x": 0.51, "y": 0.6}
    return [{"landmarks": points, "handedness": "Right"}]


def joint_pose(exercise_id: str, state: str) -> list[dict]:
    points = [{"x": 0.0, "y": 0.0, "visibility": 0.0} for _ in range(33)]
    if exercise_id == "bodyweight_squat":
        points[24] = {"x": 0.5, "y": 0.25, "visibility": 0.95}
        points[26] = {"x": 0.5, "y": 0.55, "visibility": 0.95}
        points[28] = {"x": 0.5, "y": 0.85, "visibility": 0.95} if state == "start" else {"x": 0.75, "y": 0.42, "visibility": 0.95}
    elif exercise_id == "shoulder_press":
        points[12] = {"x": 0.5, "y": 0.5, "visibility": 0.95}
        points[14] = {"x": 0.7, "y": 0.5, "visibility": 0.95}
        points[16] = {"x": 0.7, "y": 0.3, "visibility": 0.95} if state == "start" else {"x": 0.9, "y": 0.5, "visibility": 0.95}
    else:
        points[24] = {"x": 0.5, "y": 0.8, "visibility": 0.95}
        points[12] = {"x": 0.5, "y": 0.5, "visibility": 0.95}
        points[14] = {"x": 0.5, "y": 0.75, "visibility": 0.95} if state == "start" else {"x": 0.8, "y": 0.5, "visibility": 0.95}
    return points


def test_realtime_state_emits_hammer_curl_rep_with_grip_evidence():
    session = RealtimeCurlSession(user_id="user", exercise_id="hammer_curl")
    events = []
    timestamp = 0
    for state in ["extended"] * 2 + ["flexed"] * 3 + ["extended"] * 3:
        timestamp += 200
        events.extend(session.process_frame({
            "timestamp_ms": timestamp, "pose_landmarks": pose(state), "hands": neutral_hand(),
        }))
    rep = next(event for event in events if event["type"] == "rep_event")
    assert rep["rep_number"] == 1
    assert rep["grip"] == "neutral"
    assert session.summary()["grip_evidence_frames"] == 5


def test_realtime_state_counts_new_live_exercises():
    for exercise_id in ("bodyweight_squat", "shoulder_press", "shoulder_abduction"):
        session = RealtimeExerciseSession(user_id="user", exercise_id=exercise_id)
        events = []
        timestamp = 0
        for state in ["start"] * 2 + ["peak"] * 3 + ["start"] * 3:
            timestamp += 200
            events.extend(session.process_frame({"timestamp_ms": timestamp, "pose_landmarks": joint_pose(exercise_id, state)}))
        rep = next(event for event in events if event["type"] == "rep_event")
        assert rep["rep_number"] == 1
        assert rep["exercise_id"] == exercise_id


def test_coaching_websocket_requires_auth_and_persists_summary(tmp_path, monkeypatch):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'coaching.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr("app.api.routes.realtime_coaching.SessionLocal", factory)
    db = factory()
    db.add(User(user_id="coach-user", email="coach@example.com", password_hash=get_password_hash("StrongPassword123"), role="patient"))
    db.commit()
    db.close()

    client = TestClient(app)
    with client.websocket_connect("/api/v1/coaching/stream") as socket:
        socket.send_json({"type": "authenticate"})
        assert socket.receive_json()["code"] == "AUTH_REQUIRED"

    with client.websocket_connect("/api/v1/coaching/stream") as socket:
        socket.send_json({
            "type": "authenticate", "token": create_access_token("coach-user", "patient"),
            "exercise_id": "hammer_curl",
        })
        started = socket.receive_json()
        assert started["type"] == "session_started" and not started["frames_retained"]
        socket.send_json({"type": "stop"})
        summary = socket.receive_json()
        assert summary["type"] == "session_summary"

    db = factory()
    row = db.query(AnalysisSession).filter_by(session_id=summary["session_id"]).one()
    assert row.owner_user_id == "coach-user"
    assert row.source_filename is None
    assert "no camera frames" in row.summary
    db.close()


def test_coaching_readiness_contract():
    payload = TestClient(app).get("/api/v1/coaching/readiness").json()
    assert payload["status"] == "ready"
    assert all(payload["capabilities"].values())
    assert {"bodyweight_squat", "shoulder_press", "shoulder_abduction"}.issubset(payload["supported_realtime_exercises"])
