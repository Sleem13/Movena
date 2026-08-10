# Exercise Pose Recognition Model Card

## Status

Development-candidate contract. Trained artifacts may be exposed as optional suggestions when their measured validation evidence is present.

## Intended Use

Suggest a likely exercise label from compatible 2D body-pose features and ask the user to confirm. Recognition is a routing aid only.

## Prohibited Use

- Automatic analyzer selection or execution.
- Form assessment, diagnosis, treatment, injury-risk, recovery, or safe-load decisions.
- Feedback for an exercise without an active rule-based analyzer.
- Overriding invalid-input, pose-quality, or safety behavior.

## Input

The frame classifier accepts forty ordered numeric features derived from 17 body keypoints: normalized x/y coordinates plus bilateral knee, hip, and elbow angles. The temporal classifier accepts an ordered pose sequence, resamples it to 64 frames, and applies the same feature contract at each step. Runtime MediaPipe landmarks are explicitly mapped to the trained COCO-17 ordering before feature extraction. The pose-backend and feature-contract versions must match training.

## Output

Top exercise suggestions with calibrated confidence, analyzer availability, and `requires_manual_confirmation=true`. The temporal candidate returns `status=uncertain` below its validation-derived acceptance threshold and prevents suggestion confirmation. Incompatible features fail safely.

## Operational Controls

- Normal inference uses the explicitly configured `ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID` or `ACTIVE_FRAME_RECOGNITION_MODEL_ID`; directory ordering never chooses a model.
- Artifact metadata includes the artifact byte size and SHA-256 digest.
- Startup verifies the pinned artifact ID, hash, feature/class contract, normalization vectors, calibration values, loadability, and output shape using smoke inference.
- Invalid pinned artifacts disable recognition in development and test environments. Staging and production startup fail closed.
- Successful and uncertain recognition results create a `recognition_events` audit row. It contains model ID, predicted label, confidence, threshold, abstention, analyzer availability, source type, usable-pose-frame count, confirmation, and timestamps.
- Recognition audit rows never contain uploaded video bytes, a storage path, the original filename, or pose sequences.

## Known Limitations

- The XGBoost frame classifier omits movement timing; the GRU candidate models temporal order at video level.
- Body pose does not reliably observe hand orientation.
- Video grouping is not participant grouping.
- Camera view, demographics, body shape, mobility, clothing, assistive devices, occlusion, and recording environment can shift performance.
- An exercise label does not imply a valid repetition or appropriate movement execution.
- Push-up, shoulder-press, and bicep-curl suggestions may be confirmed into their dedicated rule-based analyzers; recognition confidence is never used as form evidence.

## Required Evidence

Use the promotion gates in `docs/exercise_coaching_adoption_plan.md`. Every concrete artifact must supply its own metadata, metrics, split manifest, classification report, dependency versions, provenance, and rollback behavior. Current artifacts use the `candidate` status rather than a research-only designation; their validation scope remains explicit.

## Current Candidates

### XGBoost frame classifier

- Model ID: `exercise_pose_xgb_20260809T154328Z`
- Holdout: 23 videos, disjoint from 90 training videos
- Accuracy: 0.746367
- Macro F1: 0.731121
- Weakest recall: Hammer Curl at 0.253369

### Bidirectional GRU temporal classifier

- Model ID: `exercise_pose_gru_20260809T161346Z`
- Split: 67 training, 23 validation, and 23 holdout videos
- Holdout accuracy: 0.826087
- Holdout macro F1: 0.835556
- Holdout Hammer Curl recall: 0.75
- Export: TorchScript, 64-frame normalized pose sequence
- Calibration: validation-only temperature scaling, temperature 0.519353
- Acceptance threshold: 0.635556, selected for at least 0.85 validation selective accuracy
- Validation accepted coverage / selective accuracy: 0.608696 / 0.857143
- Holdout accepted coverage / selective accuracy: 0.652174 / 0.933333
- Holdout abstention rate: 0.347826
- Holdout expected calibration error: 0.261032 before scaling, 0.103697 after scaling

Both artifacts are registered as development candidates and are available to the optional suggestion API. Their video groups are disjoint, but participant-independent performance cannot be calculated because the source table has no participant identifiers.

Inference endpoints are `POST /api/v1/recognition/exercise` for prepared features or sequences and `POST /api/v1/recognition/video` for a validated temporary video upload. `POST /api/v1/recognition/confirm` records the user's confirmed label against the generated event ID before analyzer routing. The video endpoint extracts MediaPipe landmarks, maps them to the COCO-17 contract, calls the calibrated temporal candidate, and removes the upload after processing. Calibration and threshold selection use only the validation split; the holdout figures above are evaluation results, not threshold-tuning inputs.
