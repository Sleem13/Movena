# Custom Squat Dataset Audit

## Decision

The custom collection is useful for local rule and end-to-end validation but is not balanced, independently labeled, or large enough for model training or clinical-performance claims. `squat_unlabeled` is a quarantine bucket, not an officially supported class. Its video is excluded from curated validation until a physiotherapist confirms a known label.

## Inventory

Audit source: `data/processed/labels/custom_squat_videos_labels.csv` after the Sprint 2 filename cleanup.

| Label | Videos | Coverage assessment |
|---|---:|---|
| `squat_correct` | 9 | Largest class; still too small for population claims |
| `squat_shallow_depth` | 2 | Severe minority class |
| `squat_knee_valgus` | 1 | Critical gap; no independent holdout possible |
| `squat_trunk_lean` | 4 | Minority class |
| `squat_fast_uncontrolled` | 0 | Missing class |
| `unlabeled` | 1 | Quarantined and excluded |

The correct class represents 9 of 16 officially labeled videos (56.25%). The smallest represented official class has one video, and fast/uncontrolled has none. Metrics aggregated across these clips would be dominated by correct-form recordings and must not be reported as class-balanced accuracy.

## Filename and Label Review

- The former `squat_correct_002.mp4` inside `squat_trunk_lean` was renamed to `squat_trunk_lean_004.mp4`; no remaining filename/folder conflict is present in current metadata.
- `squat_unlabeled/unlabeled.mp4` remains intentionally quarantined. It may be used to test pipeline robustness, but not label-specific rules, supervised workflows, or accuracy claims.
- Folder names are operational labels, not expert ground truth. Every issue-labeled clip still needs independent physiotherapist review with camera-view notes.

## Curated Rule-Validation Split

`data/processed/labels/custom_squat_curated_split.csv` separates threshold-tuning references, validation fixtures, and protected holdouts. It is explicitly not an ML training split. Holdouts exist only where class count permits; the single knee-valgus clip is validation-only, and the unlabeled clip is excluded.

## Minimum Additional Collection

Target a minimum of five independently reviewed videos per official label before class-level rule validation. This is a pragmatic QA floor, not a statistically powered clinical sample.

| Label | Current | Minimum additional | Priority |
|---|---:|---:|---|
| `squat_correct` | 9 | 0 | Add diversity later rather than duplicates |
| `squat_shallow_depth` | 2 | 3 | High |
| `squat_knee_valgus` | 1 | 4 | Critical |
| `squat_trunk_lean` | 4 | 1 | Medium |
| `squat_fast_uncontrolled` | 0 | 5 | Critical |

Collection should diversify consenting participants, front/side camera views, clothing, lighting, device, body proportions, and movement speed. Do not ask participants to reproduce unsafe form if doing so creates pain, instability, or risk; use clinician-supervised or safely simulated examples.
