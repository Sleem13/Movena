from app.exercises.upper_body_cyclic import (
    PUSH_UP_CONFIG,
    SHOULDER_PRESS_CONFIG,
    count_elbow_extension_cycles,
)
from app.schemas.analysis_schema import AnalysisResponse
from app.services.assisted_analysis_service import apply_assisted_exercise_fallback


def _cycle(values):
    return [value for value, count in values for _ in range(count)]


def test_push_up_counts_the_normal_extended_flexed_extended_order():
    angles = _cycle([
        (160, 4), (145, 2), (125, 2), (105, 4),
        (125, 2), (145, 2), (160, 4),
    ])
    result = count_elbow_extension_cycles(
        angles,
        timestamps=[index / 12 for index in range(len(angles))],
        config=PUSH_UP_CONFIG,
    )

    assert result.total_reps == 1
    assert result.rep_events[0].minimum_angle <= 110
    assert result.rep_events[0].maximum_angle >= 155
    assert result.phases[0] == "extended"


def test_shoulder_press_keeps_flexed_extended_flexed_order():
    angles = _cycle([
        (100, 4), (125, 2), (150, 2), (165, 4),
        (145, 2), (120, 2), (100, 4),
    ])
    result = count_elbow_extension_cycles(
        angles,
        timestamps=[index / 12 for index in range(len(angles))],
        config=SHOULDER_PRESS_CONFIG,
    )

    assert result.total_reps == 1
    assert result.phases[0] == "flexed"


def test_confident_different_exercise_is_analyzed_automatically(monkeypatch):
    class CandidateAnalyzer:
        def analyze_landmarks(self, frames, include_frame_data=False):
            assert frames
            assert include_frame_data is True
            return AnalysisResponse(
                exercise="push_up",
                exercise_id="push_up",
                exercise_name="Push-Up",
                status="success",
                movement_score=84,
                total_reps=3,
                summary="Three push-ups were assessed.",
            )

    monkeypatch.setattr(
        "app.services.assisted_analysis_service.extract_mediapipe_sequence_features",
        lambda frames: [{"feature": 1.0}],
    )
    monkeypatch.setattr(
        "app.services.assisted_analysis_service.predict_exercise_from_sequence",
        lambda sequence: {
            "status": "success",
            "suggested_exercise_id": "push_up",
            "confidence": 0.86,
            "confidence_threshold": 0.64,
            "top_predictions": [
                {"exercise_id": "push_up", "confidence": 0.86},
                {"exercise_id": "bodyweight_squat", "confidence": 0.08},
            ],
        },
    )
    monkeypatch.setattr(
        "app.services.assisted_analysis_service.registry.available_exercises",
        lambda: ("bodyweight_squat", "push_up"),
    )
    monkeypatch.setattr(
        "app.services.assisted_analysis_service.registry.get",
        lambda exercise_id: CandidateAnalyzer(),
    )
    rejected = AnalysisResponse(
        exercise="bodyweight_squat",
        exercise_id="bodyweight_squat",
        exercise_name="Bodyweight Squat",
        status="rejected",
        movement_score=None,
    )

    result = apply_assisted_exercise_fallback(
        "bodyweight_squat", rejected, [{"landmarks": {}}], include_frame_data=True
    )

    assert result.status == "success"
    assert result.exercise_id == "push_up"
    assert result.auto_routed is True
    assert result.selected_exercise_id == "bodyweight_squat"
    assert result.recognized_exercise_id == "push_up"
    assert result.recognition_confidence == 0.86
    assert "recognized" in result.recognition_message.lower()


def test_uncertain_recognition_does_not_switch_analyzers(monkeypatch):
    monkeypatch.setattr(
        "app.services.assisted_analysis_service.extract_mediapipe_sequence_features",
        lambda frames: [{"feature": 1.0}],
    )
    monkeypatch.setattr(
        "app.services.assisted_analysis_service.predict_exercise_from_sequence",
        lambda sequence: {
            "status": "uncertain",
            "suggested_exercise_id": "push_up",
            "confidence": 0.52,
            "confidence_threshold": 0.64,
            "top_predictions": [
                {"exercise_id": "push_up", "confidence": 0.52},
                {"exercise_id": "shoulder_press", "confidence": 0.48},
            ],
        },
    )
    rejected = AnalysisResponse(
        exercise="bodyweight_squat",
        exercise_id="bodyweight_squat",
        status="rejected",
        movement_score=None,
    )

    result = apply_assisted_exercise_fallback(
        "bodyweight_squat", rejected, [{"landmarks": {}}]
    )

    assert result is rejected
    assert result.auto_routed is False
    assert result.recognition_status == "suggestion_needs_confirmation"
