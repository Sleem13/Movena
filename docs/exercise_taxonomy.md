# Exercise Taxonomy

The canonical taxonomy separates dataset labels from supported application analyzers. `bodyweight_squat`, `sit_to_stand`, and `knee_extension` have `supported_in_app=true`. Every other exercise is planned, unknown, or a manual-mapping category—not a working feature. Knee extension is rule-based only; no ML model is available.

Mappings preserve the raw label, record the normalized exercise ID, and require manual review when provenance or meaning is uncertain. Taxonomy membership is not clinical validation and does not justify reusing thresholds between exercises.
