# UCI Physical Therapy Exercises Dataset Notes

## Dataset Overview

The UCI Physical Therapy Exercises Dataset is a wearable-sensor time-series dataset for physical therapy exercise analysis. The UCI Machine Learning Repository describes it as inertial and magnetic sensor data collected during physical therapy exercises using five XSens MTx sensor units. Each unit includes tri-axial accelerometer, gyroscope, and magnetometer signals sampled at 25 Hz.

The dataset includes multiple physical therapy exercise types and execution styles such as correct, fast, and low-amplitude movement.

Source:
- UCI Machine Learning Repository: `https://archive.ics.uci.edu/dataset/730/physical+therapy+exercises+dataset`

Local path:
- `data/raw/uci_physical_therapy_exercises/`

## Why It Matters

This dataset gives Movena a non-camera rehabilitation benchmark. Camera pose estimation is useful for body position and joint-angle analysis, but wearable sensors can capture movement rhythm, acceleration, angular velocity, amplitude, and smoothness. Those signals are valuable for exercise classification, execution quality modeling, and future home-rehab monitoring.

It is especially useful for future multimodal AI because it lets us design a sensor-data pipeline now without disturbing the current squat video MVP.

## How It Differs From Video Datasets

Video and pose datasets provide:

- RGB frames.
- Pose landmarks or skeleton coordinates.
- Camera viewpoint concerns.
- Visual form issues such as trunk lean or knee alignment.

The UCI dataset provides:

- Time-series sensor signals.
- Accelerometer, gyroscope, and magnetometer channels.
- Wearable sensor placement dependencies.
- Exercise execution patterns over time.

It does not provide video frames or MediaPipe landmarks, so it should not be used to validate the current `/api/v1/analyze/squat` endpoint.

## Possible ML Tasks

- Exercise classification.
- Execution quality classification.
- Correct vs fast vs low-amplitude detection.
- Time-series segmentation.
- Clustering of rehabilitation movement patterns.
- Baseline comparison with dynamic time warping or classical time-series models.
- Future multimodal fusion with camera-derived pose landmarks and joint angles.

## Limitations

- No video frames.
- No direct MediaPipe landmarks.
- Sensor placement affects signal interpretation.
- Old dataset, but still useful for baseline research.
- Execution-style labels should be verified against the dataset `Description.pdf` before clinical or product claims.
- Wearable-sensor models should remain separate from the Sprint 1 camera-based MVP until a deliberate multimodal fusion pipeline is designed.

## Pipeline Separation

Use:

- `scripts/prepare_uci_physical_therapy_dataset.py` for raw UCI sensor files.
- `scripts/extract_sensor_features.py` for sliding-window time-series features.
- `backend/app/services/sensor_dataset_loader_service.py` for future ML loading.

Do not merge these files into the MediaPipe landmark schema yet.
