# Mobile App Deployment Roadmap

## Deployment Position

The web application remains the reference client. Mobile is introduced after API, session, privacy, and retention contracts stabilize. The first mobile release sends captured video to the backend; pose inference and movement analysis do not run on-device.

## Stage 1 - Mobile-Ready Backend

- Stable versioned exercise and session contracts.
- Short-lived upload credentials or authenticated multipart upload.
- Idempotency, progress states, retry-safe processing, cancellation, and artifact expiration.
- Mobile-oriented file-size, duration, codec, and network error messages.
- Explicit consent and retention selection before upload.

## Stage 2 - Internal Expo Prototype

- Camera permission and media-library selection.
- Recording guide and full-body framing checklist.
- Upload progress, background interruption recovery, and result rendering.
- Squat as the only active exercise; other catalog entries marked unavailable.

## Stage 3 - Patient Pilot

- Session history and report sharing.
- Accessibility, low-bandwidth behavior, analytics consent, crash reporting, and support flow.
- Secure token storage and automatic session expiration.
- Store review with accurate educational-use positioning.

## Stage 4 - Therapist-Linked Mobile

- Assigned exercise list, plan context, patient-reported pain/symptoms, and controlled sharing.
- Therapist review status without implying automated clearance.

## Stage 5 - On-Device Feasibility Research

Evaluate latency, battery, thermal load, model size, device fragmentation, update governance, and privacy benefits. On-device analysis stays deferred until it matches backend validity and confidence behavior and has a safe version/rollback mechanism.

