# Training Readiness Report

The training-readiness report groups samples by exercise and modality and checks reviewed labels, sample volume, participant identity, and participant-grouped train/validation/holdout assignments. Classic ML, sequence DL, and sensor-model flags remain false when any required governance gate is absent.

`ready_for_exploration` means only that a small, bounded research experiment may be considered. It does not mean the model can be integrated, promoted, clinically interpreted, or used to replace rule-based analysis.

Common blockers include unknown/unreviewed labels, insufficient reviewed samples, unresolved modality, missing participant identifiers, and missing participant-grouped splits. Generate the report with `python scripts/build_training_readiness_report.py`.

