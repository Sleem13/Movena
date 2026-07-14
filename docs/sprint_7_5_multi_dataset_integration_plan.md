# Sprint 7.5 Multi-Dataset Integration Plan

## Objective

Create an auditable registry and adapter boundary for heterogeneous rehabilitation datasets without changing the current squat analyzer or training a v3 model.

## Measured Inventory

| Dataset | Files | Modality | Current decision |
|---|---:|---|---|
| `custom_videos` | 24 | video | Compatible candidate |
| `dyntherapy` | 1 | skeleton/tabular | Adapter required |
| `kimore` | 1 | serialized skeleton/data | Adapter required |
| `Physical-therapy exercises` | 0 | missing | Missing/incomplete; on disk folder is misspelled |
| `rehab24_6` | 914 | mixed video/NumPy | Adapter required |
| `squat_kaggle` | 2 | precomputed CSV/metadata | Label and provenance adapter required |
| `uci_physical_therapy_exercises` | 441 | sensor time series | Adapter required |
| `uco_physical_rehab` | 0 | missing | Missing/incomplete |
| `ui_prmd` | 4 | skeleton/tabular | Adapter required |
| `zenodo_squat_dataset` | 3,806 | image | Separate image workflow; excluded from temporal video training |

## Delivery Sequence

1. Audit every raw folder without loading large samples into memory.
2. Build a conservative compatibility registry.
3. Create a starter folder-label mapping, retaining uncertainty as `unknown`.
4. Route sources through explicit dataset adapters and a fail-closed modality guard.
5. Export a v3 candidate list from compatible video sources only.
6. Export registry status for a future admin dashboard.
7. Review dataset documentation and implement source-specific adapters in later sprints.

No sensor, skeleton, image-only, mixed, missing, or unknown-label source is merged into the squat video training candidates by default. The rule-based analyzer remains primary and ML remains experimental.

