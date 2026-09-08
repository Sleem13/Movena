# Physiology LLM Capstone Integration Plan

## Source Reviewed

Local reference source:
`C:/Users/NewAdmin/Desktop/Physiology-LLM-Capstone-main/`

Movena should treat this project as an external reference implementation, not
as an app to merge wholesale. The valuable parts are its exercise-specific
movement intelligence, UI-PRMD feature mapping, packaged Keras model artifacts,
knowledge-grounded cue snippets, goals/achievement concepts, and realtime
latency lessons.

Movena remains the product and architecture baseline: FastAPI backend, React
web client, Expo mobile client, authenticated history, therapist-guided care
plans, privacy gates, and rule-based analyzers as the primary source of truth.

## Integration Decision

- Do not port the PyQt desktop shell, QWebEngine dashboard, local MJPEG webcam
  server, hardcoded desktop key, or client-side Groq key storage.
- Do not replace Movena's existing analyzers with imported Keras outputs.
- Do not add TensorFlow/Keras to the default backend dependency set.
- Adopt the model-backed scoring only as an optional, experimental ML second
  opinion after provenance, license, validation, and performance gates pass.
- Adopt feedback snippets only after clinician review and with conservative
  educational wording.

## Reuse Candidates

| Candidate | Source files | Movena destination | Decision |
| --- | --- | --- | --- |
| UI-PRMD landmark adapter | `src/engine.py` | `backend/app/services/prmd_feature_adapter_service.py` | Reimplement with tests. |
| Per-exercise sequence specs | `src/engine.py`, analyzer modules | ML model catalog metadata | Reuse as metadata after validation. |
| Keras form-quality models | `models/*.keras` | Optional model pack | Gate on license, hashes, model cards, conversion or isolated runtime. |
| Knowledge cue snippets | `src/feedback_knowledge_base.py` | Backend feedback knowledge service | Reword and clinician-review before use. |
| Goal/achievement ideas | `src/goals.py`, `frontend/app.js` | Server-derived badges/care-plan milestones | Recreate, do not copy client wrapper. |
| Realtime latency lessons | `latency_power_results.txt` | Realtime coaching ADR | Reuse measurement approach and TTS locking idea. |
| Training/evaluation scripts | `scripts/*.py` | Optional research provenance only | Keep out of production path. |

## Model Mapping

| Source model | Source exercise | Movena mapping | Notes |
| --- | --- | --- | --- |
| `deep_squat_robust.keras` | Deep Squat | `bodyweight_squat` | Similar but not identical protocol; second opinion only. |
| `sit_to_stand_robust.keras` | Sit to Stand | `sit_to_stand` | Good candidate after fixture validation. |
| `knee_extension_robust.keras` | Knee Extension | `knee_extension` | Good candidate after side/view validation. |
| `lateral_raise.keras` / `w_raise_robust.keras` | Lateral Raise / W Raise | `shoulder_abduction` | Resolve duplicate source naming before import. |
| `pushup_robust.keras` | Push-Up | `push_up` | Second opinion only; keep Movena validity gates primary. |
| `bicep_curl_robust.keras` | Bicep Curl | `bicep_curl` | Classifier for cheat categories, not numeric form score. |
| `hip_march_robust.keras` | Hip March | New `hip_march` or `hip_flexion` | Requires protocol, metadata, analyzer, and UI support. |
| `wall_pushup_robust.keras` | Wall Push-Up | New `wall_pushup` | Requires new rule-based analyzer first. |
| `shoulder_extension_robust.keras` | Shoulder Extension | New `shoulder_extension` | Requires new rule-based analyzer first. |
| `shoulder_scaption_robust.keras` | Shoulder Scaption | New `shoulder_scaption` | Requires new rule-based analyzer first. |

## Required Gates

### 1. License And Provenance

- Confirm reuse rights for source code, model files, UI assets, and dataset
  derivatives. The reviewed folder does not include a `LICENSE` file even
  though the README claims MIT.
- Record SHA-256 for every imported model file.
- Add model cards describing source, dataset, intended use, excluded use,
  metrics, known leakage caveats, and validation status.
- Keep the imported repo excluded from public commits until clearance is done.

### 2. Dependency Isolation

Movena's current core environment intentionally excludes TensorFlow/Keras. Use
one of these paths:

