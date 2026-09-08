# Movena Data Directory

This directory defines the expected local dataset layout for Sprint 1.5 dataset pipeline validation.

Do not commit raw datasets, participant videos, credentials, or generated processed files. Public datasets should be downloaded manually according to their license and placed into the matching local folder.

## Expected Structure

```text
data/
├── raw/
│   ├── custom_videos/
│   │   ├── squat_correct/
│   │   ├── squat_shallow_depth/
│   │   ├── squat_knee_valgus/
│   │   ├── squat_trunk_lean/
│   │   └── squat_fast_uncontrolled/
│   ├── squat_kaggle/
│   ├── zenodo_squat_dataset/
│   ├── uci_physical_therapy_exercises/
│   ├── rehab24_6/
│   ├── uco_physical_rehab/
│   ├── dyntherapy/
│   ├── ui_prmd/
│   └── kimore/
├── processed/
│   ├── pose_landmarks/
│   │   └── zenodo_squat_dataset/
│   ├── angle_features/
│   │   └── zenodo_squat_dataset/
│   ├── sensor_features/
│   ├── merged_features/
│   └── labels/
└── samples/
    ├── squat_correct/
    ├── squat_shallow_depth/
    ├── squat_knee_valgus/
    ├── squat_trunk_lean/
    └── squat_fast_uncontrolled/
```

## Raw Data

`data/raw/` contains manually downloaded public datasets and consented project-specific raw recordings. Raw data is not committed to GitHub because it may be large, license-restricted, or participant-identifiable.

- `data/raw/custom_videos/`
- `data/raw/squat_kaggle/`
- `data/raw/zenodo_squat_dataset/`
- `data/raw/uci_physical_therapy_exercises/`
- `data/raw/rehab24_6/`
- `data/raw/uco_physical_rehab/`
- `data/raw/dyntherapy/`
- `data/raw/ui_prmd/`
- `data/raw/kimore/`

TODO: Manually download datasets from their official or licensed sources. Do not automate downloads unless credentials and license approval are configured outside the repo.

`data/raw/uci_physical_therapy_exercises/` should contain the downloaded UCI Physical Therapy Exercises Dataset files. This dataset is wearable-sensor time-series data, not video data. Keep it separate from camera samples and do not commit downloaded dataset files to GitHub.

## Zenodo Squat Dataset

- URL: https://zenodo.org/records/17558630
- DOI: `10.5281/zenodo.17558630`
- Dataset type: side-view squat images in a 1:1 aspect ratio.
- Classes: `Good`, `Bad Back`, and `Bad Heel`.
- Best use: squat posture classification, bad-back/bad-heel rule validation, and image-level angle analysis.
- Limitation: image-only data has no temporal sequence and cannot support movement phases or repetition counting.
- Local path: `data/raw/zenodo_squat_dataset/`

Download `Dataset.zip` manually from Zenodo, extract it locally, and preserve the three class folders. Raw images remain ignored by Git.

## Processed Data

`data/processed/` contains reproducible outputs created by local scripts. These files are ignored by Git unless they are small placeholders.

- `data/processed/pose_landmarks/`: MediaPipe pose landmarks, one row per frame and landmark.
- `data/processed/angle_features/`: frame-level joint angle features.
- `data/processed/pose_landmarks/zenodo_squat_dataset/`: image-level MediaPipe landmark rows.
- `data/processed/angle_features/zenodo_squat_dataset/`: image-level posture and ankle/heel proxy features.
- `data/processed/labels/zenodo_squat_dataset_labels.csv`: normalized image metadata and labels.
- `data/processed/sensor_features/`: processed wearable-sensor signals and sliding-window sensor features.
- `data/processed/merged_features/`: reserved for future multimodal fusion.
- `data/processed/labels/`: normalized labels and metadata.

## Samples

`data/samples/` contains small local development videos for camera pipeline testing. Real videos should still stay local and uncommitted.

- `data/samples/squat_correct/`
- `data/samples/squat_shallow_depth/`
- `data/samples/squat_knee_valgus/`
- `data/samples/squat_trunk_lean/`
- `data/samples/squat_fast_uncontrolled/`

These folders are intended for local development and should not be committed with real videos.

## Dataset Types

### Camera / Video Datasets

Used for:

- MediaPipe landmark extraction.
- Joint angle calculation.
- Rep counting.
- Movement quality scoring.

Examples:

- `custom_videos`
- `squat_kaggle` if video/pose-based
- `REHAB24-6`
- `DynTherapy`

### Sensor / Time-Series Datasets

Used for:

- Wearable-sensor exercise classification.
- Fast vs low-amplitude execution detection.
- Future multimodal research.

Example:

- UCI Physical Therapy Exercises Dataset.

## Camera Processed Schema

The final camera/pose processed dataframe should support:

- `source_dataset`
- `subject_id`
- `session_id`
- `exercise_name`
- `video_path`
- `frame_index`
- `timestamp`
- `landmark_name`
- `x`
- `y`
- `z`
- `visibility`
- `left_knee_angle`
- `right_knee_angle`
- `left_hip_angle`
- `right_hip_angle`
- `trunk_angle`
- `rep_id`
- `phase`
- `correctness_label`
- `detected_issue`
- `quality_score`

Additional derived feature columns may be added for experiments, but these core columns should remain stable.

## Sensor Processed Schema

The UCI wearable-sensor pipeline should remain separate from the camera landmark pipeline.

Processed sensor rows should support:

- `source_dataset`
- `subject_id`
- `exercise_id`
- `execution_type`
- `split`
- `source_file`
- `sample_index`
- sensor signal columns

Windowed sensor feature rows should support:

- `source_dataset`
- `subject_id`
- `exercise_id`
- `execution_type`
- `split`
- `source_file`
- `window_index`
- `window_start`
- `window_end`
- feature columns such as `_mean`, `_std`, `_min`, `_max`, `_median`, `_energy`, `_range`, and `_rms`
