# Report Generation Design

When `generate_report=true`, a successful squat analysis generates a ReportLab PDF in `backend/tmp/artifacts` (relative to the backend process working directory). The API exposes only an opaque UUID and `/api/v1/artifacts/reports/{report_id}`; callers cannot supply filesystem paths.

The report contains blank patient/session fields, UTC generation time, exercise, repetitions, movement score, average knee/hip/trunk angles, detected observations, feedback, limitations, and the medical disclaimer. It deliberately does not claim diagnosis, injury, pathology, treatment prescription, or clinical validation.

Artifacts expire after one hour by default. Expired files are removed opportunistically whenever artifacts are created or resolved. Source uploads are deleted immediately after analysis regardless of success. If report or overlay generation fails, partial artifacts from that request are deleted and the client receives the standard `PROCESSING_ERROR` envelope without internal paths.

This local filesystem design is intentionally simple. It does not provide durable records, user ownership, encryption-at-rest management, audit history, distributed storage, or access-controlled clinical documents. Those require an explicitly designed authenticated deployment and are outside Sprint 4.
