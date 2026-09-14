# Recovery engine v2 research track

This package is isolated from request handlers and the production engine. It
defines reviewed, participant-separated training inputs and a fail-closed model
promotion gate. Nothing in this directory is automatically promoted or used to
produce patient feedback.

`python -m unittest discover -s engines/recovery/tests` runs boundary tests without
PyTorch. `training.py` requires NumPy, scikit-learn, XGBoost and PyTorch from the
existing ML environment. Train only against an explicit manifest; never turn
unreviewed labels or generated test fixtures into training evidence.

The initial candidates are a temporal convolution classifier over 33-landmark
sequences and a boosted-tree classifier over sequence statistics. Recognition
and movement-quality are separate tasks. Repetition evaluation, rejection tests,
and decision-support evaluation remain required before any deployment.

Manifest JSON: `task` (`recognition` or `movement_quality`), `labels` (ordered class
names), and `samples` containing `sample_id`, `participant_id`, `split` (`train`,
`validation`, `holdout`), `features` (relative `.npy` path with T×33×4 coordinates
and visibility), `label`, `reviewed: true`, `source`, and `license_id`.
All samples from a participant must share one split. The feature path must stay
inside the manifest directory. Every split must include every class.
The manifest must record `coordinate_space: "world"`, `pose_backbone_version`,
and a reviewed `min_anchor_visibility` in (0, 1]. Training rejects image/world
ambiguity, out-of-range visibility and unreliable hip/shoulder normalization
anchors. These checks do not replace task-specific label and validity review.

Training never evaluates the holdout. Select candidates on validation data, freeze
them, and evaluate the holdout separately. Promotion requires signed-off paired
benchmark evidence; the gate does not establish clinical validity.

`processing.py` adds unpromoted 33-landmark geometry and streaming full-cycle
primitives. Image coordinates require source dimensions and use a 2D angle;
world coordinates use a 3D angle. This distinction follows the [MediaPipe output
contract](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python#handle_and_display_results).
Missing landmarks remain unavailable. Stable endpoint dwell, hysteresis and
duration limits are supplied in an explicit versioned protocol; there are no
default exercise thresholds. A missing frame resets the current partial cycle;
large time gaps reject the recording. Rejected/error results carry no repetition
count or quality score. A valid still signal can return a measured zero.

The tests use synthetic angles to check mechanics only. These primitives are not
connected to the API, pose extraction, candidate training or patient feedback.
Task-specific protocols, robustness to camera/body variation, labels and paired
video benchmarks must be implemented and reviewed before promotion. Static
balance and gait are not implicitly treated as repeated-joint-angle tasks.
