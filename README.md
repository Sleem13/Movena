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
requirements.txt
requirements-dev.txt
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

## Python Version

- Recommended Python version: **3.12.x**.
- Validated with **Python 3.12.10** on Windows.
- Always use a project-local `.venv`; do not reuse a global environment or a virtual environment from another project.
- On Windows, run tests with `python -m pytest` after confirming `python` resolves to this repository's `.venv`.

Verify the selected interpreter:

```powershell
python -c "import sys; print(sys.version); print(sys.executable)"
```

If PowerShell execution policy blocks `Activate.ps1`, use the project interpreter directly without changing machine policy:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Backend Setup

Create the virtual environment inside the project root. A project-local `.venv` prevents Windows launchers from resolving an old environment from another folder or drive.

If `Get-Command python` or `Get-Command pytest` points to an environment outside this project, close that terminal and open a new PowerShell window in the project root before running the setup commands.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Set-Location backend
python -m uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

If the backend is running somewhere else, set `VITE_API_BASE_URL` before starting Vite:

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Run the automated UI tests and production build from `frontend/`:

```powershell
npm test
npm run build
```

The frontend includes Home, Analyze, Results, and About views; configurable artifact/ML options; original and annotated video review; responsive KPI cards; lightweight angle, issue, radar, score, and rep-quality visualizations; PDF/video/JSON exports; and persistent medical-safety messaging. Relative artifact paths are resolved against `VITE_API_BASE_URL`.

## Testing

Run tests from the project root. On Windows, use `python -m pytest` so the test runner uses the active `.venv` interpreter instead of a stale `pytest.exe` launcher containing an old absolute path.

```powershell
python -m pytest
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
│   ├── uco_physical_rehab/
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

Prepare custom squat video metadata and a label-coverage validation report:

```powershell
python scripts/prepare_custom_squat_videos.py
```

This scans `data/raw/custom_videos/` and writes:

```text
data/processed/labels/custom_squat_videos_labels.csv
data/processed/labels/custom_squat_videos_validation_report.md
```

Extract one combined MediaPipe landmark CSV from the prepared custom videos:

```powershell
python scripts/extract_landmarks_from_videos.py
```

This uses the metadata CSV when available and writes:

```text
data/processed/pose_landmarks/custom_squat_videos_landmarks.csv
```

Unreadable or no-pose videos are recorded in `data/processed/pose_landmarks/failed_videos.csv` without stopping other videos.

Create frame-level angle features from the combined landmarks:

```powershell
python scripts/create_angle_features.py
```

It writes:

```text
data/processed/angle_features/custom_squat_videos_angle_features.csv
```

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

## Zenodo Squat Dataset

The [Zenodo Squat Dataset](https://zenodo.org/records/17558630) (DOI `10.5281/zenodo.17558630`) contains side-view `Good`, `Bad Back`, and `Bad Heel` squat images. It is useful for Sprint 2 image-level posture and rule validation, but it cannot support rep counting or temporal movement analysis.

Download `Dataset.zip` manually and extract the class folders under:

```text
data/raw/zenodo_squat_dataset/
```

Run from the project root:

```powershell
python scripts/check_dataset_structure.py --create
python scripts/prepare_zenodo_squat_dataset.py
python scripts/extract_landmarks_from_images.py
python scripts/create_image_angle_features.py
```

Generated metadata, landmarks, and image-level angle features are written under `data/processed/labels/`, `data/processed/pose_landmarks/zenodo_squat_dataset/`, and `data/processed/angle_features/zenodo_squat_dataset/`. Raw images and generated CSV files remain excluded from Git. See `docs/zenodo_squat_dataset_notes.md` for preprocessing guidance and limitations.

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

## Squat Accuracy and Confidence Hardening

The squat analyzer now smooths pose-derived angle signals and counts repetitions with a completed movement state machine rather than a single threshold crossing. Responses separate movement observations from measurement reliability through `movement_score`, `score_breakdown`, `rep_count_confidence`, `pose_quality`, and `analysis_confidence`.

The optional experimental ML output can report confidence and agreement, but it never overrides the rule-based analyzer. Low-quality pose evidence and side-view knee-alignment evidence are presented cautiously. These outputs support exercise monitoring and testing; they are not clinically validated assessments.

Run the complete validation:

```powershell
python -m pytest
Set-Location frontend
npm test
```

See [the hardening plan](docs/squat_accuracy_hardening_plan.md), [rep-counting method](docs/squat_rep_counting_method.md), [confidence design](docs/analysis_confidence_design.md), and [score breakdown](docs/squat_scoring_breakdown.md).

## Medical Disclaimer

This analysis is for exercise monitoring and educational support only. It does not replace assessment by a licensed physiotherapist. Users should stop exercising and consult a qualified professional if they experience pain, dizziness, instability, or symptoms that feel unsafe.

## Sprint Status

Sprint 2 is **Conditionally Complete**. The final curated run processed 17 videos into 64,152 landmark rows and 1,944 frame-level angle rows (the pre-curation baseline was 64,119/1,943). The live FastAPI endpoint successfully analyzed `squat_correct_001.mp4`, returned one repetition and the documented JSON fields, and handled missing, unsupported, empty, and unreadable uploads with structured 4xx responses. The frontend production build passes and its upload, loading, result, error, and configurable API states are implemented.

The remaining data-coverage condition is the absence of `squat_fast_uncontrolled` examples. The `squat_unlabeled` folder is a review-only quarantine bucket and is not an official supervised label until each video is manually curated.

Exact closure commands (run from the project root in PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python scripts\check_dataset_structure.py
python scripts\prepare_custom_squat_videos.py
python scripts\extract_landmarks_from_videos.py
python scripts\create_angle_features.py
python -m pytest
Set-Location backend
python -m uvicorn app.main:app --reload
```

