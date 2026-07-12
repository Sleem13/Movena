# Sprint 7 Model Reliability Report

## Decision

**Keep ML optional and disabled by default.** The rule-based analyzer remains primary. Candidate v2 is not an evidence-based improvement despite using seven additional real videos, because the protected three-video holdout and its class gaps are unchanged.

## Dataset

- Sprint 5 rows: 16 real videos.
- Sprint 7 v2 rows: 23 real videos.
- Augmented feature rows: 0.
- Protected holdout: 3 real videos.
- Missing holdout class: knee valgus; fast/uncontrolled is absent everywhere.

## Comparison

| Metric | Sprint 5 | Sprint 7 v2 | Delta |
|---|---:|---:|---:|
| Accuracy | 0.667 | 0.667 | 0.000 |
| Macro F1 | 0.556 | 0.556 | 0.000 |
| Weighted F1 | 0.556 | 0.556 | 0.000 |

Both experiments selected `svc_rbf`. V2’s confidence for the protected correct fixture was approximately 0.459, compared with approximately 0.556 for Sprint 5. Probability values are not calibrated clinical confidence and should not be compared as a safety score.

## Reliability Interpretation

Unchanged metrics on three holdout clips do not demonstrate stable performance or lack of improvement. They show only that the same two of three examples were classified correctly. The holdout is too small for stratification, uncertainty bounds, participant-level analysis, or meaningful class conclusions. Repeated comparison against this holdout also risks informal overfitting.

Before reconsidering default enablement, meet real-video coverage targets, establish participant-grouped splits with every class represented, freeze a sufficiently sized holdout, assess real-only metrics, review labels with physiotherapists, and calibrate confidence. No clinical-performance claim is supported.
