# Hip Abduction Analyzer Design

The MVP supports standing hip abduction from a stable front view. It requires both hips plus the selected shoulder, hip, knee, and ankle. The analyzer compares both legs using visibility and observed motion amplitude, then analyzes the stronger candidate.

The observed abduction angle is the deviation of the hip-to-ankle leg line from the shoulder-to-hip trunk reference. A repetition progresses through stable neutral, abducting, stable abducted, returning, and return-to-neutral states. Smoothing, phase debouncing, frame-gap resets, timing limits, range requirements, and partial-cycle accounting reduce noisy counts.

The validity gate requires sufficient pose frames, detection rate, selected landmarks, at least 18 degrees of observed range, and a complete neutral-abducted-neutral cycle. Invalid recordings receive `INVALID_HIP_ABDUCTION_VIDEO`, zero reps, and no score.

Valid scores describe observed abduction range, control, consistency, visibility, rep completion, and approximate pelvis/trunk stability. The 2D system cannot determine strength, instability, injury, pain source, balance capacity, joint loading, or treatment suitability.
