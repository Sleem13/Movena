# Zenodo Squat Dataset Notes

## Dataset Overview

The [Zenodo Squat Dataset](https://zenodo.org/records/17558630), DOI `10.5281/zenodo.17558630`, is an open image dataset for automated squat posture classification. Zenodo lists version v1, published on November 8, 2025, with a `Dataset.zip` archive of approximately 824.1 MB under the Creative Commons Attribution 4.0 license.

The dataset contains 1:1 side-view squat images organized into three classes:

- `Good`: correct squat posture.
- `Bad Back`: spinal or back-alignment issue in the source taxonomy.
- `Bad Heel`: improper heel/foot positioning in the source taxonomy.

The local raw path is `data/raw/zenodo_squat_dataset/`. Downloading is manual; repository scripts never download it.

## Why It Is Useful for PhysioVision AI

The dataset is closely aligned with the current squat exercise and provides labeled still images for testing whether pose-derived posture features separate the three source categories. It can support:

- Good squat image classification.
- Bad-back posture detection research.
- Bad-heel/foot-position proxy research.
- Rule-based knee, hip, trunk, and ankle angle validation.
- A future supervised image classifier after labels, splits, leakage, and subject diversity are audited.

Its labels should be treated as source annotations, not clinical diagnoses. PhysioVision feedback must retain conservative wording such as “possible back-position issue” or “possible heel-position issue.”

## How It Differs From Video Datasets

Each record is an independent image. There is no ordered frame sequence, timestamp, repetition phase, tempo, or full movement cycle. Therefore, this dataset can validate posture at captured moments but cannot validate repetition counting, descent/ascent phase detection, temporal smoothing, movement speed, or consistency across a repetition.

Custom PhysioVision squat videos remain necessary for end-to-end upload testing, rep counting, movement-phase analysis, and real camera-condition validation.

## Recommended Preprocessing

1. Download `Dataset.zip` manually and verify the Zenodo record, DOI, license, and checksum.
2. Extract the source class folders under `data/raw/zenodo_squat_dataset/`.
3. Run `prepare_zenodo_squat_dataset.py` to create normalized metadata without copying images.
4. Audit class counts, duplicates, corrupted files, subject leakage, and folder-to-label mappings.
5. Run MediaPipe Pose in static-image mode and retain landmark visibility.
6. Calculate bilateral knee/hip/ankle angles, trunk lean, and transparent heel-to-foot vertical proxies.
7. Treat heel proxies as experimental 2D features, not direct measurements of foot pressure or clinical heel loading.
8. Create subject-aware splits only after identity and collection metadata are understood; do not train a model during Sprint 2 setup.

Expected outputs:

- `data/processed/labels/zenodo_squat_dataset_labels.csv`
- `data/processed/pose_landmarks/zenodo_squat_dataset/zenodo_squat_landmarks.csv`
- `data/processed/angle_features/zenodo_squat_dataset/zenodo_squat_angle_features.csv`

## Limitations

- Image-only; no temporal or repetition information.
- Side-view-only evidence may not generalize to front-view knee alignment.
- The 1:1 source format and collection conditions may differ from uploaded phone videos.
- Fitness/posture labels are not equivalent to physiotherapist assessment.
- `Bad Back` and `Bad Heel` are broad source labels and may include heterogeneous movement patterns.
- 2D landmarks are sensitive to occlusion, framing, clothing, and camera perspective.
- A static heel/foot proxy cannot measure force, pressure, pain, or joint loading.

## Medical and Safety Disclaimer

This dataset and its derived PhysioVision features are for research, engineering validation, exercise monitoring, and educational support only. They do not diagnose injury, determine treatment, or replace assessment by a licensed physiotherapist. Any user experiencing pain, dizziness, instability, or unsafe symptoms should stop exercising and consult a qualified healthcare professional.
