"""Non-diagnostic feedback for observed shoulder-flexion movement."""

DISCLAIMER = "AI feedback supports exercise monitoring and does not replace physiotherapist assessment."
MESSAGES = {
    "limited_observed_flexion_range": "The system observed limited shoulder-flexion range in some repetitions.",
    "insufficient_range_of_motion": "Try to move the arm forward through a comfortable, clearly visible range.",
    "poor_visibility": "Ensure the camera captures the shoulder, elbow, wrist, and trunk clearly.",
    "incomplete_repetition": "Return the arm to the lowered starting position before beginning the next repetition.",
    "inconsistent_tempo": "Try to keep the movement controlled as the arm raises and lowers.",
    "possible_trunk_compensation": "A possible trunk compensation pattern was observed; keep the trunk steady when comfortable.",
    "possible_shoulder_hiking_pattern": "Possible upward shoulder movement was observed; review the recording with a physiotherapist if needed.",
    "possible_elbow_bend_pattern": "The 2D view suggests the elbow may be bending during some repetitions.",
    "no_valid_shoulder_flexion_detected": "Please record the upper body while completing lowered-raised-lowered forward arm raises.",
}


def build_shoulder_flexion_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed repetitions were completed with a generally controlled shoulder-flexion movement pattern.")
    feedback.append("Stop if you feel pain, dizziness, numbness, or unusual discomfort.")
    feedback.append(DISCLAIMER)
    return feedback
