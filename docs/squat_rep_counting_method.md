# Squat Repetition Counting Method

The counter operates on the average left/right knee angle. Non-finite samples are interpolated, isolated spikes are suppressed with a centered rolling median, and residual jitter is reduced with a short moving average. The output length remains identical to the input.

## State machine

1. **Standing:** knee angle is near or above 160°.
2. **Descending:** angle is decreasing below standing.
3. **Bottom:** angle reaches 115° or less after at least 35° of excursion. Normal recordings require at least two bottom frames.
4. **Ascending:** angle rises from the bottom.
5. **Standing:** returning to at least 160° completes the repetition.

A completed event must have a plausible duration of 0.8–8.0 seconds when timestamps are available and must respect the ten-frame separation rule. Incomplete cycles, premature returns, implausible durations, and repeated descents are reported as `ignored_partial_reps`. Very short legacy/test clips without usable timing use a conservative compatibility path because they cannot support duration validation.

The response includes event start, bottom, and end frames; minimum knee angle; duration when available; ignored partial cycles; and `rep_count_confidence`. This is a signal-processing confidence estimate, not a clinical quality rating.

## Scoring eligibility

Rep completion and squat depth are separate concepts. A completed movement cycle may be counted as an attempt after sufficient excursion even when it does not reach the 115° depth-quality threshold; this allows a valid shallow squat to receive `poor_depth`. A recording with zero completed cycles is rejected instead of being scored as poor depth. Static or near-static recordings therefore receive no movement score and cannot be sent to the optional ML classifier.
