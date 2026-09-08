# Very Important: ML Second Opinion Extension

Movena now treats the ML second opinion as an app-wide optional layer, not a squat-only feature. Rule-based biomechanical analysis remains primary for every workout and assessment.

## Supported Model Modes

- `classical_pose_baseline`: current pose-feature baseline, preserved for bodyweight squat.
- `pretrained_as_is`: a pretrained deep-learning model used without task-specific weight updates.
- `fine_tuned`: a pretrained deep-learning model adapted on approved exercise/assessment labels.
- `feature_extractor`: a pretrained deep-learning model used to create embeddings/features for a downstream classifier.

## Current Implementation

- Every supported analysis endpoint accepts `include_ml=true`.
- Every ML response advertises `supported_model_modes`, `supported_exercises`, `model_mode`, `provider_status`, `feature_source`, and `exercise_id`.
- Squat keeps the existing experimental baseline artifact path.
- Other workouts and assessments return `provider_status="not_configured"` until a model catalog/provider is configured.
- Rejected analyses skip ML inference and keep the rule-based rejection reason.

## Provider Contract

Set `ML_SECOND_OPINION_CATALOG` to a JSON file with one entry per exercise. A configured entry can point to a local `module:function` callable:

```json
{
  "shoulder_flexion": {
    "enabled": true,
    "model_mode": "fine_tuned",
    "feature_source": "video_frames",
    "callable": "app.ml_providers.shoulder_flexion:infer"
  }
}
```

Set `enabled` to `false` to keep an inventoried provider explicitly disabled.
Catalogs created before this gate remain compatible when the field is omitted.

The callable receives `exercise_id`, `frames`, `detected_issues`, and `model_config`, then returns an `MLPrediction` or a dict matching that schema.

## Safety Rules

- ML output must not replace rule-based scoring, rep counts, validation, or clinical safety warnings.
- ML disagreement may add confidence context, but the rule-based biomechanical feedback remains the displayed primary guidance.
- A provider must expose model lineage, mode, confidence semantics, and validation notes before being enabled in production.
