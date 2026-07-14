# PhysioVision AI

PhysioVision AI is a physiotherapy-informed movement-analysis and rehabilitation-support product in development. Its current working vertical slice is a focused Squat Analyzer MVP that accepts a bodyweight squat video, extracts pose landmarks with MediaPipe, estimates basic joint angles, counts repetitions, flags possible movement patterns, and returns educational feedback with validity, confidence, and limitations.

## From Squat MVP to Full Product Roadmap

The Squat Analyzer is the MVP, not the final product. The long-term architecture supports a patient web/mobile experience, therapist dashboard, exercise-specific analysis engine, consent-aware session history, report generation, dataset/model governance, and a shared safety/confidence layer. Web remains first; a React Native + Expo companion is the recommended initial mobile route, with analysis staying on the FastAPI backend before any on-device feasibility work.

No additional exercise is active today. Sit-to-stand is the recommended next rule-based pilot after dedicated recording guidance, data collection, expert threshold review, and safety tests. The current rule-based squat analyzer remains primary, and optional ML remains experimental.

Product planning documents:

- [Product vision](docs/product_vision.md)
- [Full product roadmap](docs/full_product_roadmap.md)
- [Backend exercise engine architecture](docs/backend_exercise_engine_architecture.md)
- [Product API design](docs/product_api_design.md)
- [Database schema plan](docs/database_schema_plan.md)
- [Mobile strategy](docs/mobile_strategy.md) and [deployment roadmap](docs/mobile_app_deployment_roadmap.md)
- [Therapist dashboard roadmap](docs/therapist_dashboard_roadmap.md)
- [Frontend refinement plan](docs/frontend_product_refinement_plan.md)
- [Product safety policy](docs/product_safety_policy.md) and [clinical positioning](docs/clinical_positioning_and_limitations.md)
- [Next exercise selection](docs/next_exercise_selection.md)

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

A squat validity gate runs before scoring and ML prediction. Static/profile-image videos, recordings without sufficient full-body visibility, and recordings with no complete squat repetition return `status: rejected`, `error_code: INVALID_SQUAT_VIDEO`, and `movement_score: null`. They do not receive a normal score or a `squat_correct` ML prediction. Rejected inputs include friendly re-recording guidance, low analysis confidence, `input_validity` measurements, and validation warnings.

Run the complete validation:

```powershell
python -m pytest
Set-Location frontend
npm test
```

See [the hardening plan](docs/squat_accuracy_hardening_plan.md), [rep-counting method](docs/squat_rep_counting_method.md), [confidence design](docs/analysis_confidence_design.md), and [score breakdown](docs/squat_scoring_breakdown.md).

### Sprint 6.6 Rep Count Stabilization

Rep counting removes isolated angle spikes, interpolates only short gaps, breaks continuity across long or low-confidence gaps, requires sustained movement phases, aggregates noisy partial candidates, and reports reasoned `partial_rep_events`. Low rep confidence recommends manual review but does not reject an otherwise valid squat attempt.

Create and complete the manual rep-count template, then generate accuracy evidence:

```powershell
python scripts/validate_rep_counts.py
```

