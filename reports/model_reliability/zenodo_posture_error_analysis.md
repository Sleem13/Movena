# Zenodo Static Posture Error Analysis

## Scope

This report evaluates the retained, uncalibrated logistic-regression candidate on the publisher's source-test split. A separate development-only temperature-scaling experiment was rejected after worsening untouched holdout probability quality. This is engineering evidence for static posture research, not clinical validation.

- Evaluated images: 956
- Correct predictions: 848
- Misclassifications: 108
- Error rate: 0.113
- Mean prediction confidence: 0.940
- Mean confidence on errors: 0.804

## Error Pairs

- `bad_back -> bad_heel`: 16
- `bad_back -> good`: 50
- `good -> bad_heel`: 42

## False Negatives by Actual Class

- `bad_back`: 66
- `good`: 42

## False Positives by Predicted Class

- `bad_heel`: 58
- `good`: 50

## All Predictions by Confidence Band

- `high_at_least_0_75`: 865
- `low_below_0_50`: 2
- `medium_0_50_to_0_75`: 89

## Errors by Confidence Band

- `high_at_least_0_75`: 71
- `low_below_0_50`: 1
- `medium_0_50_to_0_75`: 36

## Selective Performance by Confidence Threshold

| Threshold | Accepted | Coverage | Accuracy | Errors |
| --- | ---: | ---: | ---: | ---: |
| 0.50 | 954 | 0.998 | 0.888 | 107 |
| 0.75 | 865 | 0.905 | 0.918 | 71 |
| 0.90 | 782 | 0.818 | 0.948 | 41 |
| 0.95 | 713 | 0.746 | 0.965 | 25 |

## Confusion Matrix

```
predicted  bad_back  bad_heel  good
actual
bad_back        260        16    50
bad_heel          0       320     0
good              0        42   268
```

## Reliability Decision

Promotion is not supported. Participant identifiers are unavailable, so the source-test split is not proven participant-independent. Static images cannot validate repetitions, movement phases, tempo, or video-level movement quality.

The uncalibrated model also produces high-confidence mistakes. Confidence thresholds must not be treated as safety guarantees; calibration requires a development-only validation protocol and a separate untouched holdout.

The model remains offline and research-only; rule-based video analysis remains primary.
