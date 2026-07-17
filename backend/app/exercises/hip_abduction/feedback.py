"""Non-diagnostic feedback for observed hip-abduction movement."""

DISCLAIMER = "AI feedback supports exercise monitoring and does not replace physiotherapist assessment."
MESSAGES = {
    "limited_observed_hip_abduction_range": "The system observed limited hip abduction range in some repetitions.",
    "insufficient_range_of_motion": "Try to move the leg through a comfortable, clearly visible range away from the body.",
    "poor_visibility": "Ensure the camera captures the pelvis, hip, knee, and ankle clearly from the front.",
    "incomplete_repetition": "Return the leg to the neutral starting position before beginning the next repetition.",
    "inconsistent_tempo": "Try to keep the movement controlled as the leg moves away from and back toward the body.",
    "possible_trunk_lean_compensation": "A possible trunk lean compensation pattern was observed; keep the trunk upright when comfortable.",
    "possible_pelvic_hiking_pattern": "Possible upward pelvic movement was observed; review the recording with a physiotherapist if needed.",
    "no_valid_hip_abduction_detected": "Please record the full lower body from the front while completing neutral-abducted-neutral leg movements.",
}


def build_hip_abduction_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed repetitions were completed with a generally controlled movement pattern.")
    feedback.append("Stop if you feel pain, dizziness, numbness, or unusual discomfort.")
    feedback.append(DISCLAIMER)
    return feedback
