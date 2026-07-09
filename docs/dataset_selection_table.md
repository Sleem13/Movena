# Dataset Selection Table

| Dataset name | Source | Data type | Exercises | Labels/annotations | Best use in PhysioVision AI | Limitations | Priority |
|---|---|---|---|---|---|---|---|
| Squat Exercise Pose Dataset | Kaggle, manual download into `data/raw/squat_kaggle/` | Pose landmarks and/or derived squat pose data depending on Kaggle package | Squat | Correct/incorrect or squat form labels depending on package version | First MVP validation for squat scoring, shallow depth rules, and future squat classifiers | Not clinical; exact schema varies by Kaggle upload; credentials must not be hardcoded | P0 |
| REHAB24-6 | Public rehabilitation research dataset; manual download into `data/raw/rehab24_6/` | RGB videos and skeleton sequences | Rehabilitation exercises | Correctness labels, repetition-aware annotations, exercise assessment labels | Rehabilitation validation after squat MVP; repetition segmentation and correctness benchmarking | Not squat-first; source labels may not directly match PhysioVision issue labels | P1 |
| UCO Physical Rehabilitation Dataset | UCO physical rehabilitation dataset; manual download into `data/raw/uco_physical_rehab/` | RGB multi-view rehabilitation videos and pose/skeleton data when available | Rehabilitation exercises | Exercise identity, view/session metadata, movement data | Camera viewpoint robustness and joint angle validation | Multi-view preprocessing is more complex; label details must be checked locally | P2 |
| DynTherapy | DynTherapy dataset; manual download into `data/raw/dyntherapy/` | MediaPipe-style 33-keypoint pose sequences | Glute bridge, leg raises, knee raises, shoulder movements, and related PT exercises | Exercise and movement labels depending on release | Multi-exercise expansion using a 33-keypoint format close to the MVP stack | Requires adapter work; not needed before squat MVP stabilizes | P2 |
| UI-PRMD | Public rehabilitation movement benchmark; manual download into `data/raw/ui_prmd/` | Joint position and joint angle sequences | Rehabilitation movement set | Correct/incorrect movement examples and sequence metadata | Baseline comparison for joint sequence and angle features | Older benchmark style; sensor format may differ from phone RGB uploads | P1 |
| KIMORE | Kinematic assessment of Movement and clinical scores for remote monitoring of physical Rehabilitation; manual download into `data/raw/kimore/` | RGB-D, skeleton data, clinical-style movement data | Rehabilitation exercises, including low-back-pain-oriented movements | Physician/clinical movement quality scores and exercise metadata | Future clinical-style validation and quality-score modeling | Heavier modality requirements; clinical scores need careful interpretation | P3 |
| UCI Physical Therapy Exercises Dataset | UCI Machine Learning Repository; manual download into `data/raw/uci_physical_therapy_exercises/` | Wearable inertial and magnetic sensor time-series: accelerometer, gyroscope, magnetometer | Eight physical therapy exercise types | Execution style labels such as correct, fast, and low-amplitude; train/test organization | Future wearable-sensor baseline models, execution quality classification, time-series segmentation, and multimodal rehab research | Not a video dataset; no RGB frames or MediaPipe landmarks; sensor placement dependent; keep separate from camera pipeline | Medium for MVP, High for future multimodal research |

## Notes

- Priority `P0` means use first for the squat MVP.
- Priority `P1` means use after the MVP pipeline works for broader rehabilitation validation.
- Priority `P2` means use for viewpoint robustness or multi-exercise expansion.
- Priority `P3` means reserve for clinical-style research validation after the pipeline is stable.
- The UCI dataset is not ranked in the pose-estimation priority ladder because it belongs to the separate sensor pipeline.

Public datasets support research, benchmarking, and design checks. They should not be treated as proof of real-world product performance without PhysioVision-specific custom data.
