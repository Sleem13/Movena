# PhysioVision AI

PhysioVision AI is a video-based exercise coaching platform. It combines pose estimation, exercise-specific biomechanics rules, repetition tracking, temporal exercise recognition, annotated video, reports, session history, therapist-facing views, a React web client, and an Expo Android application.

The product supports movement review and coaching conversations. It does not diagnose conditions, prescribe treatment, or replace a licensed physiotherapist.

## Product surfaces

| Surface | Technology | Purpose |
|---|---|---|
| Backend API | FastAPI, OpenCV, MediaPipe, SQLAlchemy | Video processing, pose estimation, biomechanics analysis, recognition, reports, and sessions |
| Web application | React, Vite | Browser exercise selection, uploads, analysis, results, history, and coaching UI |
| Mobile application | Expo, React Native, Expo Router | Guided Android workflow for recording, recognition, analysis, and results |
| ML/DL training | PyTorch, XGBoost, scikit-learn | Temporal exercise recognition experiments and model artifacts |

## Main capabilities

- Exercise selection or automatic identification from a short video.
- Single-person pose tracking with subject-switch protection.
- Exercise-specific repetitions, joint angles, movement phases, and coaching feedback.
- Annotated video, PDF report, frame data, and session-history options.
- Authentication, protected sessions, and therapist dashboard foundations.
- Responsive web UI and a guided mobile UI with Home, Analyze, Exercises, History, and More navigation.
- Temporal GRU and XGBoost exercise-recognition candidates.

## Supported exercises

The registered analyzers cover:

- Bodyweight squat
- Sit-to-stand
- Knee extension
- Shoulder abduction
- Hip abduction
- Push-up
- Shoulder press
- Bicep curl

The recognition models currently classify bodyweight squat, push-up, shoulder press, bicep curl, and hammer curl. A recognized movement is always presented as a suggestion for confirmation before analysis.

## Architecture

```text
Web or Android client
        |
        | HTTPS multipart video upload
        v
FastAPI authentication and validation
        |
        +--> Exercise recognition --> ranked label suggestion
        |
        +--> Person detection/tracking --> selected subject track
        |
        +--> MediaPipe pose landmarks --> joint geometry
        |
        +--> Exercise analyzer --> reps, phases, issues, confidence
        |
        +--> Optional overlay, PDF, frame data, and saved session
```

## Repository layout

```text
backend/     FastAPI application, services, database, and API tests
frontend/    React/Vite web application
mobile/      Expo/React Native Android application
scripts/     Dataset preparation, evaluation, and ML/DL training scripts
models/      Versioned model artifacts and metadata
data/        Local dataset workspace; large data is not committed
tests/       Repository-level backend and model tests
docs/        Architecture, safety, datasets, deployment, QA, and development history
```

## Requirements

- Windows PowerShell examples below; equivalent commands work on macOS/Linux.
- Python 3.12.
- Node.js and npm.
- Git.
- Android Studio only when using an emulator or local native Android tooling.
- An Expo account for EAS cloud builds.

## Backend setup

Run from the repository root:

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file ..\.env --reload --host 127.0.0.1 --port 8000
```

Verify the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/exercises
```

For a physical phone on the same Wi-Fi, expose the backend on port `8010`:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file ..\.env --host 0.0.0.0 --port 8010
```

Use the computer's LAN IPv4 address in the mobile environment. Do not use `localhost` on a physical phone.

## Web frontend setup

Open another PowerShell terminal:

```powershell
Set-Location frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

The default frontend URL is `http://127.0.0.1:5173`. Set `VITE_API_BASE_URL` in `frontend/.env` when the backend runs elsewhere.

Production web verification:

```powershell
Set-Location frontend
npm test
npm run build
```

## Mobile setup

See [mobile/README.md](mobile/README.md) for the complete development, Android APK, and production AAB commands.

The short local-development sequence is:

