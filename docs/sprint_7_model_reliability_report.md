# Sprint 7 Model Reliability Report

## Decision

**Keep ML optional and disabled by default.** The rule-based analyzer remains primary. Candidate v2 is not an evidence-based improvement despite using seven additional real videos, because the protected three-video holdout and its class gaps are unchanged.

## Dataset

- Sprint 5 rows: 16 real videos.
- Sprint 7 v2 rows: 23 real videos.
- Augmented feature rows: 0.
- Manual rep counts validated: 0 of 23 real training rows.
- Protected holdout: 3 real videos.
- Missing holdout class: knee valgus; fast/uncontrolled is absent everywhere.

## Comparison

| Metric | Sprint 5 | Sprint 7 v2 | Delta |
|---|---:|---:|---:|
| Accuracy | 0.667 | 1.000 | +0.333 |
| Macro F1 | 0.556 | 1.000 | +0.444 |
| Weighted F1 | 0.556 | 1.000 | +0.444 |

Both experiments use `svc_rbf`; v2 pre-registers that candidate family instead of selecting a model on the protected holdout. V2 classified all three protected clips correctly. Probability values are not calibrated clinical confidence and must not be interpreted as a safety score.

The comparison uses `models/squat_baseline/sprint_5_reference_metrics.json`, an immutable 16-video Sprint 5 snapshot. The general `models/squat_baseline/metrics.json` path had previously been regenerated after data expansion and is therefore not accepted as historical comparison evidence. V2 evaluation uses real holdout rows only; correlated augmented variants are excluded.

## Reliability Interpretation

Perfect metrics on three holdout clips do not demonstrate stable performance or generalization. They show only that these three examples were classified correctly in this run. The holdout is too small for stratification, useful uncertainty bounds, participant-level analysis, or meaningful class conclusions. Knee-valgus is absent from the holdout and fast/uncontrolled is absent from the complete labeled dataset. Repeated comparison against this holdout also risks informal overfitting.

Before reconsidering default enablement, meet real-video coverage targets, establish participant-grouped splits with every class represented, freeze a sufficiently sized holdout, assess real-only metrics, review labels with physiotherapists, and calibrate confidence. No clinical-performance claim is supported.

Manual rep-count validation also remains pending. It evaluates the deterministic rep counter, not the squat-quality classifier, and must be reported separately from classification accuracy.
