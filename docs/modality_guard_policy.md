# Modality Guard Policy

The modality guard prevents files from entering incompatible processing paths:

- The video pipeline accepts MP4, AVI, MOV, MKV, and WebM video only.
- MediaPipe pose entry points may accept supported video or image inputs.
- Sensor time series require a future sensor pipeline and adapter.
- Skeleton arrays or serialized joint data require a future skeleton adapter.
- Mixed, missing, and unknown modalities are audit-only until explicitly resolved.

CSV is not automatically considered video, sensor, or skeleton data because extension alone cannot establish its semantics. Dataset adapters must declare a reviewed modality before routing ambiguous tabular files.

The guard fails closed with an explicit incompatibility error. It does not alter the current API or rule-based squat analyzer.

