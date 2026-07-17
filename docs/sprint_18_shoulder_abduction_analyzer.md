# Sprint 18: Shoulder Abduction Analyzer

Sprint 18 adds a manually selected, rule-based shoulder-abduction analyzer. It does not train or promote ML/DL and does not change recognition routing.

Delivered scope includes `POST /api/v1/analyze/shoulder-abduction`, front-view side selection, lowered–raised–lowered repetition counting, fail-closed validity, explainable scoring, non-diagnostic feedback, shared report/overlay/session support, frontend selection and results, and conservative data-candidate preparation.

```powershell
python scripts/prepare_shoulder_abduction_training_candidates.py
python -m pytest
cd frontend
npm test -- --run
npm run build
```

Thresholds are adjustable engineering defaults, not clinically validated cutoffs. Manual selection remains primary and shoulder-abduction ML is not available.
