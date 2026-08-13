# Exercise Coaching and Recognition Adoption Plan

## Decision

PhysioVision AI extends its existing exercise engine rather than importing a second application architecture. Eight rule-based development analyzers now exist; push-up, shoulder press, and bicep curl are conservative MVP additions and are not approved for the external-beta allowlist. Exercise recognition is suggestion-only, manual selection remains primary, and no planned movement can run until its own validity, phase, scoring, confidence, safety, and review gates pass.

New code, APIs, model IDs, UI labels, and artifacts use PhysioVision terminology. External research inputs retain provenance only in controlled dataset records; they are not used as product branding.

## Implemented Foundation

- A shared 17-keypoint, 40-feature pose contract: 34 normalized coordinates plus six bilateral knee, hip, and elbow angles.
- Confidence and critical-landmark rejection before feature generation.
- A conservative adapter for externally stored exercise-pose frame tables.
- A reproducible feature-preparation command with label normalization and video group IDs.
- A video-grouped XGBoost training command that writes JSON model artifacts, metadata, metrics, classification evidence, and a model card.
- A stratified video-sequence bidirectional GRU with temporal attention, early stopping, TorchScript export, validation-only temperature scaling, calibrated abstention, and disjoint train/validation/holdout video manifests.
- Optional backend loading of versioned XGBoost JSON artifacts without making XGBoost a normal production dependency.
- Dynamic analyzer availability based on the actual exercise registry.
- Conservative rule-based push-up and shoulder-press analyzers with separate geometry, validity, temporal counting, scoring, feedback, API, overlay, report, and session contracts.
- A synthetic-only bicep-curl analyzer with extended-flexed-extended counting, upright-position rejection, upper-arm/trunk observations, and explicit grip/load limitations.
- Product metadata for hammer curl as a disabled recognition candidate.
- Exercise Library and Coaching Lab UI states that distinguish supported analysis from recognition candidates.
- Explicit active-model pins, artifact SHA-256 verification, startup contract/smoke checks, and fail-closed staging/production startup.
- Privacy-safe recognition audit events and explicit confirmation recording without retaining uploaded video, filenames, or pose sequences.

## Data Contract

The input table must contain `workout_type`, `video_name`, and 17 keypoints with `x`, `y`, and `conf` values. The preparation pipeline:

1. Requires at least 10 visible keypoints at confidence 0.3 or greater.
2. Requires both shoulders and both hips.
3. Centers coordinates at the mid-hip.
4. Scales by mid-hip-to-mid-shoulder distance.
5. Computes left/right knee, hip, and elbow angles.
6. Preserves video identity as `group_id`.
7. Leaves participant identity missing rather than inferring it from video names.

Prepared frame rows are correlated observations, not independent participant samples. Video-grouped evaluation reduces direct frame leakage but does not replace a participant-grouped holdout.

## Model Contract

Each model lives below `models/recognition/<model_id>/` and contains:

- `model.json` for XGBoost or `model.pt` for TorchScript
- `metadata.json`
- `metrics.json`
- `classification_report.json`
- `model_card.md`

The service accepts existing joblib baselines, `xgboost_json` frame candidates, and `torchscript_sequence` temporal candidates. Runtime selection uses configured active model IDs rather than the newest artifact directory. A model may return top predictions, confidence, analyzer availability, and a manual-confirmation requirement. It cannot auto-route, activate a planned analyzer, score form, or override a validity rejection.

The current trained candidates are `exercise_pose_xgb_20260809T154328Z` and `exercise_pose_gru_20260809T161346Z`. The GRU achieved 0.826087 holdout accuracy and 0.835556 macro F1 on 23 held-out videos. Its validation-derived 0.635556 threshold accepted 60.87% of validation videos at 85.71% selective accuracy; on untouched holdout data it accepted 65.22% at 93.33% selective accuracy and abstained on 34.78%. Artifact-specific metrics, calibration evidence, and split manifests are stored beside each model.

The recognition API accepts prepared frame/sequence payloads and temporary video uploads. Runtime MediaPipe output is mapped explicitly to COCO-17 ordering before the shared 40-feature contract is applied; uploaded files follow the existing validation and cleanup path.

The Analyze page provides the primary recognition flow beside manual selection: select a short video, request temporal recognition, review ranked calibrated confidence values, and explicitly confirm a supported suggestion above the acceptance threshold without leaving `/analyze`. The confirmation is saved against the recognition event before the detected exercise is selected. The browser keeps the user-selected `File` in transient in-memory state and carries it into the confirmed analyzer, so the user does not need to choose the same file again; the recognition audit path still stores no raw video or filename. Uncertain results and recognized labels without active analyzers cannot be confirmed or routed. This Analyze-page workflow is independent of the optional Coaching Lab feature flag; model readiness determines whether its recognition action can run.

