# Exercise Coverage Matrix

The exercise coverage matrix groups unified metadata by exercise, dataset, and modality. It reports sample count, label quality, manual-review count, discovery-level training candidates, app support, rule-based analyzer status, and ML/DL readiness.

Readiness values are intentionally conservative:

- `ready_for_exploration`: enough reviewed discovery candidates for a bounded experiment; not promotion-ready.
- `needs_manual_mapping`: an exercise or label requires review.
- `insufficient_samples`: reviewed coverage is too small.
- `unsupported_modality`: the modality is mixed, unknown, or unresolved.
- `app_supported_no_model`: the app analyzer exists but reviewed model data does not.
- `research_only`: dataset coverage exists for a non-app exercise.

The matrix never activates a frontend exercise or establishes clinical validity. Generate it with `python scripts/build_exercise_coverage_matrix.py`.

