# Sprint 17: Knee Extension Analyzer

Sprint 17 adds a manually selected, rule-based seated knee-extension analyzer without training or promoting an ML model. The existing squat and sit-to-stand analyzers remain unchanged and primary for their exercises.

## Delivered scope

- `POST /api/v1/analyze/knee-extension`
- flexed → extending → extended → returning rep state machine
- fail-closed pose visibility, movement-range, and complete-rep validity checks
- explainable movement scoring and non-diagnostic feedback
- optional frame data, PDF report, overlay, and session persistence through shared services
- frontend exercise selection, recording guidance, and knee-specific result labels
- conservative dataset-candidate export and an empty manual-annotation template

## Run

```powershell
python scripts/prepare_knee_extension_training_candidates.py
python -m pytest
cd frontend
npm test -- --run
npm run build
```

The engineering thresholds are configurable defaults, not clinically validated cutoffs. Manual exercise selection remains primary. No knee-extension recognition or biomechanics model is trained or available.

