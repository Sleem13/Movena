# Real-Time Coaching Technical Spike ADR

## Status

Accepted as a disabled technical spike. Not enabled for private staging demos,
closed pilot use, public release, clinical decision-making, diagnosis, or
treatment prescription.

## Context

`docs/valuable_ideas_adoption_plan.md` identifies real-time coaching as a
valuable idea to investigate, but not to copy from the imported prototype. The
safe path is to evaluate camera capture, local derived signals, optional
on-device landmarks, latency, consent, and privacy behavior without creating a
parallel analyzer stack or storing raw camera streams.

## Decision

Movena will keep upload-based, rule-based analysis as the product
baseline. Real-time coaching remains behind the frontend feature flag:

```text
VITE_ENABLE_REALTIME_COACHING_SPIKE=true
```

The flag is unset by default, so no real-time coaching route appears in normal
development, staging, or production builds.

The spike captures camera video only on the user's device after an explicit
button press. It does not upload video, does not record audio, does not retain
frames, does not write session records, and does not produce medical advice.
The current prototype samples low-resolution frame-derived quality metrics and
can read a deliberately injected local landmark extractor if one is supplied by
a later experiment.

## Safety and Privacy Rules

- Camera access must be user initiated.
- The UI must show an active-camera state and a stop control.
- Stopping must immediately stop all media tracks.
- Audio capture is disabled.
- Raw frames and camera streams are not sent to the backend.
- Low-confidence or missing landmarks must suppress coaching feedback rather
  than guess.
- Any future transport must send only approved derived landmarks or deliberately
  sampled frames after privacy and threat review.
- Existing exercise validity, confidence, scoring, and safety services remain
  the source of truth.

## Technical Shape

The frontend spike lives in:

- `frontend/src/config/featureFlags.js`
- `frontend/src/pages/RealtimeCoachingSpike.jsx`

The route `/coach` is available only when the feature flag is explicitly true.
When enabled, the navigation shows a coaching spike entry. The page uses
`navigator.mediaDevices.getUserMedia` with `audio: false`, samples a small
canvas for non-retained frame-quality metrics, and stops tracks on unmount or
when the user clicks stop.

## Acceptance Evidence

- Feature flag defaults to disabled.
- Direct route selection falls back to Home unless the flag is true.
- Browser camera capture is local and user initiated.
- Optional landmark extraction is local-only and absent by default.
- Frontend tests cover feature flag parsing and the spike surface.

## Open Questions Before Any Pilot Exposure

- Which browser landmark backend is acceptable for mobile CPU, battery, and
  thermal limits?
- What P95 feedback latency is achievable on target devices?
- Should the system use local-only landmarks, authenticated WebSocket/WebRTC
  transport of derived landmarks, or no real-time transport at all?
- What rate limits and reconnect rules are required?
- How will camera consent, browser compatibility, and device support be
  documented for closed pilot reviewers?

## Non-Goals

- No clinical release.
- No public production release.
- No diagnosis, treatment prescription, recovery-time estimate, or diet advice.
- No use of imported prototype code, models, prompts, or claims.
