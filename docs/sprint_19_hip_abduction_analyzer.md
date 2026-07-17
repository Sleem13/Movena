# Sprint 19: Hip Abduction Analyzer

Sprint 19 adds a manually selected, rule-based standing hip-abduction analyzer. It does not train or promote ML/DL and does not change recognition routing.

Delivered scope includes `POST /api/v1/analyze/hip-abduction`, front-view moving-side selection, neutral–abducted–neutral repetition counting, fail-closed validity, explainable scoring, non-diagnostic feedback, shared report/overlay/session support, frontend selection and results, and conservative data-candidate preparation.

```powershell
python scripts/prepare_hip_abduction_training_candidates.py
python -m pytest
cd frontend
npm test -- --run
npm run build
```

Thresholds are adjustable engineering defaults, not clinically validated cutoffs. Manual exercise selection remains primary and hip-abduction ML is not available.
