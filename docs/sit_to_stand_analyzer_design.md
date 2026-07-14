# Sit-to-Stand Analyzer Design

## Scope

Sprint 9 adds `sit_to_stand` as the second active PhysioVision AI exercise. It analyzes repeated chair-stand movement using MediaPipe landmarks and transparent rules. It does not estimate fall risk, diagnose disease, or replace physiotherapist assessment.

## Movement Pipeline

1. Validate the upload and extract shoulders, hips, knees, ankles, and feet with the existing pose service.
2. Calculate bilateral-average knee angle, midline hip angle, and trunk angle.
3. Suppress isolated angle spikes, short low-confidence gaps, and frame jitter.
4. Track `sitting -> rising -> standing -> lowering -> sitting`.
5. Count only cycles that reach standing, return to sitting, meet the minimum excursion, and satisfy duration safeguards.
6. Reject static, standing-only, sitting-only, low-visibility, and zero-repetition inputs before scoring.
7. Produce an explainable educational score from completion, control, trunk control, consistency, and pose confidence.

Rep events contain the start, standing, and end frames, duration, and observed knee-angle excursion. Partial cycles do not increase the completed count.

## Architecture

The implementation is isolated under `backend/app/exercises/sit_to_stand/`. The registry exposes `bodyweight_squat` and `sit_to_stand`, while the established squat route remains unmigrated to reduce regression risk. Upload validation, pose extraction, temporary artifacts, PDF generation, and overlay rendering are reused.

ML is unavailable for sit-to-stand. The API returns a disabled `ml_prediction` with an explicit warning. Rule-based analysis remains primary.

## Known Constraints

MediaPipe detects the body but not chair stability or chair geometry. Side or oblique recording is preferred. 2D angles are camera-dependent and do not measure strength, balance, pain, loading, fall risk, or clinical status.
