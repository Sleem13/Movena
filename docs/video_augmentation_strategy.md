# Video Augmentation Strategy

## Purpose

Augmentation creates controlled robustness variants for engineering experiments. It does not increase participant count, provide independent validation, repair label imbalance, or prove clinical generalization.

## Allowed Transformations

- Mild brightness and contrast changes.
- Horizontal flip with explicit left/right interpretation warning.
- Rotation limited to approximately ±5 degrees.
- Slight zoom-out with reflected borders so the full frame is preserved.
- Mild Gaussian noise and compression variation.
- Modest playback-rate metadata variation only within an existing fast/uncontrolled label.

## Prohibited Transformations

No large rotation, heavy crop, stretching, body distortion, fake valgus by joint warping, conversion of correct movement into an issue class, or undocumented label change.

## Governance

Outputs live in `data/augmented/custom_videos`, retain source lineage and parameters in the augmentation CSV, and must remain grouped with their source during any future split to prevent leakage. `safe_for_training=true` means only that automated structural checks passed; visual QA and physiotherapist review are still required.