1. Preferred: convert Keras models to ONNX or TFLite and load them through a
   small optional inference provider.
2. Acceptable for research only: create `requirements-keras.txt` and keep
   TensorFlow behind an explicit feature flag.
3. Longer term: run TensorFlow in an isolated model-worker service with a
   narrow internal API and no direct access to user identity.

If the optional provider is missing, Movena must continue returning
`provider_status="not_configured"` and keep normal analysis behavior.

### 3. PRMD Adapter Validation

Build a tested adapter that maps Movena pose frames into the 22-joint UI-PRMD
feature contract used by the source models. Validation must cover:

- MediaPipe 33-landmark to UI-PRMD 22-joint ordering.
- Optional mirror handling.
- Per-exercise sequence length.
- Per-exercise normalization, especially pelvis-width and torso-length scale.
- Missing landmarks, low visibility, subject changes, and empty sequences.

The source ablation results show normalization is mandatory; raw landmarks
should never be sent directly to these models.

### 4. Safety And Product Semantics

- Rule-based validity, rep counting, scoring, and safety warnings remain
  primary.
- ML outputs may add confidence context, labels, or a second opinion only after
  the primary analyzer accepts the exercise attempt.
- ML disagreement must not override a rejected attempt or clear a warning.
- Output copy must avoid "doctor score", diagnosis, treatment, recovery-time,
  or safety-clearance claims.
- Any LLM-generated cue requires explicit user consent, a server-side key,
  audit logging, redaction, and a deterministic fallback.

## Implementation Phases

### Phase A: Documentation And Inventory

- Add this integration memo.
- Maintain the completed inventory in
  `docs/external_capstone_model_inventory.md`, including filename, exercise
  mapping, SHA-256, size, expected input shape, output meaning, and clearance
  status.
- Add a license/provenance blocker to the release checklist.

### Phase B: Adapter And Catalog

- Implement `prmd_feature_adapter_service.py`.
- Add a catalog schema for form-quality models:
  `exercise_id`, `source_model`, `model_mode`, `input_shape`,
  `normalizer`, `output_type`, `raw_min`, `raw_max`, `sha256`, and
  `validation_status`.
- Add unit tests with golden synthetic landmarks.

### Phase C: Optional Inference Provider

- Implemented a governed optional Keras provider compatible with Movena's
  existing ML second-opinion contract.
- Selected `sit_to_stand` as the first candidate.
- Kept the external catalog entry disabled and approval-blocked.
- Added readiness, missing/runtime/hash/path, shape, output, and synthetic
  inference coverage. The real Linux artifact smoke test remains required.

### Phase D: Feedback Knowledge Base

- Convert the source snippets into conservative Movena cue templates.
- Add clinician review status per snippet.
- Use deterministic snippets first; defer LLM cue generation.

### Phase E: New Exercise Expansion

Add new source-backed exercises only after rule-based analyzers and validation
exist:

1. `wall_pushup`
2. `hip_march` or `hip_flexion`
3. `shoulder_extension`
4. `shoulder_scaption`

Each exercise needs metadata, camera guidance, backend analyzer, API tests,
frontend/mobile route coverage, fixtures, and safety copy.

### Phase F: Goals And Achievements

Recreate achievements as server-derived Movena badges tied to authenticated
session records and therapist-guided care plans. Do not copy the source
desktop API wrapper or hardcoded key.

Candidate badges:

- First completed session.
- Consistent weekly sessions.
- Therapist-plan adherence streak.
- Total completed reps.
- High-confidence movement streak.

## Immediate Next Sprint

Completed in the first integration slice:

1. Produced the model inventory and SHA-256 manifest.
2. Added PRMD adapter unit tests using synthetic landmark fixtures.
3. Implemented the adapter without enabling inference.
4. Added a disabled optional provider entry for `sit_to_stand`.

Next:

1. Prepare conversion research for ONNX/TFLite before adding TensorFlow to any
   environment.

## Blockers Before Production Use

- Formal license confirmation for code, model files, assets, and training data.
- Trademark/domain clearance for Movena remains unresolved for public launch.
- Independent validation on Movena fixture videos.
- Clinician review of cue text and exercise protocols.
- Privacy/security review for any realtime camera or LLM feedback path.
