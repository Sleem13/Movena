"""Non-diagnostic feedback for observed shoulder-abduction movement."""

DISCLAIMER = "AI feedback supports exercise monitoring and does not replace physiotherapist assessment."
MESSAGES = {
    "limited_observed_abduction_range": "The system observed limited shoulder abduction range in some repetitions.",
    "insufficient_range_of_motion": "Try to move the arm through a comfortable, clearly visible range away from the body.",
    "poor_visibility": "Ensure the camera captures the shoulder, elbow, wrist, and trunk clearly from the front.",
    "incomplete_repetition": "Return the arm to the lowered starting position before beginning the next repetition.",
    "inconsistent_tempo": "Try to keep the movement controlled as the arm moves away from and back toward the body.",
    "possible_trunk_compensation": "A possible trunk compensation pattern was observed; keep the trunk steady when comfortable.",
    "possible_shoulder_hiking_pattern": "Possible upward shoulder movement was observed; review the recording with a physiotherapist if needed.",
    "no_valid_shoulder_abduction_detected": "Please record the upper body from the front while completing lowered-raised-lowered arm movements.",
}


def build_shoulder_abduction_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed repetitions were completed with a generally controlled movement pattern.")
    feedback.append("Stop if you feel pain, dizziness, numbness, or unusual discomfort.")
    feedback.append(DISCLAIMER)
    return feedback
