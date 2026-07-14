# Manual Squat Annotation Protocol

## Safety and Privacy

Use pseudonymous identifiers only. Do not enter names, dates of birth, contact details, diagnoses, or other directly identifying or medical information. Annotation supports engineering evaluation and is not a clinical assessment.

## Required Fields

- `participant_id`: stable pseudonym matching `P[A-Za-z0-9_-]{2,31}`, such as `P001`.
- `session_id`: pseudonymous recording-session identifier, stable for clips from one session.
- `exercise_label`: one approved squat-quality label or `unlabeled` pending review.
- `expected_reps`: integer count of complete repetitions observed through frame review.
- `view_type`: `front`, `side`, `front_oblique`, or `side_oblique`.
- `recording_quality`: `poor`, `fair`, `good`, or `excellent`.
- `annotator`: pseudonymous reviewer identifier.
- `annotation_confidence`: `low`, `medium`, or `high`.
- `notes`: concise ambiguity, occlusion, editing, or counting-boundary notes without personal information.

## Rep Counting

A complete rep begins from a stable standing position, descends through a meaningful squat excursion, reaches the bottom region, ascends, and returns to stable standing. Do not count setup motion, partial demonstrations, edit transitions, or camera movement. Review slow motion and frame boundaries when uncertain. Record disagreement in notes and request a second reviewer instead of guessing.

## Augmented Videos

An augmented variant inherits the source participant, session, exercise label, and expected rep count only after lineage is confirmed. It is not an independent participant or validation sample. If a transformation obscures movement or changes interpretation, mark it unsuitable in the augmentation registry rather than forcing an annotation.

Run the validator after every annotation batch. A structurally valid file does not establish clinical validity or label correctness.

