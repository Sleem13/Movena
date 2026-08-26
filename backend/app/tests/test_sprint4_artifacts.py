import os
import time

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, FrameAnalysis
from app.services.artifact_service import artifact_download_filename, cleanup_expired_artifacts, create_artifact, resolve_artifact
from app.services.overlay_service import generate_skeleton_overlay
from app.services.report_service import generate_session_report
from app.services.squat_analysis_service import create_frame_analysis


client = TestClient(app)


def sample_report() -> AnalysisResponse:
    return AnalysisResponse(
        total_reps=2,
        average_knee_angle=101.2,
        average_hip_angle=76.5,
        average_trunk_angle=22.1,
        movement_score=80,
        detected_issues=["poor_depth"],
        feedback=["Possible movement issue detected.", "Educational only."],
        limitations=["Does not replace clinical assessment."],
    )


def test_pdf_report_generation(tmp_path):
    output = generate_session_report(sample_report(), tmp_path / "report.pdf")
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 1000


def test_artifact_resolution_and_expiry(monkeypatch, tmp_path):
    settings = get_settings()
    monkeypatch.setattr(settings, "artifact_dir", tmp_path)
    monkeypatch.setattr(settings, "artifact_ttl_seconds", 10)
    artifact_id, path = create_artifact("report")
    path.write_bytes(b"%PDF-test")
    assert resolve_artifact(artifact_id, "report") == path

    old_time = time.time() - 20
    os.utime(path, (old_time, old_time))
    assert cleanup_expired_artifacts() == 1
    assert resolve_artifact(artifact_id, "report") is None


def test_artifact_download_filename_uses_safe_exercise_slug():
    assert artifact_download_filename("walking_gait_screen", "report") == "physiovision-walking-gait-screen-report.pdf"
    assert artifact_download_filename("../../Unsafe Name", "overlay") == "physiovision-unsafe-name-overlay.webm"


def test_invalid_artifact_ids_return_404_without_path_access(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "artifact_dir", tmp_path)
    report_response = client.get("/api/v1/artifacts/reports/not-a-uuid")
    overlay_response = client.get("/api/v1/artifacts/overlays/../../README.md")
    assert report_response.status_code == 404
    assert overlay_response.status_code == 404


def test_frame_analysis_contains_phase_timestamp_and_issue():
    def point(x, y):
        return {"x": x, "y": y, "z": 0.0, "visibility": 0.95}

    frames = [{
        "frame_index": 7,
        "timestamp_sec": 0.25,
        "low_confidence": False,
        "landmarks": {
            "left_shoulder": point(0.40, 0.20), "right_shoulder": point(0.60, 0.20),
            "left_hip": point(0.42, 0.50), "right_hip": point(0.58, 0.50),
            "left_knee": point(0.42, 0.70), "right_knee": point(0.58, 0.70),
            "left_ankle": point(0.52, 0.85), "right_ankle": point(0.48, 0.85),
        },
    }]
    row = create_frame_analysis(frames)[0]
    assert row.frame_index == 7
    assert row.timestamp_sec == 0.25
    assert row.phase in {"standing", "descent", "depth", "ascent"}
    assert 0 <= row.knee_angle <= 180


def test_overlay_service_writes_annotated_video(tmp_path):
    source = tmp_path / "source.mp4"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 10.0, (96, 96))
    assert writer.isOpened()
    for _ in range(3):
        writer.write(np.zeros((96, 96, 3), dtype=np.uint8))
    writer.release()

    landmarks = {
        name: {"x": x, "y": y, "z": 0.0, "visibility": 0.95}
        for name, x, y in [
            ("left_shoulder", .35, .2), ("right_shoulder", .65, .2),
            ("left_hip", .4, .5), ("right_hip", .6, .5),
            ("left_knee", .4, .7), ("right_knee", .6, .7),
            ("left_ankle", .4, .9), ("right_ankle", .6, .9),
        ]
    }
    frames = [{"frame_index": index, "landmarks": landmarks} for index in range(3)]
    details = [
        FrameAnalysis(
            frame_index=index, timestamp_sec=index / 10, knee_angle=100,
            hip_angle=80, trunk_angle=20, phase="depth",
            detected_issue="possible_knee_valgus" if index == 1 else None,
        ) for index in range(3)
    ]
    output = generate_skeleton_overlay(source, tmp_path / "overlay.webm", frames, details)
    assert output.stat().st_size > source.stat().st_size
    capture = cv2.VideoCapture(str(output))
    assert capture.isOpened()
    assert int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) == 3
    capture.release()
