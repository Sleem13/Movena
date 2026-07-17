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

ML/DL predictions are experimental unless a model has passed documented promotion criteria. They must remain visibly subordinate to the validity gate and primary rule-based biomechanics. Low-confidence analyses require manual review and must not be presented as reliable clinical conclusions.

## Knee-extension boundary

The system may describe visible extension range, complete cycles, tempo consistency, landmark visibility, and possible trunk movement. It must not infer joint stiffness, muscle weakness, pain, injury, passive range, safe resistance, or treatment progression.

## Shoulder-abduction boundary

The system may describe visible arm-raise range, complete cycles, tempo consistency, landmark visibility, possible trunk movement, and possible upward shoulder movement. It must not infer impingement, frozen shoulder, rotator-cuff weakness, injury, pain source, passive range, or treatment suitability.

## Hip-abduction boundary

The system may describe visible lateral leg range, complete cycles, tempo consistency, landmark visibility, possible trunk lean, and possible upward pelvic movement. It must not infer hip or gluteal weakness, instability, injury, pain source, balance capacity, passive range, or treatment suitability.
# Deployment privacy boundary

Deployment readiness does not imply clinical or patient-data readiness. Without authentication, authorization, consent, encryption governance, retention controls, and formal privacy/security review, this MVP must use synthetic or non-identifiable evaluation data only. Movement outputs are educational support and must not be represented as diagnosis or prescribed treatment.

Authentication controls access but does not validate clinical use, professional identity, consent, or appropriateness of an exercise. Role labels never grant clinical authority, and the development therapist dashboard is not a medical record.

Dataset availability, taxonomy mapping, model training, and app integration are separate gates. Unknown or weak labels require manual review, incompatible modalities cannot enter a pipeline, and no ML/DL model may automatically become an app or clinical output.

## Exercise-recognition boundary

Exercise recognition is an experimental routing aid, not clinical interpretation. It must never overwrite explicit selection, automatically invoke an analyzer, or provide feedback for an unsupported exercise. Suggestions require confirmation; absent or low-confidence output falls back to manual selection. Recognition confidence thresholds are product thresholds, not clinical safety thresholds.
