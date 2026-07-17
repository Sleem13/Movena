# Dataset-Specific Adapter Notes

| Dataset | Local evidence | Adapter behavior | Current blocker |
|---|---|---|---|
| `custom_videos` | MP4 files in reviewed squat issue folders | Video metadata; reviewed folders can be discovery-level ready | Participant/session coverage and evaluation governance still required |
| `squat_kaggle` | One augmented feature CSV; no local videos/images | Tabular feature artifact; squat identity retained | Row schema, original provenance, augmentation, and label mapping review |
| `zenodo_squat_dataset` | JPG files under Good/Bad Back/Bad Heel-style folders | Image modality; squat identity retained; raw issue folder preserved | Human approval of issue mapping; images cannot support reps |
| `kimore` | Pickle container | Skeleton research container; pickle is not deserialized during audit | Safe parser, schema, codebook, participant, and exercise mapping |
| `ui_prmd` | Input/label CSV and serialized scaler files | Skeleton metadata; label file separated from samples | Codebook and row/sequence boundaries |
| `uci_physical_therapy_exercises` | `s*/e*/u*/test.txt` time series | Sensor routing; participant and raw exercise/session codes retained | Exercise codebook, units, sampling, and protocol mapping |
| `dyntherapy` | Pose/feature CSV container | Skeleton/tabular discovery | Row schema and exercise-label semantics |
| `rehab24_6` | MP4 plus 2D/3D joint/marker NPY files | Per-file video/skeleton modality; Ex and participant codes retained | Exercise codebook, synchronization, coordinate systems, and segmentation review |
| `Physical-therapy exercises` | Empty local folder | Zero samples, missing-safe result | Dataset acquisition and license/provenance review |
| `uco_physical_rehab` | Placeholder only | Explicit `missing_or_incomplete`; zero samples | Dataset acquisition and integrity verification |

Container formats are never unpickled or interpreted during metadata audit. Coded labels remain `unknown` until a reviewer approves a mapping.

