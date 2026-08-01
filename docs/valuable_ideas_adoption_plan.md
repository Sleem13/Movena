# Valuable Ideas Adoption Plan

## Decision

PhysioVision AI remains the product and architecture baseline. The imported
`Powered-Physiotherapy-System-master` project is a concept reference only and
must not be merged, deployed, or used with real user or patient data.

The useful ideas will be reimplemented within PhysioVision's existing safety,
privacy, testing, authentication, and deployment controls. Third-party code,
models, datasets, prompts, assets, and claims require provenance and license
review before any reuse.

## Immediate Containment

- Keep the imported prototype excluded from Git commits.
- Rotate or revoke every credential found in the imported source.
- Do not copy its plaintext-password authentication or permissive CORS setup.
- Do not use its unvalidated accuracy, therapy, recovery-time, or diet claims.
- Do not send health attributes or movement data to an external AI service.

## Phase 1 — Accessible Feedback Foundation

### Scope

- Add a small localization framework with English and Arabic app-shell/result
  coverage and a persistent language preference.
- Add optional on-device spoken result feedback using the browser Web Speech
  API.
- Keep speech user-initiated, cancellable, and unavailable when the browser
  does not support it.
- Do not upload or retain audio. Do not use an external TTS provider.

### Acceptance Gate

- Existing analysis behavior and safety language remain unchanged.
- Language selection is keyboard-accessible and persists locally.
- Spoken feedback uses only the current in-browser report.
- Unsupported browsers fail safely without blocking result review.
- Frontend tests and production build pass.

## Phase 2 — Real-Time Coaching Technical Spike

### Scope

- Capture the camera on the user device, never with server-side
  `VideoCapture(0)`.
- Compare on-device landmark extraction with authenticated WebSocket/WebRTC
  transport of derived landmarks or deliberately sampled frames.
- Reuse the existing exercise validity, phase, confidence, scoring, and safety
  services instead of creating a parallel analyzer stack.
- Add visibility checks, latency measurement, rate limiting, reconnect rules,
  and explicit camera consent.

### Acceptance Gate

- No raw camera stream is retained by default.
- The user can stop capture immediately and see a clear active-camera state.
- P95 feedback latency and device CPU/battery impact are measured.
- Low-confidence feedback is suppressed rather than guessed.
- Threat, privacy, and mobile/browser compatibility reviews pass.

## Phase 3 — Real Progress Dashboard

### Scope

- Build longitudinal views only from persisted, authenticated session metrics.
- Show exercise, date, rep count, confidence, movement observations, and trend
  provenance.
- Never fabricate percentages or infer clinical recovery.

### Acceptance Gate

- Every displayed metric maps to an API/database field.
- Empty, expired, and low-confidence data have explicit states.
- Authorization prevents cross-user session access.

## Phase 4 — Exercise Expansion Research

### Candidate Order

1. Lunge
2. Straight-leg raise
3. Step-up or heel raise
4. Balance/warrior-style static pose research

Each candidate requires an exercise-specific protocol, landmark/view rules,
annotation guide, validity gate, state machine, conservative feedback,
fixtures, and independent validation. Imported model files are not accepted as
evidence of accuracy.

## Phase 5 — Constrained Educational Assistant

This phase is deferred until privacy and content-governance controls exist. Any
assistant must use a clinician-reviewed, citation-backed knowledge base and
remain educational. It must not diagnose, prescribe treatment, create a diet
plan, estimate recovery time, or personalize medical advice from health data.

## Delivery Order

1. Complete Phase 1. **Status: complete.**
2. Write the real-time coaching architecture decision record and prototype
   camera/landmark capture behind a disabled feature flag. **Status:
   complete as a disabled technical spike; see
   `docs/realtime_coaching_technical_spike_adr.md`.**
3. Improve longitudinal progress views using existing session records.
   **Status: next.**
4. Begin lunge protocol and dataset feasibility work. **Status: not started.**
5. Reassess the educational assistant only after the closed-pilot gate.
   **Status: deferred.**
