# Sprint 5 Plan

## Goal

Create a small, explainable, reproducible ML baseline over custom-video angle features without replacing the rule-based Squat Analyzer or making clinical claims.

## Scope

- Aggregate frame-level custom-video angles to video-level statistics.
- Preserve the curated split and exclude unlabeled recordings.
- Train Logistic Regression, Random Forest, and probability-enabled SVC pipelines.
- Evaluate on the protected holdout, save metrics/artifacts/contracts, and expose offline prediction through a script.

## Non-goals

No deep learning, dataset-blind merging, backend inference, rule replacement, new exercises, authentication, database, diagnostic claim, or production deployment.

## Datasets

The experiment uses only `custom_squat_videos_angle_features.csv`. The Zenodo angle file was absent and its image posture labels do not align with the custom video taxonomy, so no merge was attempted.

## Evaluation Metrics

Accuracy, macro precision/recall/F1, weighted F1, classification report, and a fixed-label confusion matrix are recorded. Stratified cross-validation is skipped because development contains singleton classes. Candidate selection uses protected-holdout macro F1, but the holdout has only three videos and lacks knee valgus.

## Acceptance Criteria

- Video-level training CSV and reproducible feature contract exist.
- Three simple pipelines train and the selected artifact is saved.
- Metrics, mapping, prediction output, confusion figure, and limitations are documented.
- Dummy-data tests and the complete existing suite pass.
- Rule-based backend behavior remains unchanged.

## Risks

Tiny samples, label imbalance, subject leakage, camera dependence, MediaPipe failure, incomplete holdout coverage, repeated holdout inspection, and unsafe overinterpretation. This experiment is a pipeline baseline, not evidence of clinical accuracy.