In a second PowerShell terminal, start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

See [the Sprint 2 completion report](docs/sprint_2_completion_report.md) for validation evidence and remaining limitations.

## Sprint 3 Focus

Sprint 3 improves the existing Squat Analyzer MVP through curated squat-video coverage, expert threshold validation, upload hardening, stable API errors, and frontend automated tests. It does **not** add model training, additional exercises, authentication, database complexity, or an architecture redesign.

Run the data and automated checks from the project root:

```powershell
python scripts/check_dataset_structure.py
python scripts/prepare_custom_squat_videos.py
python scripts/extract_landmarks_from_videos.py
python scripts/create_angle_features.py
python -m pytest
```

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

In another terminal, run and test the frontend:

```powershell
cd frontend
npm install
npm run dev
npm test
```

Sprint 3 QA artifacts:

- [Custom squat dataset audit](docs/custom_squat_dataset_audit.md)
- [Squat threshold review](docs/squat_thresholds.md)
- [API contract](docs/api_contract.md)
- [Sprint 3 plan](docs/sprint_3_plan.md)
- [Sprint 3 QA checklist](docs/sprint_3_qa_checklist.md)

## Sprint 4 Focus

Sprint 4 adds visual feedback and therapist-friendly reporting to the existing Squat Analyzer. Successful analyses can generate a temporary PDF report with `generate_report=true`. Optional query flags add a CPU-friendly skeleton overlay and bounded frame-level angles without changing the default summary workflow. The frontend requests the report and overlay for its results view and adds camera-placement guidance, download controls, annotated preview, and a dedicated educational-use notice.

No model training, new exercise, authentication, database, permanent patient record, or diagnostic claim is included.

