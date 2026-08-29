# Phase 0 + Phase 1 implementation checklist

This checklist maps `CODEX_Live_Exercise_Coaching_PhysioVision_Patch_Plan.md` to the existing repository. It records the state before the additive Phase 1 patch and prevents duplicate modules.

## Phase 0 — audit and stabilization

- [x] FastAPI remains the backend foundation (`backend/app/main.py`, versioned routers under `backend/app/api/v1`).
- [x] React/Vite remains the web foundation (`frontend/src/App.jsx`).
- [x] Expo Router remains the mobile foundation (`mobile/app`).
- [x] Existing auth, role authorization, protected Super Admin behavior, patient ownership, and therapist assignment checks are reused.
- [x] Existing analysis endpoints, durable analysis jobs, recognition, session history, artifacts, overlays, and PDF reports remain backward compatible.
- [x] Alembic is present. `0001` establishes the care baseline; subsequent migrations are additive.
- [x] Baseline verified before this batch: 298 backend tests, 117 frontend tests, and the frontend production build passed.
- [x] Existing appointments, telemedicine provider abstraction, notifications, catalog, and commerce code came from earlier approved work. They are preserved but are not expanded in this Phase 1 batch.
- [ ] Activate production PostgreSQL only after the deployment migration and backup/restore gates in `docs/care_platform_launch_gate.md` pass.

## Phase 1 — rehabilitation core

- [x] Patient-owned Today API and responsive Today dashboards exist on web and mobile.
- [x] Therapist-owned rehabilitation plans support title, dates, status, dosage, schedule days, instructions, precautions, and optional media requests.
- [x] Daily completion supports completed, partial, and not-completed states with idempotent upsert behavior.
- [x] Pain before/after, difficulty, and patient comments are stored separately from AI metrics.
- [x] Therapist access to patient plans, adherence, sessions, and progress is assignment-scoped.
- [x] Basic 7-day adherence and pain summaries are available.
- [x] Add fatigue/exertion to completion records and surface all recorded outcomes in Today and therapist review.
- [x] Add rest interval, tempo, target ROM, target score, and explicit AI/video requirements to assigned exercises.
- [x] Add an explicit, ownership-validated link between a saved PhysioVision analysis session and an assigned exercise completion.
- [x] Preserve plan history by treating dosage replacement as a new plan/revision; never overwrite completed-plan history.
- [x] Verify upgrade and downgrade of the Phase 1 migration on a disposable database.
- [x] Run backend, frontend, mobile typecheck/tests, and production builds after implementation.

## Safety and compatibility invariants

- AI output remains movement-analysis data, never diagnosis or autonomous treatment.
- Manual completion remains available when AI is not required.
- High pain creates a therapist review notification and never changes treatment automatically.
- Existing `/analyze`, session-history, exercise-library, and analysis API flows remain available.
- Medical content is never exposed through the Super Admin operational workflow; it uses de-identified references.
