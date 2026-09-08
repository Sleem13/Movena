# Custom Dataset Collection Protocol

## Purpose

This protocol defines how to collect Movena squat videos for research and product validation. The immediate focus is the squat MVP. Future exercises can reuse the same file naming, consent, labeling, and safety structure.

## Safety Disclaimer

This collection protocol is for exercise monitoring and educational research support only. It does not replace assessment by a licensed physiotherapist. Participants should not perform any exercise that causes pain, dizziness, instability, shortness of breath, or symptoms that feel unsafe.

## Consent Note

Collect videos only with documented participant consent. Consent records should explain:

- What data is collected.
- How videos and derived landmarks will be stored.
- Who can access the data.
- Whether videos may be used for research, demos, or model development.
- How a participant can request deletion.

Do not commit raw participant videos or identifiable metadata to Git.

## Recording Setup

### Camera

- Use a smartphone or webcam with stable placement.
- Record at 720p or higher when possible.
- Use 30 FPS when available.
- Keep the camera fixed; avoid handheld recordings.

### Lighting

- Use bright, even lighting.
- Avoid strong backlighting from windows.
- Avoid heavy shadows over knees, hips, and ankles.

### Clothing and Visibility

- Wear clothing that makes body outline visible.
- Avoid long coats, loose clothing, or objects blocking joints.
- Full body should remain in frame for the full set.

### Distance From Camera

- Stand far enough that head, shoulders, hips, knees, ankles, and feet are visible.
- Leave some margin around the body so MediaPipe does not lose landmarks at the top or bottom of the frame.
- For most phones, start around 2.5 to 4 meters from the camera and adjust based on framing.

## Required Views

### Front View

Use front view to label:

- Knee valgus
- Unstable balance
- Asymmetry
- Foot and knee alignment

Camera placement:

- Camera faces the participant directly.
- Lens should be around hip to chest height.
- Participant stands centered in frame.

### Side View

Use side view to label:

- Shallow depth
- Excessive trunk lean
- Hip hinge strategy
- Squat depth and phase timing

Camera placement:

- Camera is perpendicular to the participant.
- Lens should be around hip height when possible.
- The full side profile must remain visible.

## Repetition Protocol

- Record 5 repetitions per clip for MVP collection.
- Use a slow and controlled tempo.
- Rest between clips.
- Stop immediately if movement becomes painful or unsafe.

For each participant, target:

- 1 front-view correct squat clip.
- 1 side-view correct squat clip.
- 1 to 2 labeled issue clips only if safe and appropriate.

Do not ask participants to intentionally perform unsafe movement patterns if they cannot do so comfortably and under appropriate supervision.

## Required Labels

Use one primary label per clip:

- `correct`
- `shallow_depth`
- `knee_valgus`
- `excessive_trunk_lean`
- `unstable_balance`
- `fast_uncontrolled`
- `pain_reported`

Optional secondary labels may be added later in a metadata CSV.

## Metadata Fields

Recommended metadata file: `data/samples/metadata.csv`

Columns:

- `video_file`
- `subject_id`
- `session_id`
- `exercise_name`
- `view`
- `primary_label`
- `secondary_labels`
- `reps_planned`
- `reps_completed`
- `pain_reported`
- `notes`
- `consent_record_id`

## File Naming Convention

Use:

```text
subject-<id>_session-<id>_exercise-squat_view-<front|side>_label-<label>_repcount-<n>.mp4
```

Examples:

```text
subject-001_session-001_exercise-squat_view-front_label-correct_repcount-5.mp4
subject-001_session-001_exercise-squat_view-side_label-shallow_depth_repcount-5.mp4
subject-002_session-001_exercise-squat_view-front_label-knee_valgus_repcount-5.mp4
```

## Quality Checklist

Before accepting a clip:

- Full body remains in frame.
- Feet, knees, hips, shoulders, and head are visible.
- Camera is stable.
- Lighting is adequate.
- Repetition count is clear.
- Label matches the movement.
- Participant consent is recorded outside the repo.

## Storage

Place local videos under:

```text
data/samples/squat_correct/
data/samples/squat_knee_valgus/
data/samples/squat_shallow_depth/
data/samples/squat_trunk_lean/
```

Do not commit raw video data. Commit only documentation, scripts, schemas, and small synthetic examples if needed.
