# Dataset Adapter Policy

Every source receives a named adapter that audits files, lists samples without expensive loading, preserves raw labels, maps exercises only with evidence, normalizes unified metadata, validates samples, and declares pipeline compatibility. Missing or uncertain fields stay null/unknown and set manual review.

Adapters do not make a dataset training-ready. Review must cover license, provenance, modality, coordinate system, labels, participants, augmentation, leakage-safe splits, quality, and intended exercise. Complex KIMORE, UI-PRMD, UCI, DynTherapy, Rehab24-6, and physical-therapy collections remain adapter/manual-mapping work for Sprint 15.