Install the updated dependencies and run validation:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
cd frontend
npm install
npm test
npm run build
```

Start the API from `backend/`:

```powershell
python -m uvicorn app.main:app --reload
```

Sprint 4 endpoints:

- `POST /api/v1/analyze/squat` — compact summary JSON.
- `POST /api/v1/analyze/squat?generate_report=true` — adds a temporary PDF report.
- `POST /api/v1/analyze/squat?include_frame_data=true` — adds at most 300 sampled frame rows.
- `POST /api/v1/analyze/squat?include_overlay=true` — adds an experimental annotated-video artifact.
- `GET /api/v1/artifacts/reports/{report_id}` — downloads a non-expired PDF.
- `GET /api/v1/artifacts/overlays/{overlay_id}` — downloads a non-expired overlay MP4.

Reports and overlays are stored temporarily for one hour by default and cleaned opportunistically. They are not durable or access-controlled clinical records. OpenCV’s CPU-friendly MP4 output may not preview in every browser. See [the Sprint 4 plan](docs/sprint_4_plan.md), [report design](docs/report_generation_design.md), and [visual feedback design](docs/visual_feedback_design.md).

## Sprint 5 Model Baseline

Sprint 5 adds an **offline experimental ML baseline** over aggregated custom-video angle features. It does not replace or modify the rule-based Squat Analyzer, and it is not clinically validated. The Zenodo image dataset is not merged because its prepared angle file is absent and its posture taxonomy differs from the custom-video movement labels.

Run from the project root:

```powershell
python scripts/prepare_squat_training_dataset.py
python scripts/train_squat_baseline.py
python scripts/evaluate_squat_baseline.py
python scripts/predict_squat_baseline.py --video-path data/raw/custom_videos/squat_correct/squat_correct_009.mp4
```

Outputs:

- `data/processed/features/squat_video_training_features.csv`
- `models/squat_baseline/metrics.json`
- `models/squat_baseline/feature_columns.json`
- `models/squat_baseline/label_mapping.json`
- `models/squat_baseline/artifacts/squat_quality_baseline.pkl`
- `reports/figures/squat_baseline_confusion_matrix.png`

The current experiment contains only 16 labeled videos and a three-video holdout without knee-valgus coverage. Reported scores are pipeline smoke-test evidence, not reliable generalization or clinical accuracy. See [the Sprint 5 plan](docs/sprint_5_plan.md), [training design](docs/model_training_baseline.md), [evaluation report](docs/model_evaluation_report.md), and [model limitations](docs/model_limitations.md).

## Sprint 6 — Experimental ML Integration and Video Augmentation

The rule-based analyzer remains the primary product output. Add `include_ml=true` only when an explicitly experimental second opinion is useful:

```text
POST /api/v1/analyze/squat?include_ml=true
```

If the trusted Sprint 5 model or compatible features are unavailable, the request still succeeds with the rule-based report and a disabled ML status. ML never overrides rule feedback and is not clinically validated.

The augmentation notebook and helper create mild, lineage-tracked robustness variants under `data/augmented/custom_videos/`. They do not fabricate clinical labels or replace real consented collection.

```powershell
python scripts/check_dataset_structure.py --create
python scripts/prepare_custom_squat_videos.py
python scripts/extract_landmarks_from_videos.py
python scripts/create_angle_features.py
python scripts/prepare_squat_training_dataset.py
python scripts/train_squat_baseline.py
python scripts/evaluate_squat_baseline.py
python scripts/predict_squat_baseline.py
python scripts/prepare_augmented_squat_videos.py
python -m pytest
```

Launch the reviewed notebook workflow with:

```powershell
jupyter notebook notebooks/custom_squat_video_augmentation.ipynb
```

After generating variants, validate them and use the augmented input/output CLI options documented inside the notebook. See [Sprint 6 plan](docs/sprint_6_plan.md), [ML integration design](docs/ml_integration_design.md), [augmentation strategy](docs/video_augmentation_strategy.md), and [validation checklist](docs/sprint_6_validation_checklist.md).

## Sprint 7 — Dataset Expansion and Model Reliability

Sprint 7 prepares a lineage-aware v2 dataset, optionally includes validated augmented features, trains a separate candidate baseline, and compares it with Sprint 5. The candidate does not replace the current optional Sprint 5 backend model. The rule-based analyzer remains primary.

```powershell
python scripts/prepare_squat_training_dataset_v2.py --include-augmented
python scripts/train_squat_baseline_v2.py
python scripts/evaluate_squat_baseline_v2.py
python scripts/predict_squat_baseline_v2.py --video-path data/raw/custom_videos/squat_correct/squat_correct_009.mp4
python -m pytest
```

The current v2 run contains 23 real videos and zero augmented feature rows. It matches Sprint 5’s three-video holdout metrics rather than demonstrating improvement, so ML remains optional and disabled by default. See the [dataset expansion plan](docs/sprint_7_dataset_expansion_plan.md), [augmented data policy](docs/augmented_data_policy.md), [reliability report](docs/sprint_7_model_reliability_report.md), [v2 evaluation](docs/model_evaluation_report_v2.md), and [model versioning policy](docs/ml_model_versioning_policy.md).

## Pretrained Pose Backbone Benchmarking

PhysioVision AI uses pretrained pose estimation models for landmark detection, while biomechanics interpretation is handled by rule-based and experimental ML layers. Pose landmarks are measurements, not diagnoses or clinically validated decisions. MediaPipe/BlazePose remains the production default and the rule-based analyzer remains primary.

The optional offline benchmark layer compares backbone coverage, confidence, angle stability, speed, and downstream rule agreement without changing the API:

```powershell
$env:POSE_BACKEND = "mediapipe"
python scripts/benchmark_pose_backends.py
```

MoveNet Lightning and Thunder have stable interface placeholders but remain deferred because TensorFlow/model assets are not application dependencies. See [the pretrained pose strategy](docs/pretrained_pose_model_strategy.md) and [benchmark plan](docs/pose_model_benchmark_plan.md).
