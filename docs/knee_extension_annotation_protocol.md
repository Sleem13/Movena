# Knee Extension Annotation Protocol

Use `data/processed/labels/knee_extension_annotation_template.csv` for human review. One row represents one source video; augmented variants must retain lineage and must not be treated as independent participants.

Annotators should verify exercise identity, participant/session identifiers, exercising side, camera view, recording quality, expected complete repetitions, visible extension range quality, tempo quality, possible observable compensation, and critical-joint visibility. Use `unknown` instead of guessing. Notes should describe visible evidence and must not infer pain, stiffness, weakness, diagnosis, or safe loading.

Two independent reviews are recommended for rep counts and ambiguous movement labels. Conflicts should remain `review_status=needs_adjudication`. A candidate becomes training-ready only under a future documented promotion workflow after identity, label, participant grouping, and annotation quality are complete. The preparation script never grants that status.

