"""Non-diagnostic feedback for observed walking gait."""

DISCLAIMER = "AI feedback supports gait monitoring and does not replace physiotherapist assessment."

MESSAGES = {
    "insufficient_gait_cycles": "Record a longer walking pass with at least two visible gait cycles from the same side.",
    "poor_visibility": "Keep the hips, knees, ankles, heels, and toes visible for both legs throughout the walk.",
    "stance_swing_outside_reference": "The stance/swing timing estimate was outside the usual adult walking reference band; review the video quality and walking task.",
    "asymmetric_timing": "A left-right timing difference was observed. Recheck with a clear side-view recording and review with a clinician when relevant.",
    "inconsistent_stride_timing": "Stride timing varied between cycles; repeat with a steady, comfortable pace when safe.",
    "low_cadence": "Cadence appeared low for a comfortable adult walking screen. Interpret cautiously without a measured walkway distance.",
    "high_cadence": "Cadence appeared high for a comfortable adult walking screen. Confirm the recording frame rate and walking task.",
    "limited_knee_motion": "The visible knee-angle range was limited during walking; this can reflect camera angle, clothing, pace, or movement strategy.",
    "no_valid_gait_detected": "Please record a side-view walking pass with the full lower body and several clear steps visible.",
}


def build_gait_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed walking pass had generally consistent timing and visible lower-limb motion.")
    feedback.append("Stop walking analysis if pain, dizziness, loss of balance, or unusual symptoms occur.")
    feedback.append(DISCLAIMER)
    return feedback