Mobile now follows the same contract through its Exercise Library: **Identify Exercise from Video** opens a dedicated native route, accepts an existing or newly recorded clip, checks for an active integrity-valid temporal model, displays ranked suggestions, records confirmation, and carries the same transient video into one of the eight registered analyzers. Manual selection remains available throughout. Mobile also maps `SUBJECT_SWITCH_DETECTED` to single-person re-recording guidance.

## Subject Identity Safety

The current MediaPipe pipeline is single-subject. Before recognition, rep counting, scoring, report creation, or overlay generation, PhysioVision evaluates pose-center and body-scale continuity across usable frames. A severe discontinuity, or repeated suspicious discontinuities, raises `SUBJECT_SWITCH_DETECTED`; analysis stops and the API returns bounded frame/timestamp diagnostics plus single-person recording guidance. Thresholds are configurable through `SUBJECT_*` environment values, and the guard defaults to enabled.

This guard prevents mixed-person reports but does not claim to identify every visible person. The next multi-person phase must introduce a multi-person detector or pose model, persistent track IDs, explicit athlete selection, and separate temporal/analyzer state per track. Instance segmentation may improve overlapping-person handling, but segmentation alone cannot preserve identity. Until that phase is validated, coaches, spotters, and bystanders must remain outside the recording frame and the product analyzes one person at a time.

## Exercise Delivery Sequence

### Push-up

- Implemented: side-view position gate, critical-landmark visibility, and full-body geometry rejection.
- Implemented: elbow flexion/extension phase state machine with temporal hysteresis and gap resets.
- Implemented: shoulder-hip-ankle alignment observations and left/right visibility selection.
- Remaining: reviewed real-video rep-count, invalid-input, supported-variation, and physical-device fixtures.

### Shoulder press

- Implemented: separate taxonomy, endpoint, and analyzer from shoulder abduction.
- Implemented: view, starting-position, overhead-visibility, and elbow extension/return gates.
- Implemented: trunk-compensation observations with educational wording only.
- Remaining: reviewed unloaded and clinician-approved-load video fixtures across camera views.

### Bicep curl and hammer curl

- Implemented: one generic bicep-curl elbow-flexion analyzer while keeping recognition labels separate.
- Implemented: extended-flexed-extended hysteresis, upright geometry, visibility, partial-rep, and upper-arm/trunk observation rules.
- Current evidence is synthetic only; no real-video threshold or rep-count claim is made.
- The real-time lab now combines local pose and hand landmarks to estimate neutral versus palm-facing hand orientation for curl development sessions. The upload analyzer remains disabled for Hammer Curl pending reviewed real-video validation.
- Grip type, safe load, injury risk, and resistance are never inferred.

## Real-Time Delivery Sequence

1. Implemented: local pose and hand extraction; camera frames remain on device.
2. Implemented: authenticated WebSocket sessions with TTL, message limits, cleanup, and bounded landmark sampling.
3. Implemented: derived normalized landmarks rather than image frames or base64 REST polling.
4. Implemented: `session_started`, `frame_feedback`, `rep_event`, `session_summary`, `warning`, and `error` messages.
5. Implemented: approved session metadata and derived metrics only; frames and landmark sequences are not retained.
6. Add the same contract to mobile after web physical-device QA.

## Promotion Gates

- Provenance and license record for every dataset and model artifact.
- Frozen participant-grouped train, validation, and holdout partitions.
- At least five holdout participants and at least 10 reviewed real videos per major class; broader diversity is preferred.
- Macro F1 at least 0.75 and recall at least 0.70 for each declared class.
- Confidence calibration and documented abstention behavior.
- Real-video analyzer fixtures covering valid, invalid, partial, occluded, and wrong-exercise inputs.
- Physiotherapy review of thresholds, feedback, camera instructions, and prohibited claims.
- Privacy, security, performance, web, mobile, and physical-device review.

Passing these gates permits optional engineering evaluation only. It does not establish clinical validity.

## Commands

```powershell
python scripts/prepare_exercise_pose_recognition_features.py <external-pose-table.csv> --dry-run
python scripts/prepare_exercise_pose_recognition_features.py <external-pose-table.csv>
python scripts/train_exercise_pose_xgboost.py --dry-run
python scripts/train_exercise_pose_gru.py --dry-run

# Training requires the isolated optional ML dependency set.
python -m pip install -r requirements-ml.txt
python scripts/train_exercise_pose_xgboost.py
python scripts/train_exercise_pose_gru.py
```

## Remaining Milestones

1. Complete provenance and participant metadata.
2. Add participant-grouped data and repeat calibrated training and evaluation without changing the frozen holdout during tuning.
3. Complete real-video review for push-up, shoulder press, and bicep curl when recordings become available; keep Hammer Curl disabled pending hand orientation.
4. Add authenticated streaming and per-rep event contracts.
5. Extend session persistence and progress views.
6. Complete web and mobile controlled-pilot gates.
