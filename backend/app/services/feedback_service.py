DISCLAIMER = (
    "This analysis is for exercise monitoring and educational support only. "
    "It does not replace assessment by a licensed physiotherapist."
)


ISSUE_FEEDBACK = {
    "poor_depth": "Try to squat deeper only if it is pain-free and safe for your condition.",
    "excessive_trunk_lean": "Possible forward trunk lean was observed; try to keep your chest comfortably lifted.",
    "possible_knee_valgus": "Try to push your knees outward and keep them aligned with your toes.",
    "inconsistent_movement": "Move slowly and aim for a steady depth on each repetition.",
    "low_landmark_confidence": "Record in a well-lit space with your full body visible to improve tracking quality.",
}


def build_feedback(detected_issues: list[str]) -> list[str]:
    if not detected_issues:
        feedback = ["Good control. Keep your movement slow and stable."]
    else:
        feedback = [
            ISSUE_FEEDBACK[issue]
            for issue in detected_issues
            if issue in ISSUE_FEEDBACK
        ]

    feedback.append(DISCLAIMER)
    return feedback
