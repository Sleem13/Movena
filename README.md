# PhysioVision AI

PhysioVision AI is an AI-assisted physical therapy exercise analysis prototype. Sprint 1 implements a focused Squat Analyzer MVP that accepts a bodyweight squat video, extracts pose landmarks with MediaPipe, estimates basic joint angles, counts repetitions, flags common movement issues, and returns patient-friendly feedback.

## Sprint 1 Scope

This sprint intentionally builds only the first working squat analysis prototype. It does not include authentication, a database, clinician dashboards, multi-exercise support, model training, or production deployment.

The MVP includes:

- FastAPI backend with `/health` and `/api/v1/analyze/squat`.
- OpenCV and MediaPipe video pose processing.
- Rule-based squat repetition counting.
- Knee, hip, and trunk angle estimates.
- Basic detection for poor depth, excessive trunk lean, possible knee valgus, inconsistent movement, and low landmark confidence.
- React frontend for uploading a video and viewing the returned report.

## Project Structure

```text
backend/
  app/
    api/routes/
    core/
    schemas/
    services/
    tests/
    utils/
  requirements.txt
data/
  raw/
  processed/
  samples/
docs/
frontend/
  src/
    components/
    pages/
    services/
scripts/
```

## Backend Setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

If the backend is running somewhere else, set `VITE_API_BASE_URL` before starting Vite.

## Testing

```powershell
cd backend
pytest
```

The tests cover the pure angle calculation functions and core squat analysis rules with synthetic landmarks.

## Dataset Strategy

PhysioVision AI should not rely on a single dataset. The MVP starts with squat-focused data, but rehabilitation AI needs broader validation across camera viewpoints, exercise types, subject variability, repetition styles, and clinical-quality labels.

Recommended phases:

- MVP: use the Kaggle Squat Exercise Pose Dataset first for squat form labels and rule validation.
- Rehabilitation validation: use REHAB24-6 and UI-PRMD for repetition segmentation, skeleton sequence analysis, and correctness benchmarking.
- Expansion: use UCO Physical Rehabilitation and DynTherapy for multi-view robustness and additional physical therapy exercises.
- Clinical research: use KIMORE for clinical-style quality scoring research after the feature pipeline is stable.

Public datasets are used for research support, benchmarking, and early validation. They are not enough to prove real-world performance because PhysioVision AI has its own camera workflow, upload conditions, patient instructions, label taxonomy, and target users. Custom consented data is required before making strong claims about product reliability.

See:

- `docs/dataset_strategy.md`
- `docs/dataset_selection_table.md`
- `docs/custom_dataset_collection_protocol.md`
- `docs/uci_dataset_notes.md`
- `data/README.md`

## Dataset Sources

PhysioVision AI uses separate dataset tracks:

- Custom squat videos for the current camera-based MVP and real-world product validation.
- Squat pose datasets for squat scoring rule validation and future squat form classifiers.
- UCI Physical Therapy Exercises for wearable-sensor time-series research.
- Future rehabilitation video/skeleton datasets such as REHAB24-6, UCO Physical Rehabilitation, DynTherapy, UI-PRMD, and KIMORE for broader validation.

The UCI Physical Therapy Exercises Dataset is not used by the Sprint 1 squat video endpoint. It has no video frames or MediaPipe landmarks, so it belongs to a separate sensor pipeline. A future multimodal pipeline may combine camera-derived features and wearable-sensor features after each path is validated independently.

## Dataset Folder Setup

Datasets must be downloaded manually. Do not commit raw datasets, participant videos, generated processed files, Kaggle credentials, or license-restricted assets.

Expected local structure:

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
│   ├── uci_physical_therapy_exercises/
│   ├── rehab24_6/
│   ├── dyntherapy/
│   ├── ui_prmd/
│   └── kimore/
├── processed/
│   ├── pose_landmarks/
│   ├── angle_features/
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

## Dataset Pipeline

Validate and create the expected dataset folders:

```powershell
python scripts/check_dataset_structure.py --create
```

### Camera Pipeline

Prepare the local Kaggle squat dataset:

