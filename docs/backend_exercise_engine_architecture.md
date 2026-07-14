# Backend Exercise Engine Architecture

## Current-to-Target Strategy

The existing squat services remain the reference implementation. Migration should be incremental and behavior-preserving; a directory move is not worth destabilizing validity, counting, feedback, artifacts, or the API.

Target structure:

```text
backend/app/exercises/
  base.py
  registry.py
  squat/
    analyzer.py
    thresholds.py
    feedback.py
    schemas.py
  sit_to_stand/
    analyzer.py
    thresholds.py
    feedback.py
    schemas.py
  knee_extension/
    analyzer.py
    thresholds.py
    feedback.py
    schemas.py
```

Only `squat` should be registered as active until the next exercise completes its own validation gates.

## Core Contracts

`ExerciseAnalyzer` should expose immutable metadata and one analysis operation:

```python
class ExerciseAnalyzer(Protocol):
    exercise_id: str
    display_name: str
    version: str
    supported_views: tuple[str, ...]

    def analyze(self, pose_sequence, options) -> ExerciseAnalysisResult: ...
```

The shared result envelope contains exercise, analyzer version, status, repetitions, metrics, score or null, detected observations, feedback, confidence, validity, limitations, and optional frame details. Exercise-specific metrics live in a typed `metrics` object so knee/hip/trunk fields are not falsely required for every movement.

The registry resolves a documented exercise ID to one analyzer instance and rejects unknown or inactive exercises. Registration is explicit at startup; dynamic imports and user-supplied module names are prohibited.

## Shared Services

- Upload validation and temporary media lifecycle.
- Pose estimation backend and landmark contracts.
- Signal filtering/interpolation primitives.
- Common geometry and angle calculations.
- Pose visibility and recording-quality assessment.
- Confidence composition framework.
- Artifact, overlay, report, logging, and error-envelope infrastructure.

Shared code provides mechanisms, not universal biomechanics thresholds.

## Exercise-Specific Responsibilities

- Required landmarks and supported camera views.
- Input-validity and complete-attempt definition.
- Phase/state machine and repetition logic.
- Threshold values and their version/provenance.
- Metrics, observations, score composition, and feedback wording.
- Frame warnings, overlay emphasis, and report sections.

Sit-to-stand must not inherit squat depth thresholds merely because both involve knee flexion.

## Migration Plan

1. **Keep the current route unchanged:** retain `/api/v1/analyze/squat` and its tests as golden behavior.
2. **Introduce the base interface:** add `base.py` and an explicit registry with squat as the only active entry.
3. **Wrap squat behind the interface:** delegate to `analyze_squat_landmarks` without moving or rewriting its internal logic.
4. **Add sit-to-stand later:** implement it as an independent module only after dedicated data, protocol, and expert review.
5. **Expose a generic route later:** route `POST /api/v1/analyze/{exercise_id}` through the registry while retaining the squat endpoint as a backward-compatible alias.

After parity is established, move squat thresholds, feedback, schemas, and analyzer code one boundary at a time. Any legacy-route deprecation requires a versioned API change and migration window.

## Testing and Observability

Every analyzer needs unit tests for geometry, validity, phases, confidence, safety wording, and valid/invalid fixtures; contract tests across all active analyzers; endpoint compatibility tests; and resource/timeout tests. Logs include exercise ID, analyzer version, processing stage, duration, and opaque request ID, never raw media or personal data.
