# Analysis Confidence Design

`analysis_confidence` describes how trustworthy the available measurements are. It is intentionally separate from `movement_score`, which summarizes the rule-based movement observations.

The confidence score combines pose quality (45%), rep-count confidence (25%), smoothed angle stability (20%), and camera-view suitability (10%). Levels are high at 0.80 or above, medium from 0.60 to below 0.80, and low below 0.60. Reasons expose the major factors. Warnings identify low tracking coverage, weak critical-joint visibility, side-view limitations for valgus, irregular cycles, or experimental-ML disagreement.

Pose quality combines detection rate, overall visibility, critical-landmark visibility, and low-confidence-frame rate. A low score does not automatically fail analysis; it produces cautious warnings and lowers confidence. Camera-view classification is a coarse 2D heuristic and must not be treated as a validated view detector.

When optional ML is enabled, confidence below 0.65 is labelled low. A disagreement adds: “The experimental ML prediction disagrees with rule-based analysis. Rule-based biomechanical feedback remains primary.” It never changes the rule-derived movement score, issues, or feedback.

## Validity gate

Analysis confidence does not make an invalid recording valid. Before movement scoring, `input_validity` requires at least 30 pose-detected frames, 50% pose coverage during the contiguous movement segment, 50% critical-landmark visibility, 30° knee range, 20° hip range, measurable temporal variation, and at least one complete squat cycle. Whole-video pose coverage remains available separately so long intros or outros can lower confidence without automatically invalidating a well-tracked active segment. A failed gate forces confidence to `low`, adds validation warnings, sets `movement_score` to null, and prevents ML inference. Static/profile images encoded as video are expected to fail motion, angle-range, or completed-repetition checks.
