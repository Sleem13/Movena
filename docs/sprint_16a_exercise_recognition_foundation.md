# Sprint 16A — Exercise Recognition Model Foundation

Sprint 16A introduces a suggestion-only recognition research layer without changing explicit squat or sit-to-stand analysis.

## Components

- A modality-separated recognition sample index with explicit exclusion reasons.
- Lightweight feature reuse that never reprocesses all raw videos by default.
- Logistic regression, random forest, and SVC baseline training with dry-run gates.
- Optional model loading and inference that is safe when artifacts are absent.
- Experimental feature-payload API endpoints for model discovery and suggestions.
- Confirmation-first future routing and model-card policies.

```powershell
python scripts/build_exercise_recognition_dataset.py --dry-run
python scripts/build_exercise_recognition_dataset.py
python scripts/build_exercise_recognition_features.py --dry-run
python scripts/build_exercise_recognition_features.py
python scripts/train_exercise_recognition_baseline.py --dry-run --track video_pose_recognition --model random_forest
python -m pytest
```

Current reviewed features contain only bodyweight squat, so baseline training must refuse until another reviewed class and participant-grouped split exist. No model is trained or promoted by the required workflow. The frontend retains explicit exercise selection; a suggestion UI is deferred until an evaluated model and upload-to-feature path exist.

