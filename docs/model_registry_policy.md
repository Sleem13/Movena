# Model Registry Policy

Every model is registered as `experimental`, `candidate`, `app_optional`, or `deprecated`. Training never promotes automatically. Promotion requires complete manual annotations, participant-grouped holdout, acceptable macro F1 and per-class recall for the declared scope, error analysis, model card, safety review, versioned artifacts, rollback, and explicit approval.

Rule-based analyzers remain primary. An approved model may only provide optional/research support within its evaluated exercise, modality, population, and capture protocol. Registry metrics are engineering evidence, not clinical claims.
