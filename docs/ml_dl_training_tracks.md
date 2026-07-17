# ML/DL Training Tracks

Pose estimation, biomechanics interpretation, and clinical decision-making are different layers. Pretrained pose models locate landmarks; they do not independently validate exercise quality or make clinical decisions. Rule-based biomechanics remains the primary product layer while all ML/DL tracks are experimental.

## Track A — Video Pose Feature ML

- Inputs: video files processed into MediaPipe landmarks, joint angles, temporal summaries, and quality metadata.
- Methods: classic ML baselines such as logistic regression, random forest, SVM, and gradient boosting.
- Use: current video-based exercise quality experiments and optional second opinions.
- Boundary: participant-grouped evaluation and complete labels are required; ML cannot override validity or rules.

## Track B — Skeleton Sequence DL

- Inputs: ordered 2D/3D skeleton sequences with timestamps and confidence.
- Methods: LSTM, GRU, temporal CNN, and transformer candidates.
- Use: future exercise recognition, phase recognition, and movement-quality research.
- Boundary: landmark definitions, coordinates, sequence handling, and participant splits must be normalized and documented.

## Track C — Sensor Time-Series ML/DL

- Inputs: IMU, accelerometer, gyroscope, force, or other sampled signals.
- Methods: statistical feature ML, 1D CNN, LSTM, and GRU candidates.
- Use: sensor-specific activity or movement research.
- Boundary: sensor data is not directly mixed with video; sampling rate, placement, calibration, and units require dedicated adapters.

## Track D — Image/Pose Static Analysis

- Inputs: still images or isolated frames and extracted static geometry.
- Use: bounded posture or capture-quality research.
- Boundary: static samples are not evidence for rep counting or temporal movement quality.

## Track E — Future Multi-Modal Fusion

- Inputs: synchronized video, skeleton, and sensor streams.
- Status: research-only until each independent track is reliable and sufficient synchronized data, participant-grouped validation, missing-modality handling, and safety review exist.

## Non-negotiable data rule

Do not blindly merge video, skeleton, sensor, image, and tabular datasets into one model. Every source first requires modality, provenance, licensing, taxonomy, participant, leakage, quality, and training-readiness review through a dataset-specific adapter.

## Sprint 15 routing status

Named adapters now route video/image, skeleton, sensor, and tabular artifacts to their matching research tracks. Mixed Rehab24-6 samples are classified per file where the folder and extension provide evidence. Unknown exercise codes remain excluded from training candidates. A technically compatible modality is not sufficient: reviewed labels and participant-grouped splits remain mandatory for serious evaluation.
