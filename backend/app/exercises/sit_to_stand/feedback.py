"""Safety-aware, non-diagnostic sit-to-stand feedback."""

DISCLAIMER = "This feedback is for exercise monitoring and educational support only. It does not replace assessment by a licensed physiotherapist."

MESSAGES = {
    "incomplete_stand": "Try to stand up fully before sitting back down.",
    "excessive_trunk_lean": "Try to keep your trunk controlled as you rise.",
    "fast_uncontrolled_movement": "Move with steady control instead of rushing the movement.",
    "poor_control": "Use a steady, comfortable pace through both rising and lowering.",
    "low_confidence_tracking": "Keep the hips, knees, ankles, shoulders, and chair visible throughout the recording.",
    "no_valid_sit_to_stand_detected": "Please upload a video showing the full body or lower body performing repeated sit-to-stand repetitions.",
}


def build_sit_to_stand_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("Continue using a steady, controlled movement pace when comfortable.")
    feedback.append("Use a stable chair and stop if you feel pain, dizziness, or unusual discomfort.")
    feedback.append(DISCLAIMER)
    return feedback