```powershell
Set-Location mobile
npm ci
Copy-Item .env.example .env
npm run typecheck
npm test -- --runInBand
npx expo start --clear
```

## Android APK build

The exact internal Android build sequence is documented in [mobile/README.md](mobile/README.md#build-an-installable-android-apk). The configured `preview-staging` profile builds an installable APK and connects to the deployed HTTPS backend.

```powershell
Set-Location mobile
npm ci
npx expo install --check
npm run typecheck
npm test -- --runInBand
npx eas-cli login
npx eas-cli whoami
npx eas-cli build --platform android --profile preview-staging --non-interactive --wait
```

These commands are documentation only; run them manually when a new Android artifact is required.

## ML/DL environment and training

Install the optional recognition dependencies in the active project environment:

```powershell
python -m pip install -r requirements-ml.txt
```

Run dry checks before training:

```powershell
python scripts/train_exercise_pose_xgboost.py --dry-run
python scripts/train_exercise_pose_gru.py --dry-run
```

Train the candidates:

```powershell
python scripts/train_exercise_pose_xgboost.py
python scripts/train_exercise_pose_gru.py
```

Generated artifacts belong under `models/recognition/` with metadata, class labels, metrics, dataset provenance, and promotion status.

## Testing

Backend and model tests:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Web tests and build:

```powershell
Set-Location frontend
npm test
npm run build
```

Mobile tests and static validation:

```powershell
Set-Location mobile
npm run typecheck
npm test -- --runInBand
npx expo export --platform android
```

## Configuration

Important public client variables:

| Variable | Consumer | Example |
|---|---|---|
| `VITE_API_BASE_URL` | Web | `http://127.0.0.1:8000` |
| `EXPO_PUBLIC_API_BASE_URL` | Mobile | `https://name-physiovision-api-staging.onrender.com` |
| `EXPO_PUBLIC_APP_ENV` | Mobile | `development`, `staging`, or `production` |

Never place server secrets in `VITE_*` or `EXPO_PUBLIC_*`. Those values are included in client builds.

Backend configuration includes database, authentication, CORS, upload-size, artifact, report, overlay, history, and analysis-authentication controls. Use `.env.example` and `.env.staging.example` as the source templates.

## Dataset and model notes

- Split video data by participant, not by frame, to reduce leakage.
- Preserve label provenance and licensing.
- Keep training, validation, and final test subjects separate.
- Include multiple participants, camera views, clothing, lighting, backgrounds, and correct/incorrect technique.
- The exercise pose CSV is useful for baseline training but is not sufficient by itself for dependable real-world validation.
- Do not promote a model only from training accuracy; record held-out per-class precision, recall, F1, confusion matrix, and confidence calibration.

See [dataset strategy](docs/dataset_strategy.md), [recognition model card](docs/exercise_pose_recognition_model_card.md), and [adoption plan](docs/exercise_coaching_adoption_plan.md).

## Safety and privacy

- Use non-identifying test videos unless the complete privacy, consent, retention, and deletion workflow has been approved.
- Keep one athlete fully visible and exclude coaches, spotters, and bystanders where possible.
- Stop exercise if pain, dizziness, or unusual symptoms occur.
- Treat all scores and coaching feedback as educational estimates.
- Do not use the system for diagnosis, emergency guidance, or treatment decisions.

See [product safety policy](docs/product_safety_policy.md), [privacy checklist](docs/privacy_security_release_checklist.md), and [known limitations](docs/external_beta_known_limitations.md).

## Documentation

- [Development journey](docs/development_journey.md)
- [Mobile guide](mobile/README.md)
- [Mobile API contract](docs/mobile_api_contract.md)
- [Cloud deployment preparation](docs/cloud_deployment_preparation.md)
- [Exercise coaching adoption plan](docs/exercise_coaching_adoption_plan.md)
- [References](docs/references.md)

## License

See [LICENSE](LICENSE).
