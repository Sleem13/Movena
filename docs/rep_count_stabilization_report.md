# Sprint 6.6 Rep Count Stabilization Report

## Current issue and root causes

A valid recording was reported as two complete reps, 29 ignored partials, and 0.298 confidence. The previous state machine incremented the partial counter on every premature return to standing and every re-descent during ascent. Bottom/ascent jitter could therefore generate many pseudo-partials from one continuous attempt. Preprocessing also interpolated every missing value, did not reject isolated angle spikes, and did not break continuity at long frame gaps.

## Implemented improvements

- Joint angles outside 20–180° become missing samples.
- Isolated adjacent jumps above 45° are removed.
- Gaps of at most three frames are interpolated; longer gaps break continuity.
- Low-confidence pose frames are excluded before smoothing.
- Rolling-median and moving-average filters operate independently within valid segments.
- Sustained phase evidence, bottom hysteresis, 40° excursion, plausible duration, and an inclusive 12-frame cooldown are required.
- Only meaningful movement of at least 20° can create a partial event.
- Partial candidates are aggregated within between-rep intervals and capped at three review events.
- Confidence combines complete-rep ratio, pose quality, angle stability, transition clarity, and duration consistency.

## Before/after evidence

| Sequence | Reps before | Reps after | Partials before | Partials after | Confidence before | Confidence after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Long knee-valgus instructional clip | 8 | 8 | 38 | 3 | 0.647 | 0.813 |
| Four-rep instructional clip | 4 | 4 | 7 | 2 | 0.677 | 0.768 |
| `squat_correct_001.mp4` API validation | 1 | 1 | 0 | 0 | not directly comparable | 0.861 |

The originally reported two-rep upload was not identified by a durable session ID or filename, so its exact after value cannot be claimed. It should be rerun through the current endpoint.

## Manual validation status

`data/processed/labels/custom_squat_manual_rep_counts.csv` was generated for 24 videos. Expected counts remain blank pending frame-reviewed human annotation, so mean absolute error and the percentage within ±1 rep are not yet available. Run `python scripts/validate_rep_counts.py` after entering expected counts.

## Limitations and recommendation

Edited instructional videos contain cuts, demonstrations, and non-set movement and are not reliable rep-count accuracy benchmarks. The three-event cap represents aggregated review intervals, not a claim that only three incomplete movements occurred. Sprint 7 can begin as dataset/annotation work; threshold expansion should wait for manual expected counts and error review.
