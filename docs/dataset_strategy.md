# PhysioVision AI Dataset Strategy

## Why We Should Not Rely on One Dataset

PhysioVision AI needs to work across exercises, camera views, body types, lighting conditions, repetition speeds, and rehabilitation movement patterns. No single public dataset covers that full operating range.

A squat-only dataset is useful for the Sprint 1 MVP, but it will not validate rehabilitation correctness, clinical scoring, camera robustness, sensor-based monitoring, or multi-exercise generalization. Rehabilitation datasets such as REHAB24-6, UCO Physical Rehabilitation, DynTherapy, UI-PRMD, and KIMORE each contribute a different slice of evidence: RGB video, skeleton sequences, repetition segmentation, correctness labels, multi-view recordings, or clinical quality scores. The UCI Physical Therapy Exercises Dataset adds a separate wearable-sensor time-series track for future multimodal research.

The practical strategy is to use public datasets for research support, benchmarking, and early validation, while building a custom PhysioVision dataset for real-world product performance. Public datasets help us avoid designing rules in a vacuum. Custom data is still necessary because our target camera setup, upload workflow, patient instructions, body framing, and feedback labels will be specific to PhysioVision AI.

## Dataset Phases

### Phase 1: MVP Squat Rule Validation

Primary dataset:
- Squat Exercise Pose Dataset from Kaggle
- Zenodo Squat Dataset for image-level posture validation

Goals:
- Validate squat form labels against the current rule-based analyzer.
- Stress-test shallow depth, knee valgus, trunk lean, and repetition counting rules.
- Build first train/validation/test CSV splits for future supervised squat classifiers.
- Validate image-level `Good`, `Bad Back`, and `Bad Heel` labels against interpretable pose and angle features.

Why first:
- It is closest to the MVP exercise.
- It can be used immediately for squat-specific labels and simple form classification.
- It keeps Sprint 1 focused on one exercise instead of prematurely broadening the platform.
- The Zenodo image dataset is directly relevant to Sprint 2 posture validation, while custom videos remain necessary for rep counting and movement-phase analysis.

### Phase 2: Rehabilitation Validation

Primary datasets:
- REHAB24-6
- UI-PRMD

Goals:
- Compare PhysioVision features against rehabilitation movement benchmarks.
- Evaluate repetition segmentation, movement phases, and correctness labels.
- Test whether generic pose features transfer from squat to rehab movements.

### Phase 3: Viewpoint and Multi-Exercise Expansion

Primary datasets:
- UCO Physical Rehabilitation Dataset
- DynTherapy

Goals:
- Improve robustness across front-view, side-view, and multi-view videos.
- Add more rehabilitation exercises such as glute bridges, leg raises, knee raises, and shoulder movements.
- Test MediaPipe-style 33-keypoint compatibility across exercise types.

### Phase 4: Clinical Research and Quality Scoring

Primary dataset:
- KIMORE

Goals:
- Study clinical-style movement quality scoring.
- Compare rule-derived scores against physician or clinical assessment scores.
- Prepare future validation work for low-back-pain rehabilitation workflows.

### Phase 5: Wearable-Sensor and Multimodal Research

Primary dataset:
- UCI Physical Therapy Exercises Dataset

Goals:
- Build baseline time-series models for wearable rehabilitation exercise classification.
- Study execution-style classification such as correct, fast, and low-amplitude movement.
- Prepare future multimodal AI work that can combine camera landmarks with inertial sensor signals.
- Keep sensor data separate from MediaPipe landmarks until a deliberate fusion design is added.

## Dataset Strengths and Limitations

### Squat Exercise Pose Dataset from Kaggle

Strengths:
- Directly aligned with the current bodyweight squat MVP.
- Useful for correct vs incorrect squat classification.
- Good starting point for validating shallow depth and posture heuristics.

Limitations:
- Usually not collected in a clinical rehabilitation setting.
- May have limited subject diversity, camera consistency, metadata, or label granularity depending on the specific Kaggle version.
- Manual download is required; do not hardcode credentials or automate Kaggle access in the repo.

### Zenodo Squat Dataset

Source:
- https://zenodo.org/records/17558630
- DOI: `10.5281/zenodo.17558630`

Strengths:
- Side-view squat images align directly with image-level squat posture assessment.
- `Good`, `Bad Back`, and `Bad Heel` classes can support validation of bad-back and bad-heel feedback rules.
- MediaPipe landmarks and transparent angle features can be compared across the three source labels.
- High priority for Sprint 2 posture-rule validation and a possible future supervised image classifier.

Limitations:
- It is an image dataset, not a video dataset.
- It cannot validate repetition counting, movement phases, tempo, or temporal consistency.
- It should not replace custom PhysioVision squat videos, which are required for the upload workflow and temporal analysis.
- It is not clinical rehabilitation evidence and must not be used to make diagnostic claims.

### REHAB24-6

Strengths:
- Useful for rehabilitation exercise assessment and correctness labels.
- Supports repetition-aware analysis and skeleton sequence modeling.
- Research literature reports its use for exercise quality assessment and feedback generation.

Limitations:
- Not squat-specific.
- Data format may require custom adapters.
- Labels may not map one-to-one to PhysioVision feedback categories.

### UCO Physical Rehabilitation Dataset

Strengths:
- Useful for RGB multi-view rehabilitation exercise analysis.
- Helps validate camera viewpoint robustness.
- Good candidate for testing whether joint angle features remain stable across views.

Limitations:
- May not include the exact squat labels used by the MVP.
- Multi-view data increases preprocessing complexity.
- Clinical label coverage may be narrower than KIMORE.

