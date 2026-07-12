# Sprint 7 Dataset Expansion Plan

## Current Coverage

The current metadata contains 24 supported real videos: 23 officially labeled and one quarantined unlabeled video. No augmented video features are available, so the candidate experiment uses real videos only.

| Label | Real | Augmented | Total | Target | Additional real videos recommended |
|---|---:|---:|---:|---:|---:|
| `squat_correct` | 13 | 0 | 13 | 15 | 2 |
| `squat_knee_valgus` | 4 | 0 | 4 | 10 | 6 |
| `squat_shallow_depth` | 2 | 0 | 2 | 10 | 8 |
| `squat_trunk_lean` | 4 | 0 | 4 | 10 | 6 |
| `squat_fast_uncontrolled` | 0 | 0 | 0 | 10 | 10 |
| `unlabeled` | 1 | 0 | 1 | excluded | expert review required |

At least 32 additional independently reviewed real videos are needed to reach these minimum targets. Shallow-depth and fast/uncontrolled are the largest gaps. The fast/uncontrolled label is entirely missing. Knee-valgus and trunk-lean remain small and sensitive to camera view. Correct-form recordings still dominate.

## Split and Collection Policy

The curated split covers the original collection. Seven newly available official videos are marked `development_unassigned`; they are not silently added to the protected holdout. Before a future reliability claim, assign participant-grouped validation and holdout splits without placing variants or repeated sessions from one source across partitions.

Record front and side views only under safe instructions, with full-body visibility, varied devices/lighting/body proportions, and independent physiotherapist label review. Do not ask participants to perform painful or unsafe technique to manufacture issue classes.
