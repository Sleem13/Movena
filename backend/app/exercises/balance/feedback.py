"""Non-diagnostic balance feedback."""

DISCLAIMER = "AI feedback supports balance monitoring and does not replace physiotherapist assessment."

MESSAGES = {
    "short_balance_hold": "The visible balance hold was short. Repeat with a longer steady hold only if it is safe.",
    "excessive_postural_sway": "The body position moved more than expected for a steady hold; review the recording and support setup.",
    "high_sway_velocity": "The body position changed quickly during the hold, which may indicate movement corrections or noisy tracking.",
    "possible_trunk_lean": "A possible trunk lean pattern was observed. Keep the trunk upright when comfortable and safe.",
    "possible_pelvic_drop_or_hike": "A possible pelvic drop or hike pattern was observed; compare both sides with a professional if relevant.",
    "variable_stance_knee": "The stance knee angle varied during the hold; try a comfortable steady knee position when safe.",
    "foot_adjustment_detected": "A possible foot adjustment was observed. Repeat with a clear fixed stance if balance testing is intended.",
    "poor_visibility": "Keep shoulders, hips, knees, ankles, heels, and toes visible throughout the hold.",
    "no_valid_balance_detected": "Please record a static standing balance hold with the full body visible.",
}


def build_balance_feedback(issues: list[str]) -> list[str]:
    feedback = [MESSAGES[issue] for issue in issues if issue in MESSAGES]
    if not feedback:
        feedback.append("The observed hold showed generally steady visible posture in this recording.")
    feedback.append("Use a safe support surface nearby and stop if pain, dizziness, imbalance, or unusual symptoms occur.")
    feedback.append(DISCLAIMER)
    return feedback