### DynTherapy

Strengths:
- Relevant to MediaPipe-style 33-keypoint physical therapy workflows.
- Useful for multi-exercise expansion beyond squats.
- Exercise set aligns with common rehab movements such as glute bridges, leg raises, knee raises, and shoulder movements.

Limitations:
- Requires format normalization before it can be merged with other sources.
- Label definitions must be checked before training correctness models.
- Not the first priority while the MVP remains squat-focused.

### UI-PRMD

Strengths:
- Classical rehabilitation movement benchmark.
- Useful for joint position sequence analysis and baseline comparisons.
- Frequently appears in rehabilitation exercise assessment literature.

Limitations:
- Older benchmark style and sensor assumptions may not match phone-upload RGB workflows.
- Not directly labeled for PhysioVision issue categories.
- Requires mapping from source skeleton format to the unified schema.

### KIMORE

Strengths:
- Clinical-style rehabilitation dataset with RGB-D/skeleton data and movement quality scores.
- Strong candidate for future medical validation and quality scoring research.
- Especially relevant to low-back-pain rehabilitation assessment.

Limitations:
- Heavier data modalities and clinical scoring make it better for later validation than Sprint 1.
- Labels and scores need careful interpretation before being used in patient-facing feedback.
- Not a substitute for PhysioVision-specific consented custom data.

## UCI Physical Therapy Exercises Dataset

Dataset type:
- Wearable sensor time-series dataset.

Sensors:
- Accelerometer.
- Gyroscope.
- Magnetometer.

The UCI Physical Therapy Exercises Dataset contains wearable inertial and magnetic sensor data collected during physical therapy exercises. The UCI repository describes eight exercise types, three execution styles, and five XSens MTx sensor units, each containing tri-axial accelerometer, gyroscope, and magnetometer sensors sampled at 25 Hz.

Use case in PhysioVision AI:
- Future wearable-sensor analysis for rehabilitation exercise classification.
- Execution quality classification for correct, fast, and low-amplitude movement styles.
- Baseline time-series modeling for segmentation, clustering, and classification.
- Multimodal research where wearable sensors may complement camera-based pose estimation.

Why it is useful:
- It gives PhysioVision a non-video benchmark for rehabilitation movement recognition.
- It supports robust time-series feature engineering and sequence modeling.
- It can help compare movement quality signals from sensors against camera-derived angle features in future research.

Why it is not directly used for pose-estimation video analysis:
- It has no RGB frames.
- It has no MediaPipe landmarks.
- It depends on wearable sensor placement rather than camera viewpoint.
- It cannot directly validate the Sprint 1 squat upload endpoint, pose landmarks, or visual joint-angle pipeline.

How it supports future multimodal AI rehab systems:
- Camera data can estimate body position, joint angles, and visual movement issues.
- Wearable data can capture acceleration, rotation, rhythm, smoothness, and amplitude signals even when camera visibility is poor.
- A future multimodal pipeline can fuse both streams after each modality has a stable independent preprocessing path.

## Recommended First Dataset

Use the Kaggle Squat Exercise Pose Dataset and Zenodo Squat Dataset for complementary squat validation, while keeping custom videos as the primary end-to-end Sprint 2 evidence.

Reason:
- It directly supports the current MVP exercise.
- It can validate rule-based squat scoring quickly.
- It keeps engineering effort aligned with Sprint 1 acceptance criteria.
- The Zenodo dataset adds focused image-level validation for good posture, back alignment, and heel/foot positioning, but it does not cover rep counting.

After the MVP squat pipeline is stable, add REHAB24-6 and UI-PRMD for rehabilitation sequence validation. Then add UCO and DynTherapy for viewpoint and exercise expansion. KIMORE should be reserved for clinical-style scoring research once the platform has stable feature extraction and a well-documented custom data collection protocol.

The UCI Physical Therapy Exercises Dataset should be kept medium priority for the camera-only MVP and high priority for future multimodal research. It should not block the squat video analyzer.

## Camera Pipeline Process

Camera and pose-estimation datasets should be normalized into the same processed dataframe schema:

- `source_dataset`
- `subject_id`
- `session_id`
- `exercise_name`
- `video_path`
- `frame_index`
- `timestamp`
- `landmark_name`
- `x`
- `y`
- `z`
- `visibility`
- `left_knee_angle`
- `right_knee_angle`
- `left_hip_angle`
- `right_hip_angle`
- `trunk_angle`
- `rep_id`
- `phase`
- `correctness_label`
- `detected_issue`
- `quality_score`

This schema keeps the MVP simple while allowing future supervised learning, repetition segmentation, and clinical quality scoring.

## Sensor Pipeline Process

Wearable-sensor datasets should stay independent from the camera landmark schema. The UCI Physical Therapy Exercises Dataset should be processed into:

- `source_dataset`
- `subject_id`
- `exercise_id`
- `execution_type`
- `split`
- `source_file`
- `sample_index`
- sensor signal columns

Sliding-window feature extraction then creates:

- `window_index`
- `window_start`
- `window_end`
- mean, standard deviation, min, max, median, energy, range, and RMS features per sensor channel

Do not merge sensor features with MediaPipe landmarks until a future multimodal pipeline is explicitly designed.

## Manual Dataset Handling

Datasets must be downloaded manually into `data/raw/` or `data/samples/`. Do not commit raw videos, patient data, Kaggle credentials, or license-restricted dataset files.

TODO: Add dataset-specific adapters after each dataset is manually downloaded and its exact local file format is confirmed.
