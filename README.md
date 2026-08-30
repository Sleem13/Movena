# PhysioVision AI

**AI-Assisted Rehabilitation Platform**<br>
*Move Better · Recover Faster · Live Healthier*

PhysioVision AI is a video-based exercise coaching and rehabilitation platform. It combines pose estimation, exercise-specific biomechanics rules, repetition tracking, temporal exercise recognition, annotated video, reports, session history, therapist-facing care workflows, bounded recovery and lifestyle coaching, and protected RehabRL decision support across React web and Expo Android clients.

The product supports movement review and coaching conversations. It does not diagnose conditions, prescribe treatment, or replace a licensed physiotherapist.

The integrated RehabRL workspace provides therapist-reviewed recommendation candidates, synthetic recovery simulation, prescription exercise exploration, and super-admin model operations. See the [integration guide](docs/rehab_rl_integration.md) for its architecture, security model, API, deployment, and verification status.

## Product surfaces

| Surface | Technology | Purpose |
|---|---|---|
| Backend API | FastAPI, OpenCV, MediaPipe, SQLAlchemy | Video processing, pose estimation, biomechanics analysis, recognition, reports, and sessions |
| Web application | React, Vite | Browser exercise selection, uploads, analysis, results, history, and coaching UI |
| Mobile application | Expo, React Native, Expo Router | Guided Android workflow for recording, recognition, analysis, and results |
| ML/DL training | PyTorch, XGBoost, scikit-learn | Temporal exercise recognition experiments and model artifacts |
| RehabRL decision support | Double Dueling DQN, NumPy/PyTorch | Clinician-reviewed recommendations, synthetic trajectories, and policy operations |
| Recovery coaching | FastAPI, React, SQLAlchemy | Patient-agreed goals, daily reflections, barriers, action plans, and clinical escalation |

## Main capabilities

- Exercise selection or automatic identification from a short video.
- Single-person pose tracking with subject-switch protection.
- Exercise-specific repetitions, joint angles, movement phases, and coaching feedback.
- Annotated video, PDF report, frame data, and session-history options.
- Authentication, protected sessions, and therapist dashboard foundations.
- Responsive web UI and a guided mobile UI with Home, Analyze, Exercises, History, and More navigation.
- Temporal GRU and XGBoost exercise-recognition candidates.
- Protected RehabRL workspace for stage-aware recommendation review, synthetic recovery simulation, and policy exercise exploration.
- Protected Recovery & Lifestyle Coaching workspace for patient-chosen SMART goals, non-diagnostic check-ins, therapist-reviewed action plans, and hard safety escalation.

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
        |
        +--> RehabRL policy --> clinician-reviewed recommendation or simulation
```

## Repository layout

```text
backend/     FastAPI application, embedded RehabRL engine, checkpoints, services, database, and API tests
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
.\scripts\start_backend.ps1 -Reload
```

Verify the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/exercises
```

For a physical phone on the same Wi-Fi, expose the backend on port `8010`:

```powershell
.\scripts\start_backend.ps1 -HostAddress 0.0.0.0 -Port 8010
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
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
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

## Rehabilitation workflow

The authenticated product now treats PhysioVision as the movement-intelligence engine inside a therapist-prescribed rehabilitation workflow. Phase 1 includes a patient Today dashboard on web and Expo, immutable plan replacement/history, scheduled exercise dosage, pain/difficulty/fatigue check-ins, patient comments, therapist outcome review, and an ownership-validated link from saved analysis sessions to assigned plan items. Direct analysis and session-history routes remain supported.

Apply schema changes with Alembic before starting an existing environment:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

The Phase 1 migration is reversible to revision `0003_data_rights` for validation on a disposable database. Production rollback still requires a reviewed backup/restore decision because clinical records must not be discarded casually. See [Phase 0 + Phase 1 checklist](docs/phase_0_1_implementation_checklist.md).

### Recovery & Lifestyle Coaching

Authenticated patients and assigned clinical users can open `/recovery-coaching`. Patients can create explicitly agreed SMART goals, record non-diagnostic daily reflections, identify barriers, and track progress. Therapists can review assigned patients and create patient-agreed action plans. New or worsening symptoms require clinical follow-up; an immediate concern pauses coaching, displays the organization-configured urgent pathway, creates a therapist notification, and records an audit event. Coaching never changes a prescription autonomously and does not provide diagnosis, psychotherapy, nutrition prescribing, or emergency care. See the [clinical and technical guide](docs/recovery_lifestyle_coaching.md).

### RehabRL decision support

Authenticated therapists, administrators, and super administrators can open `/rehab-policy` to review:

- Policy status and the active NumPy/CPU or PyTorch/CUDA backend.
- Stage-aware prescription candidates generated from clinician-entered patient-state measures.
- A searchable 26-condition clinical protocol catalog with red flags, precautions, phase goals, treatment options, progression criteria, and outcome measures.
- A mandatory clinician safety gate that withholds model/treatment output for unscreened, unattested, postoperative-order-incomplete, or red-flag-positive cases.
- A versioned MLOps model manifest with a SHA-256 contract fingerprint, checkpoint compatibility, intended-use limits, and release-monitoring requirements.
- Privacy-minimized decision audit IDs, rolling safety-hold metrics, and organization-configurable escalation guidance.
- Synthetic recovery trajectories for model evaluation.
- The policy's prescription exercise library.
- Super-admin-only model inspection, checkpoint restore, and training controls.

The packaged model still supports its original 12-condition state space. Additional cases are explicitly labeled as clinical protocol references and do not produce model confidence or Q-values. Patients cannot access this workspace or its API. All outputs require clinician review and must not be treated as autonomous prescriptions, diagnoses, or patient-specific outcome forecasts. See the [clinical protocol catalog](docs/rehab_clinical_protocols.md), [RehabRL integration guide](docs/rehab_rl_integration.md), and [improvement roadmap](docs/rehab_rl_improvement_roadmap.md).

## Testing

Backend and model tests:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Focused RehabRL integration tests:

```powershell
python -m pytest -q tests/test_rehab_rl_api.py tests/test_root_uvicorn_entrypoint.py
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

