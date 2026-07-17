# Sprint 15 — Exercise-Specific Dataset Adapters

Sprint 15 converts the Sprint 14 discovery architecture into named, fail-closed adapters for every registered source. Each adapter identifies files and modalities, preserves source codes, exports unified metadata, and declares compatible research pipelines. It does not blindly merge datasets, approve an exercise label, activate an analyzer, or promote a model.

## Deliverables

- Specific adapters for custom videos, Squat Kaggle, Zenodo squat images, KIMORE, UI-PRMD, UCI Physical Therapy Exercises, DynTherapy, Rehab24-6, Physical-therapy exercises, and missing/incomplete UCO Physical Rehab.
- Adapter validation, unified metadata export, exercise coverage, training-readiness, and label-mapping review outputs.
- Debug limits that avoid loading large datasets during development and tests.
- Fail-closed handling for unknown labels, unresolved modalities, and missing datasets.

## Commands

```powershell
python scripts/audit_raw_datasets.py
python scripts/build_dataset_registry.py
python scripts/create_exercise_label_mapping.py
python scripts/validate_dataset_adapters.py
python scripts/export_unified_dataset_metadata.py
python scripts/build_exercise_coverage_matrix.py
python scripts/build_training_readiness_report.py
python -m pytest
```

Only bodyweight squat and sit-to-stand are app-supported. Training readiness is research metadata, not app readiness or clinical validation. Rule-based analysis remains primary and no model is promoted by these workflows.

