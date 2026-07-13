# Custom Squat Videos Validation Report

- Total videos found: 24
- Unsupported files: 0
- Videos with extracted landmarks: 24
- Landmark extraction failures: 0

## Videos Per Label

| Label | Videos |
|---|---:|
| `squat_correct` | 13 |
| `squat_shallow_depth` | 2 |
| `squat_knee_valgus` | 4 |
| `squat_trunk_lean` | 4 |
| `squat_fast_uncontrolled` | 0 |
| `unlabeled` | 1 |

## Unsupported Files

- None detected.

## Metadata Warnings

- `data\raw\custom_videos\squat_unlabeled\unlabeled.mp4`: Unrecognized label folder: squat_unlabeled. Review-only video; excluded from official supervised-label use until manually curated.

## Landmark Extraction

- Success: 24 video(s).
- No failed-video records are currently available.

## Recommendations

- Add consented validation videos for missing labels: `squat_fast_uncontrolled`.
- Review files under unrecognized folders and move them only after confirming the correct label.
- Keep raw videos local and obtain consent before using recordings for product validation.
