# Squat Repetition Counting Method

The counter operates on the average left/right knee angle. Values outside 20–180°, non-finite samples, low-confidence frames, and isolated jumps over 45° are removed. Internal gaps up to three frames are interpolated; longer gaps break continuity. Each valid segment then receives centered rolling-median and moving-average smoothing. The display output retains one value per detected frame, while the state machine respects continuity breaks.

## State machine

1. **Standing:** at least three consecutive frames are near or above 158°.
2. **Descending:** angle decreases after confirmed standing for at least three phase frames.
3. **Bottom:** an attempt reaches at most 140° after at least 40° of excursion and holds bottom evidence for two frames. The stricter 115° threshold remains the depth-quality rule.
4. **Ascending:** angle rises at least 8° from the tracked minimum; bottom jitter remains in the same candidate.
5. **Standing:** returning to at least 158° completes the repetition.

A completed event must have a plausible duration of 0.8–8.0 seconds when timestamps are available and must respect an inclusive 12-frame cooldown.

## Partial movements

A partial is recorded only after at least 20° of meaningful movement. Reasons are `did_not_reach_depth`, `did_not_return_to_standing`, `too_short`, `too_long`, or `low_confidence_segment`. Repeated candidates in the same between-rep interval are aggregated and no more than three review events are returned. Consequently, `ignored_partial_reps` describes aggregated review intervals rather than every noisy threshold transition.

The response includes completed event start, bottom, and end frames; minimum knee angle; duration when available; `partial_rep_events`; ignored aggregated partial cycles; and `rep_count_confidence`. Confidence combines complete-rep ratio, pose quality, angle stability, transition clarity, and duration consistency. It is a signal-processing confidence estimate, not a clinical quality rating.

## Scoring eligibility

Rep completion and squat depth are separate concepts. A completed movement cycle may be counted as an attempt after sufficient excursion even when it does not reach the 115° depth-quality threshold; this allows a valid shallow squat to receive `poor_depth`. A recording with zero completed cycles is rejected instead of being scored as poor depth. Static or near-static recordings receive no movement score and cannot be sent to the optional ML classifier.

## Manual validation

Run `python scripts/validate_rep_counts.py`. On first run it creates `data/processed/labels/custom_squat_manual_rep_counts.csv`. Enter frame-reviewed `expected_reps` values and rerun to generate CSV and Markdown results under `reports/rep_count_validation/`.
