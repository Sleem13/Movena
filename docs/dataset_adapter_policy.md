# Dataset Adapter Policy

Every source receives a named adapter that audits files, lists samples without expensive loading, preserves raw labels, maps exercises only with evidence, normalizes unified metadata, validates samples, and declares pipeline compatibility. Missing or uncertain fields stay null/unknown and set manual review.

Adapters do not make a dataset training-ready. Review must cover license, provenance, modality, coordinate system, labels, participants, augmentation, leakage-safe splits, quality, and intended exercise.

Sprint 15 provides named adapters for every registered source. Where exact parsing or codebooks are unresolved, adapters export only safe metadata and set `processing_status=needs_manual_mapping`, `label_quality=low`, and `requires_manual_review=true`. Missing sources return zero samples rather than failing the complete export. Container formats are not deserialized during audits, and unknown codes are never converted into exercise or clinical issue labels without approval.

Adapter validation may report technical health while label review is still pending. Technical adapter health, research training readiness, model promotion, and application readiness are four separate decisions.
