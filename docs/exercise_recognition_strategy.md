# Exercise Recognition Strategy

## Purpose

Experimental exercise recognition estimates the likely exercise represented by movement data. Its future role is to help a user select the correct exercise-specific analyzer and support safe multi-exercise expansion. It is classification and routing assistance, not biomechanics interpretation, diagnosis, or treatment guidance.

## Current behavior

- Explicit user selection remains primary.
- Recognition output is labeled experimental and may be displayed only as a suggested exercise.
- Recognition never changes the selected analyzer, triggers analysis, or produces clinical feedback.
- If no validated model or compatible features exist, the service returns `not_available` or `not_implemented` without affecting app startup.

The app-supported analyzers are `bodyweight_squat`, `sit_to_stand`, `knee_extension`, and `shoulder_abduction`. Manual selection remains primary; neither newer exercise has a trained recognition or biomechanics model.

## Future behavior

A high-confidence result may suggest an available analyzer, but the user must confirm it. A low-confidence result asks for manual selection. A predicted exercise without an implemented analyzer is described as planned and cannot produce feedback.

Planned taxonomy labels include `hip_abduction`, `heel_raise`, `balance`, `walking_gait_screen`, `lunge`, and `step_up`. Dataset coverage for these labels does not mean an exercise works in the app.

Recognition datasets and features remain separated into video pose, skeleton sequence, sensor time-series, image pose, and tabular-feature tracks. Participant-grouped evaluation and adequate per-class recall are required before any candidate routing experiment. No recognition model is clinically validated, and rule-based analyzers remain primary.
