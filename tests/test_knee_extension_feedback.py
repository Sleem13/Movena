from app.exercises.knee_extension.feedback import build_knee_extension_feedback


def test_feedback_is_observational_and_includes_safety_boundary():
    text = " ".join(build_knee_extension_feedback(["limited_knee_extension", "possible_compensation"])).lower()
    assert "observed" in text
    assert "does not replace physiotherapist assessment" in text
    assert all(word not in text for word in ("diagnosis", "injury", "weakness", "stiffness"))
