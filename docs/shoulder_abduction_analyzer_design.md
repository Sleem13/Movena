# Shoulder Abduction Analyzer Design

The preferred input is a stable front view showing both shoulders and the selected shoulder, elbow, wrist, and hip. The analyzer selects the better-visible arm. The observed abduction angle is the 2D angle between the shoulder-to-hip trunk reference and shoulder-to-elbow upper-arm line.

A repetition progresses through stable lowered, raising, stable raised, lowering, and return-to-lowered states. Smoothing, debouncing, frame-gap resets, timing limits, minimum visible range, and partial-cycle accounting reduce noisy counts.

The validity gate requires sufficient pose frames, detection rate, selected-joint visibility, at least 45 degrees of observed angle range, and a complete cycle. Invalid recordings receive `INVALID_SHOULDER_ABDUCTION_VIDEO`, zero reps, and no score. Valid sessions receive components for observed abduction range, control, consistency, visibility, and rep completion.

The 2D system cannot determine pain, injury, impingement, frozen shoulder, muscle weakness, passive range, joint loading, or treatment suitability. Results support educational movement monitoring and do not replace physiotherapist assessment.
