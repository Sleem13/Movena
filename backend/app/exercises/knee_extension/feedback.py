"""Non-diagnostic feedback for observed knee-extension movement."""

DISCLAIMER = "AI feedback supports exercise monitoring and does not replace physiotherapist assessment."

MESSAGES = {
    "limited_knee_extension": "The system observed limited extension range in some repetitions.",
    "insufficient_range_of_motion": "Try to move through a comfortable, clearly visible flexion-to-extension range.",
    "poor_visibility": "Ensure the camera captures the hip, knee, and ankle clearly from the side.",
    "incomplete_repetition": "Complete the extension and return to the flexed starting position before the next repetition.",
    "inconsistent_tempo": "Try to keep the movement controlled through the full range.",
    "possible_compensation": "A possible compensation pattern was observed; keep the seated posture steady when comfortable.",
    "no_valid_knee_extension_detected": "Please record the lower limb from the side while completing flexion-extension-flexion repetitions.",
}


def build_knee_extension_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed repetitions were completed with a generally controlled movement pattern.")
    feedback.append("Stop if you feel pain, dizziness, or unusual discomfort.")
    feedback.append(DISCLAIMER)
    return feedback

