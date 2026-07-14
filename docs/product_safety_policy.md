# Product Safety Policy

## Scope

PhysioVision AI provides educational movement-monitoring support. It does not diagnose injury or disease, determine fitness for activity, prescribe or modify treatment, or replace a licensed physiotherapist or other healthcare professional.

## Non-Negotiable Behaviors

- Reject static, invalid, zero-rep, or insufficient-visibility recordings rather than assign a normal movement score.
- Show pose quality, analysis confidence, limitations, and camera-view constraints with results.
- Keep experimental ML subordinate to validity and rule-based analysis; it cannot override rejection or safety messaging.
- Use observational wording such as “possible,” “may,” and “review,” not diagnostic labels.
- Do not infer pain, injury, pathology, recovery, fall risk, or treatment need from pose landmarks.
- Avoid logging raw media, personal identifiers, tokens, or health details.

## Stop and Seek Guidance

Users should stop the activity if pain increases, or if they experience dizziness, faintness, chest discomfort, unusual shortness of breath, new weakness/numbness, instability, or another concerning symptom. Urgent or severe symptoms require appropriate local urgent or emergency care. Product messaging must not attempt to triage emergencies algorithmically.

## Professional Review

Therapist review is preferred for clinical decisions, persistent symptoms, uncertain technique, low-confidence recordings, and exercise progression. Reports must retain their timestamp, exercise, analysis version, confidence, limitations, and disclaimer.

## Change Control

Each exercise, threshold, feedback rule, model, and user-facing safety statement requires versioning, regression tests, expert review, and rollback. Product release approval and clinical research approval are separate decisions.
