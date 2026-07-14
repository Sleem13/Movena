# Squat Training Dataset v3 Candidate Policy

The v3 output is a candidate inventory, not a trained model dataset or promotion decision.

## Inclusion Gates

- Registry status permits current squat-video use.
- Sample is a recognized video file.
- Exercise and issue labels have an explicit non-unknown mapping.
- Source is not missing or incomplete.
- Source, participant, view, and augmentation lineage are preserved when available.

## Default Exclusions

Sensor-only, skeleton-only, mixed, image-only, missing, unknown-modality, unknown-label, and unlabeled samples are excluded. Augmented rows remain marked and never count as independent participants.

The current candidate contains 23 real custom videos and no augmented videos. All nine other registry entries are excluded. No v3 model is trained automatically, the v2 model remains experimental, and the rule-based analyzer remains primary.

