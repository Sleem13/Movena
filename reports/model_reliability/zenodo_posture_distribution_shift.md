# Zenodo Posture Distribution-Shift Review

## Scope

This report compares publisher train/test feature distributions among pose-detected images and separately audits pose-detection coverage. It does not establish participant independence or clinical validity.

- Prepared images: 3806
- Pose-detected images: 3770
- Detection rate: 0.991
- Visual-review sample: 18 high-confidence errors

## Pose Detection Coverage

| Split | Label | Prepared | Detected | Missed | Detection rate |
| --- | --- | ---: | ---: | ---: | ---: |
| test | bad_back | 338 | 326 | 12 | 0.964 |
| test | bad_heel | 321 | 320 | 1 | 0.997 |
| test | good | 310 | 310 | 0 | 1.000 |
| train | bad_back | 984 | 961 | 23 | 0.977 |
| train | bad_heel | 852 | 852 | 0 | 1.000 |
| train | good | 1001 | 1001 | 0 | 1.000 |

## Largest Overall Feature Shifts

| Feature | Train mean | Test mean | Standardized difference | KS statistic | KS p-value |
| --- | ---: | ---: | ---: | ---: | ---: |
| `right_hip_angle` | 56.093 | 71.843 | 0.854 | 0.332 | 3.29e-70 |
| `left_hip_angle` | 57.257 | 69.832 | 0.599 | 0.263 | 7.50e-44 |
| `right_knee_angle` | 69.667 | 77.640 | 0.431 | 0.183 | 1.94e-21 |
| `left_knee_angle` | 71.863 | 76.936 | 0.277 | 0.162 | 9.78e-17 |
| `right_heel_foot_vertical_delta` | 0.026 | 0.023 | -0.157 | 0.145 | 1.24e-13 |

The complete overall and class-conditional results are stored in the drift CSV. Statistical significance is descriptive because images may not be participant-independent.

## Visual Review Protocol

The manifest selects the highest-confidence errors within every observed confusion pair. Reviewers should record framing, viewpoint, occlusion, source-label ambiguity, pose-landmark plausibility, and whether static geometry supports the source label. The sample must not be used to tune against the test set.

Manual observations for the generated contact sheet are recorded in `zenodo_posture_visual_review.md` and kept separate from this reproducible statistical report.

## Decision

Promotion remains unsupported. Distribution shift, source-label ambiguity, and participant identity must be resolved using development data or a new participant-grouped dataset; the source test set remains audit-only.
