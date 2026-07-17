# Unified Sample Schema

`unified_sample_schema.json` defines common discovery metadata for video, image, 2D/3D skeleton, sensor time-series, and tabular samples. Modality-specific fields may be null. Unknown participant, view, label, or exercise values stay unknown; they are never inferred as clinical labels.

Weak or inferred label mappings set `requires_manual_review=true`. `processing_status` describes discovery/preparation and is not equivalent to training readiness. Adapters preserve dataset and source paths, raw and normalized labels, augmentation provenance, participant/session identity where supplied, and split assignment.
