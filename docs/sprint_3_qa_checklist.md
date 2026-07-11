# Sprint 3 QA Checklist

## Dataset Coverage

- [x] Metadata reviewed and class counts documented.
- [x] Imbalance and missing fast/uncontrolled coverage flagged.
- [x] Filename/folder conflict resolved.
- [x] Unlabeled clip quarantined from official validation.
- [x] Curated rule-validation split created.
- [x] Minimum additional collection targets documented.
- [ ] Physiotherapist independently confirms every class label.

## Thresholds and Safety

- [x] Threshold constants centralized.
- [x] Rep transitions, score penalties, confidence, and movement proxies documented.
- [x] Score clamped and tested from 0–100.
- [x] Poor depth, trunk lean, and good-squat behavior tested.
- [x] Feedback avoids diagnosis and includes an educational/clinical disclaimer.
- [ ] Physiotherapist signs off threshold values and whether the composite score should remain patient-facing.

## Backend and Uploads

- [x] Extension and MIME validation.
- [x] 100 MB streaming size limit.
- [x] Generated temporary filename and cleanup on success/failure.
- [x] Missing, empty, unsupported, oversized, broken, and no-pose errors tested.
- [x] Extremely short video rejected after decode.
- [x] Low confidence returned as a cautious issue rather than a crash.
- [x] Clean error JSON without stack traces.
- [x] Real Sprint 2 fixture still succeeds.

## Frontend

- [x] Vitest, React Testing Library, and jsdom configured.
- [x] Upload page and disabled submit tested.
- [x] Video selection and loading state tested.
- [x] API error envelope displayed.
- [x] Reps, score, issues, feedback, and disclaimer tested.
- [x] Production build passes.

## Documentation

- [x] Dataset audit and split documented.
- [x] Threshold rationale and limitations documented.
- [x] API request, success, error, field, and limitation contract documented.
- [x] Sprint plan and QA checklist created.
- [x] README commands and Sprint 3 focus updated.
- [x] No model training, new exercise, authentication, database, or redesign added.
