# Dataset Adapter Policy

Every external dataset must cross a dataset-specific adapter boundary before it can enter a feature or model pipeline. The base adapter exposes availability, audit, sample listing, metadata extraction, label normalization, and current-pipeline compatibility.

Initial adapters cover custom videos, Squat Kaggle, Zenodo squat images, and a fail-closed generic source. Only the custom-video adapter currently reports compatibility with the temporal squat pipeline.

Adapters must:

- preserve source paths, original labels, participant/session identifiers when available, and augmentation lineage;
- map uncertain labels to `unknown` rather than guessing issue meaning;
- document licenses and source splits before training use;
- avoid treating frames, augmentations, or repeated sessions as independent participants;
- remain dataset-specific when schemas or modalities differ.

Adding an adapter does not authorize a new exercise, clinical interpretation, or automatic model inclusion.

