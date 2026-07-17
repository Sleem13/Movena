# Exercise Taxonomy

The canonical taxonomy separates dataset labels from supported application analyzers. Only `bodyweight_squat` and `sit_to_stand` have `supported_in_app=true`. Every other exercise is planned, unknown, or a manual-mapping category—not a working feature.

Mappings preserve the raw label, record the normalized exercise ID, and require manual review when provenance or meaning is uncertain. Taxonomy membership is not clinical validation and does not justify reusing thresholds between exercises.
