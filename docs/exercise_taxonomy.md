# Exercise Taxonomy

The canonical taxonomy separates dataset labels from supported application analyzers. `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction` have `supported_in_app=true`. Every other exercise is planned, unknown, or a manual-mapping category—not a working feature. Knee extension, shoulder abduction, and hip abduction are rule-based only; no exercise-specific ML model is available for them.

Mappings preserve the raw label, record the normalized exercise ID, and require manual review when provenance or meaning is uncertain. Taxonomy membership is not clinical validation and does not justify reusing thresholds between exercises.
