from app.exercises.hip_abduction.feedback import build_hip_abduction_feedback


def test_feedback_avoids_diagnostic_wording():
    text = " ".join(build_hip_abduction_feedback(["limited_observed_hip_abduction_range", "possible_trunk_lean_compensation"])).lower()
    assert "observed" in text
    assert "does not replace physiotherapist assessment" in text
    assert all(word not in text for word in ("hip weakness", "gluteus medius weakness", "instability", "injury"))
