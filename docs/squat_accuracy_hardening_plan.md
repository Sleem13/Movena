# Squat Accuracy and Confidence Hardening Plan

## Baseline findings

The previous analyzer counted a repetition whenever knee angle crossed below 110 degrees and later crossed above 160 degrees. It did not require descent, bottom, ascent, minimum excursion, plausible duration, spacing, or a completed return to standing. Raw frame angles were used directly. The movement score started at 100 and applied fixed deductions: poor depth 20, trunk lean 20, possible valgus 20, inconsistency 10, and low landmark confidence 10.

Likely failure causes were landmark jitter crossing thresholds, partial movements being counted, missing pose frames being invisible to the analyzer, whole-video trunk averages, side-view valgus evidence receiving the same weight as front-view evidence, and a movement score that did not express evidence strength.

## Implemented hardening

- Median-plus-moving-average angle smoothing with finite-value interpolation.
- A standing → descending → bottom → ascending → standing state machine.
- Reviewable thresholds: standing 160°, bottom 115°, minimum excursion 35°, 0.8–8.0 second duration, ten-frame spacing, and a two-frame bottom hold for normal recordings.
- Pose detection coverage and visibility scoring over shoulders, hips, knees, ankles, heels, and foot indices.
- Explainable depth, knee-alignment, trunk-control, consistency, and pose-confidence sub-scores.
- Separate movement and analysis-confidence outputs.
- Explicit experimental-ML confidence and disagreement handling; ML never changes rule-based issues or feedback.
- Friendly UI confidence, pose-quality, rep-confidence, and score-breakdown presentation.

## Non-goals

No new exercises, deep-learning training, clinical validation claim, authentication, database redesign, or replacement of the rule-based analyzer is included. The optional SVC remains an experimental second opinion.

## Acceptance criteria

The hardening is accepted when clean and noisy synthetic eight-rep signals count eight reps; partial and tiny movements do not count; low visibility lowers confidence; scoring sub-components respond in the expected direction; ML disagreement preserves rule output; existing backend and frontend tests pass; and the API/documentation expose the new fields and limitations.

## Custom-video counter comparison

The read-only comparison over the current processed angle CSV found 24 video sequences. The legacy threshold counter produced 161 crossings, while the hardened counter accepted 33 completed, duration-valid cycles. Most of the reduction came from long instructional/compilation videos with cuts and repeated threshold jitter; for example, one knee-valgus explainer changed from 96 threshold crossings to 9 completed cycles. The direct custom numbered clips changed from 16 to 10 accepted cycles overall.

These labels describe squat category, not manually verified rep totals. Therefore this comparison demonstrates stricter rejection of partial/noisy cycles, not measured counting accuracy. A frame-reviewed rep-count ground truth is still required before claiming sensitivity or error-rate improvement. Run `python scripts/compare_squat_rep_counters.py` to reproduce the audit.