The first run creates `data/processed/labels/custom_squat_manual_rep_counts.csv`. After manually entering `expected_reps`, rerun to write validation results under `reports/rep_count_validation/`. See [the stabilization report](docs/rep_count_stabilization_report.md).

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
python scripts/prepare_augmented_squat_videos.py
python scripts/validate_rep_counts.py
python scripts/prepare_squat_training_dataset_v2.py --include-augmented
python scripts/train_squat_baseline_v2.py
python scripts/evaluate_squat_baseline_v2.py
python scripts/predict_squat_baseline_v2.py --video-path data/raw/custom_videos/squat_correct/squat_correct_009.mp4
python -m pytest
```

The current v2 run contains 23 real videos, zero augmented feature rows, and zero completed manual rep-count reviews. It classified all three real protected clips correctly, versus two of three for the immutable 16-video Sprint 5 reference. This sample is far too small and incomplete to demonstrate generalization, so ML remains optional and disabled by default. Augmented holdout variants are never treated as independent evaluation samples. See the [dataset expansion plan](docs/sprint_7_dataset_expansion_plan.md), [augmented data policy](docs/augmented_data_policy.md), [reliability report](docs/sprint_7_model_reliability_report.md), [v2 evaluation](docs/model_evaluation_report_v2.md), and [model versioning policy](docs/ml_model_versioning_policy.md).

## Sprint 7.5 - Multi-Dataset Integration and Registry

Sprint 7.5 audits heterogeneous raw datasets and adds a conservative registry, starter label mapping, dataset adapters, modality guard, v3 candidate inventory, and dashboard JSON export. It does not train v3, add exercises, or mix sensor/skeleton data into the squat video model.

```powershell
python scripts/audit_raw_datasets.py
python scripts/build_dataset_registry.py
python scripts/create_exercise_label_mapping.py
python scripts/prepare_squat_training_dataset_v3.py
python scripts/export_dataset_dashboard_summary.py
python -m pytest
```

Only `custom_videos` currently passes all squat-video compatibility gates. REHAB24-6 is mixed, Zenodo is image-only, UCI is sensor time series, UI-PRMD/DynTherapy/KiMoRe require source-specific adapters, Squat Kaggle needs label/provenance review, and UCO plus the physical-therapy folder are missing or incomplete. See the [integration plan](docs/sprint_7_5_multi_dataset_integration_plan.md), [registry design](docs/dataset_registry_design.md), [adapter policy](docs/dataset_adapter_policy.md), [modality guard](docs/modality_guard_policy.md), and [v3 candidate policy](docs/squat_training_dataset_v3_candidate_policy.md).

## Sprint 8A - Clinical/Data Validation and Model Reliability

Sprint 8A adds a privacy-conscious human annotation registry, validation reporting, participant-grouped split preparation, and error analysis for the existing squat v2 candidate. It does not add exercises or clinical claims. The rule-based analyzer remains primary and v2 remains experimental.

Run from the project root:

```powershell
python scripts/create_manual_annotation_template.py
python scripts/validate_manual_rep_annotations.py
python scripts/create_participant_metadata_template.py
python scripts/create_participant_grouped_split.py
python scripts/evaluate_rep_count_accuracy.py
python scripts/analyze_model_errors_v2.py
python -m pytest
```

Blank human fields are never inferred. Manual annotations and a real participant-grouped holdout are required before model promotion. Until participant IDs and manual rep counts are completed, the grouped split records rows as unassigned and ML remains experimental. The rule-based analyzer remains primary. See the [Sprint 8A plan](docs/sprint_8a_clinical_data_validation_plan.md), [validation report](docs/sprint_8a_clinical_data_validation_report.md), [annotation protocol](docs/manual_annotation_protocol.md), [participant-grouped evaluation](docs/participant_grouped_evaluation.md), and [promotion criteria](docs/model_promotion_criteria.md).

## Sprint 9 - Sit-to-Stand Analyzer

PhysioVision AI now includes a second selectable, rule-based movement analyzer for repeated sit-to-stand exercise. The existing squat endpoint and UI remain available. Sit-to-stand ML is not available; it returns an explicit disabled result, and rule-based interpretation remains primary.

```powershell
python -m pytest
Set-Location backend
python -m uvicorn app.main:app --reload
```

In another terminal:

```powershell
Set-Location frontend
npm install
npm test
npm run dev
```

API endpoints:

- `POST /api/v1/analyze/squat`
- `POST /api/v1/analyze/sit-to-stand`

Both accept optional overlay, report, and frame-data query flags. Sit-to-stand uses engineering thresholds, not clinically validated cutoffs, and does not diagnose fall risk, disease, or impairment. See the [analyzer design](docs/sit_to_stand_analyzer_design.md), [threshold notes](docs/sit_to_stand_thresholds.md), and [safety notes](docs/sit_to_stand_safety_notes.md).

## Pretrained Pose Backbone Benchmarking

PhysioVision AI uses pretrained pose estimation models for landmark detection, while biomechanics interpretation is handled by rule-based and experimental ML layers. Pose landmarks are measurements, not diagnoses or clinically validated decisions. MediaPipe/BlazePose remains the production default and the rule-based analyzer remains primary.

The optional offline benchmark layer compares backbone coverage, confidence, angle stability, speed, and downstream rule agreement without changing the API:

```powershell
$env:POSE_BACKEND = "mediapipe"
python scripts/benchmark_pose_backends.py
```

MoveNet Lightning and Thunder have stable interface placeholders but remain deferred because TensorFlow/model assets are not application dependencies. See [the pretrained pose strategy](docs/pretrained_pose_model_strategy.md) and [benchmark plan](docs/pose_model_benchmark_plan.md).
