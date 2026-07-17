# Model Registry Policy

Every model is registered as `experimental`, `candidate`, `app_optional`, or `deprecated`. Training never promotes automatically. Promotion requires complete manual annotations, participant-grouped holdout, acceptable macro F1 and per-class recall for the declared scope, error analysis, model card, safety review, versioned artifacts, rollback, and explicit approval.

Rule-based analyzers remain primary. An approved model may only provide optional/research support within its evaluated exercise, modality, population, and capture protocol. Registry metrics are engineering evidence, not clinical claims.

## Exercise-recognition models

Recognition models enter the registry as `experimental` and `promoted_to_app=false`. They cannot route automatically without a completed recognition model card, participant-grouped evaluation, approved macro F1 and per-class recall, confidence calibration, and evidence that systematic routing errors do not trigger unsafe or unsupported analysis. A suggestion always requires confirmation. A predicted exercise without a supported analyzer cannot produce feedback, and recognition artifacts are never promoted automatically.
