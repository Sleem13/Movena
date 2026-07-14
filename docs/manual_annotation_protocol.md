# Manual Squat Annotation Protocol

## Purpose and Safety

This protocol supports reproducible engineering evaluation of squat videos. It does not diagnose an impairment, establish treatment, or validate clinical effectiveness. Use pseudonymous participant and session identifiers; never enter names, dates of birth, contact information, diagnoses, or other directly identifying health information.

## Counting One Squat Rep

Count one complete repetition only when the visible movement cycle:

1. starts from standing or near-standing;
2. descends with visible hip and knee flexion;
3. reaches a lowest controlled position; and
4. returns to standing or near-standing.

The cycle must be visible enough to identify its start, bottom, and end. Do not count setup movements, camera movement, edit transitions, or repeated oscillations at the bottom as separate reps.

Partial attempts should be described in `notes` but not included in `expected_reps` unless the full movement-cycle definition is met. When the beginning or end is clipped, record whether `has_clear_start_position` and `has_clear_end_position` are false and request review rather than guessing.

## Required Labels

- `view_type`: `front`, `side`, `oblique`, or `unknown`.
- `recording_quality`: `high`, `medium`, `low`, or `unusable`.
- `visible_body_region`: `full_body`, `lower_body`, `partial_body`, or `unknown`.
- `annotation_confidence`: `high`, `medium`, or `low`.
- `camera_position`: concise controlled description such as `waist_height_side`; use `unknown` when not established.
- Visibility/start/end flags: use consistent boolean values (`true`/`false`) only after review.

Use `side` when the camera is predominantly perpendicular to the frontal plane, `front` when facing the participant, and `oblique` for intermediate views. Mark quality `unusable` when occlusion, framing, corruption, or lighting prevents a defensible movement count. Notes should explain ambiguity, partial attempts, occlusion, editing, or disagreement without adding clinical interpretation.

## Review Procedure

Review the complete clip, then inspect ambiguous boundaries frame by frame or at reduced speed. A second annotator should independently review low-confidence, poor-visibility, or disputed videos. Record disagreement and adjudication in notes; do not manufacture consensus. Augmented variants inherit source metadata only after lineage is confirmed and never count as independent holdout participants.

Run the validator after each annotation batch. A structurally complete file still does not establish clinical validity or justify clinical claims.
