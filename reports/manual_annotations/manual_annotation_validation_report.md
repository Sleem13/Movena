# Manual Annotation Validation Report

**Status: INCOMPLETE**

This is an engineering/data-quality review, not clinical validation.

## Completion

- Total rows: 24
- Completed annotations: 0
- Annotation completion: 0.00%

## Missing and Invalid Fields

- Missing Expected Reps: 24
- Invalid Expected Reps: 0
- Missing Participant Id: 24
- Invalid Participant Id: 0
- Missing Session Id: 24
- Duplicate Video Path: 0
- Invalid View Type: 24
- Invalid Recording Quality: 24
- Invalid Annotation Confidence: 24
- Invalid Visible Body Region: 24
- Missing Exercise Label: 0

## Class Balance

- `squat_correct`: 13
- `squat_knee_valgus`: 4
- `squat_shallow_depth`: 2
- `squat_trunk_lean`: 4
- `unlabeled`: 1

## Participant Distribution

- None

## Dataset Source Distribution

- `custom_squat_videos`: 24

## Expected Reps Distribution

- `missing`: 24

## Recording Quality Distribution

- `missing`: 24

## Recommendations

- Complete rep counts and pseudonymous participant/session metadata through manual review.
- Use only the documented categorical values and resolve duplicate paths before freezing a split.
- Collect real videos for every missing or underrepresented class.
- Keep the model experimental until the promotion gates are met.