```powershell
python scripts/prepare_squat_dataset.py
```

Optional explicit input:

```powershell
python scripts/prepare_squat_dataset.py --input data/raw/squat_kaggle/squat_dataset.csv
```

Extract MediaPipe landmarks from local sample videos:

```powershell
python scripts/extract_landmarks_from_videos.py
```

This reads from `data/samples/` and `data/raw/custom_videos/` and writes to `data/processed/pose_landmarks/`.

Create angle features from extracted landmarks:

```powershell
python scripts/create_angle_features.py
```

This reads from `data/processed/pose_landmarks/` and writes to `data/processed/angle_features/`.

### Sensor Pipeline

Prepare the manually downloaded UCI Physical Therapy Exercises Dataset:

```powershell
python scripts/prepare_uci_physical_therapy_dataset.py
```

This reads `.txt`, `.csv`, and `.data` files from:

```text
data/raw/uci_physical_therapy_exercises/
```

It writes:

```text
data/processed/sensor_features/uci_physical_therapy_exercises_processed.csv
```

Extract sliding-window sensor features:

```powershell
python scripts/extract_sensor_features.py
```

It writes:

```text
data/processed/sensor_features/uci_sensor_window_features.csv
```

The sensor pipeline stays independent from the MediaPipe landmark pipeline.

### Future Multimodal Pipeline

Future sprints may align camera features and wearable-sensor features by exercise, subject, session, timestamp, or repetition. That fusion step is intentionally not implemented in Sprint 1.5.

The processed dataframe is normalized around:

- `source_dataset`
- `subject_id`
- `session_id`
- `exercise_name`
- `video_path`
- `frame_index`
- `timestamp`
- `landmark_name`
- `x`, `y`, `z`, `visibility`
- `left_knee_angle`, `right_knee_angle`
- `left_hip_angle`, `right_hip_angle`
- `trunk_angle`
- `rep_id`, `phase`
- `correctness_label`
- `detected_issue`
- `quality_score`

TODO: Add dataset-specific adapters after each public dataset is manually downloaded and its exact local schema is confirmed.

## API Endpoints

### `GET /health`

Returns:

```json
{
  "status": "ok",
  "project": "PhysioVision AI",
  "version": "0.1.0"
}
```

### `POST /api/v1/analyze/squat`

Accepts a multipart form upload with a `video` file.

Returns:

```json
{
  "exercise": "bodyweight_squat",
  "status": "success",
  "total_reps": 0,
  "average_knee_angle": 0,
  "average_hip_angle": 0,
  "average_trunk_angle": 0,
  "movement_score": 0,
  "detected_issues": [],
  "feedback": [],
  "summary": "",
  "limitations": []
}
```

## Known Limitations

- This is a CPU-friendly rule-based prototype, not a trained diagnostic model.
- 2D MediaPipe landmarks are sensitive to camera angle, lighting, occlusion, clothing, and whether the full body is visible.
- Knee valgus and trunk lean estimates are approximate because they are inferred from 2D video.
- The app stores uploaded files only temporarily during processing and does not persist analysis history.
- No database, user accounts, clinician workflows, or multi-exercise analysis are included in Sprint 1.
- Public datasets support research and benchmarking only; custom consented PhysioVision data is needed for real-world validation.

## Medical Disclaimer

This analysis is for exercise monitoring and educational support only. It does not replace assessment by a licensed physiotherapist. Users should stop exercising and consult a qualified professional if they experience pain, dizziness, instability, or symptoms that feel unsafe.

## Recommended Sprint 2

- Add side-view and front-view capture guidance.
- Save analysis reports and metadata in a lightweight database.
- Add annotated video export with pose overlays.
- Improve squat phase detection with smoothing and temporal thresholds.
- Add clinician review notes and a patient progress timeline.
- Add more validation videos and integration tests for real upload processing.
- Add dataset-specific adapters for REHAB24-6, UCO Physical Rehabilitation, DynTherapy, UI-PRMD, and KIMORE.
- Start a consented custom squat dataset using `docs/custom_dataset_collection_protocol.md`.
