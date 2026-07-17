# Knee Extension Analyzer Design

## Scope and movement model

The analyzer supports seated, open-chain knee extension viewed from the side. It chooses the left or right leg with the stronger average hip/knee/ankle visibility, calculates the selected knee angle, and observes hip/trunk geometry for context.

A complete repetition must progress through stable flexion, increasing knee angle, stable extension, decreasing knee angle, and return to flexion. Debouncing, smoothing, timing bounds, frame-gap resets, and partial-cycle accounting reduce double counts and noisy transitions.

## Validity gate

The response is rejected with `INVALID_KNEE_EXTENSION_VIDEO` unless there are enough pose frames, sufficient pose detection and selected-joint visibility, at least 30 degrees of knee-angle range, and at least one complete repetition. Rejected recordings have no movement score.

## Explainable scoring

Only valid recordings receive a score. The components are extension range, movement control, rep consistency, posture/landmark visibility, and rep completion. Observations such as limited visible extension, incomplete cycles, variable tempo, or possible trunk movement describe 2D evidence; they do not diagnose restriction, weakness, injury, pain, or treatment need.

## Known limitations

- Thresholds are engineering defaults pending representative expert review.
- 2D pose is sensitive to viewpoint, occlusion, clothing, and camera motion.
- The analyzer does not measure torque, strength, passive range, pain, tissue status, or safe resistance.
- The result is educational monitoring support and does not replace physiotherapist assessment.