Backend configuration includes database, authentication, CORS, upload-size, artifact, report, overlay, history, and analysis-authentication controls. Use `.env.example`, `.env.staging.example`, and `.env.production.example` as the source templates. Production starts fail closed when authentication, HTTPS origins, SMTP delivery, database configuration, or secrets are unsafe.

RehabRL clinical governance uses the server-only variables `CLINICAL_ORGANIZATION_NAME`, `CLINICAL_ESCALATION_CONTACT`, and `CLINICAL_ESCALATION_INSTRUCTION`. Configure these for the deployment's approved urgent and emergency workflow; do not place them in public client variables.

### Protected super administrator

Provision the root account from server-only environment variables. Never expose these values through `VITE_*` or commit them:

```powershell
$env:SUPER_ADMIN_EMAIL="owner@example.com"
$env:SUPER_ADMIN_PASSWORD="use-a-unique-long-password"
$env:SUPER_ADMIN_FULL_NAME="Application Owner"
.\.venv\Scripts\python.exe scripts\seed_super_admin.py
```

Use `--reset` only for an intentional credential reset or promotion. Once signed in, the account-management console is available at `/admin/users`. The protected account cannot be changed, paused, demoted, password-reset, or deleted through the application API. Account actions against other users revoke affected sessions and create audit-log records.

### Email verification and password recovery

New public accounts persist their selected non-privileged role and a stable permission snapshot in the `users` table. Startup seeding and compatibility migrations do not replace existing roles. New accounts must verify their email before login or protected API/WebSocket access.

Development and the default Render staging blueprint use `EMAIL_DELIVERY_MODE=console`, which writes verification/reset links to backend logs. Staging validates SMTP settings when `EMAIL_DELIVERY_MODE=smtp`; production always requires SMTP. Before testing email flows in staging, set `FRONTEND_URL`, `EMAIL_FROM`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_USE_TLS` using server-only environment variables or a secret manager, then switch the delivery mode to `smtp`. The expiry and resend controls are `EMAIL_VERIFICATION_EXPIRE_MINUTES`, `PASSWORD_RESET_EXPIRE_MINUTES`, and `AUTH_EMAIL_RESEND_COOLDOWN_SECONDS`.

Authentication action endpoints:

- `POST /api/v1/auth/verify-email`
- `POST /api/v1/auth/resend-verification`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

Only SHA-256 token hashes are stored. Tokens expire, are invalidated after use, and password recovery revokes existing access tokens.

## Dataset and model notes

- Split video data by participant, not by frame, to reduce leakage.
- Preserve label provenance and licensing.
- Keep training, validation, and final test subjects separate.
- Include multiple participants, camera views, clothing, lighting, backgrounds, and correct/incorrect technique.
- The exercise pose CSV is useful for baseline training but is not sufficient by itself for dependable real-world validation.
- Do not promote a model only from training accuracy; record held-out per-class precision, recall, F1, confusion matrix, and confidence calibration.
- Do not promote a rehabilitation policy from simulated reward alone; require clinical baseline comparison, safety constraint evaluation, subgroup analysis, and documented clinician approval.

See [dataset strategy](docs/dataset_strategy.md), [recognition model card](docs/exercise_pose_recognition_model_card.md), and [adoption plan](docs/exercise_coaching_adoption_plan.md).

The integrated patient-care, scheduling, Daily, Paymob, privacy, and release status is tracked in the [care-platform launch gate](docs/care_platform_launch_gate.md). It deliberately keeps production and real-patient use blocked until the external security, provider, device, clinical, and legal evidence is complete.

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
- [RehabRL integration guide](docs/rehab_rl_integration.md)
- [RehabRL improvement roadmap](docs/rehab_rl_improvement_roadmap.md)
- [Recovery & Lifestyle Coaching clinical and technical guide](docs/recovery_lifestyle_coaching.md)
- [References](docs/references.md)

## License

See [LICENSE](LICENSE).
