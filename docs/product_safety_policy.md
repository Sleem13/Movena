# Product Safety Policy

## Scope

PhysioVision AI provides educational movement-monitoring support. It does not diagnose injury or disease, determine fitness for activity, prescribe or modify treatment, or replace a licensed physiotherapist or other healthcare professional.

## Non-Negotiable Behaviors

- Reject static, invalid, zero-rep, or insufficient-visibility recordings rather than assign a normal movement score.
- Show pose quality, analysis confidence, limitations, and camera-view constraints with results.
- Warn clearly when confidence is low and recommend camera correction or professional review rather than over-interpreting the result.
- Keep experimental ML subordinate to validity and rule-based analysis; it cannot override rejection or safety messaging.
- Use observational wording such as “possible,” “may,” and “review,” not diagnostic labels.
- Do not infer pain, injury, pathology, recovery, fall risk, or treatment need from pose landmarks.
- Avoid logging raw media, personal identifiers, tokens, or health details.

## Camera and 2D Pose Limitations

Single-camera 2D pose estimates are affected by camera view, height, tilt, distance, lighting, clothing, occlusion, frame rate, video edits, and landmark errors. They do not measure full three-dimensional joint motion, force, tissue load, pain, or pathology. Front and side recordings support different observations, and an unsupported view must reduce confidence or cause rejection rather than produce a stronger claim.

## Stop and Seek Guidance

Users should stop the activity if pain increases, or if they experience dizziness, faintness, chest discomfort, unusual shortness of breath, new weakness/numbness, instability, or another concerning symptom. Urgent or severe symptoms require appropriate local urgent or emergency care. Product messaging must not attempt to triage emergencies algorithmically.

## Suggested UI Safety Messages

- “Stop if you feel pain, dizziness, or unusual discomfort.”
- “This feedback is for exercise monitoring and educational support only.”
- “Consult a licensed physiotherapist for clinical decisions.”
- “Low-confidence results should be reviewed manually.”

## Professional Review

Therapist review is preferred for clinical decisions, persistent symptoms, uncertain technique, low-confidence recordings, and exercise progression. Reports must retain their timestamp, exercise, analysis version, confidence, limitations, and disclaimer.

## Change Control

Each exercise, threshold, feedback rule, model, and user-facing safety statement requires versioning, regression tests, expert review, and rollback. Product release approval and clinical research approval are separate decisions.
