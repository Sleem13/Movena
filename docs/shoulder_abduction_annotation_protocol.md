# Shoulder Abduction Annotation Protocol

Use `data/processed/labels/shoulder_abduction_annotation_template.csv`. Record a front view with the full upper body, shoulder, elbow, wrist, and trunk visible. A valid rep starts with the arm near the side, raises outward to the reviewed target region, and returns near the side without a continuity-breaking occlusion.

Reject or flag static clips, truncated cycles, unknown exercise identity, poor joint visibility, incompatible views, major camera motion, or insufficient range. Allowed issue labels are `limited_observed_abduction_range`, `insufficient_range_of_motion`, `poor_visibility`, `incomplete_repetition`, `inconsistent_tempo`, `possible_trunk_compensation`, and `possible_shoulder_hiking_pattern`. These are observational labels, not diagnoses.

Annotators must enter participant/view, expected and observed reps, frame bounds, quality, reviewer, and review status. Use `unknown` rather than guessing. Ambiguous rows require adjudication. Candidate exports remain `requires_manual_review=true` and `training_ready=false` until a future governed promotion workflow.
