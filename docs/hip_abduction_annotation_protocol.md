# Hip Abduction Annotation Protocol

Use `data/processed/labels/hip_abduction_annotation_template.csv`. Record standing hip abduction from the front with the pelvis, both hips, moving hip, knee, ankle, and trunk visible. A valid rep starts near neutral, moves the leg laterally away from the body, reaches a clearly reviewed abducted phase, and returns near neutral without a continuity-breaking occlusion.

Reject or flag static clips, side-lying variants under this MVP, truncated cycles, unknown exercise identity, poor landmark visibility, incompatible views, major camera motion, or insufficient observed range. Allowed issue labels are `limited_observed_hip_abduction_range`, `insufficient_range_of_motion`, `poor_visibility`, `incomplete_repetition`, `inconsistent_tempo`, `possible_trunk_lean_compensation`, and `possible_pelvic_hiking_pattern`. These labels are observational and not diagnostic.

Annotators must enter participant/view, expected and observed reps, frame bounds, quality, reviewer, and review status. Use `unknown` rather than guessing. Ambiguous rows require adjudication. Candidate exports remain `requires_manual_review=true` and `training_ready=false` until a future governed promotion workflow.
