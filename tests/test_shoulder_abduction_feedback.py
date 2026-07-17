from app.exercises.shoulder_abduction.feedback import build_shoulder_abduction_feedback


def test_feedback_avoids_diagnostic_wording():
    text = " ".join(build_shoulder_abduction_feedback(["limited_observed_abduction_range", "possible_trunk_compensation"])).lower()
    assert "observed" in text
    assert "does not replace physiotherapist assessment" in text
    assert all(word not in text for word in ("impingement", "rotator cuff weakness", "injury", "frozen shoulder"))
