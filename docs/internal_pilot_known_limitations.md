# Internal Pilot Known Limitations

- Only five manually selected exercises are supported.
- Analysis requires network upload and backend availability; there is no on-device analysis.
- Single-camera MediaPipe estimates are affected by view, occlusion, lighting, clothing, distance, and frame quality.
- Scores and feedback are educational movement-monitoring outputs, not diagnosis, injury detection, or treatment prescription.
- Rule-based analyzers remain primary; ML/DL and exercise recognition remain experimental.
- Invalid/static/insufficient movement should be rejected, but validity and repetition logic are not clinically validated.
- Reports/overlays are temporary signed artifacts and may expire or disappear after deploy/restart.
- Staging local artifact storage and `init_db()` schema creation are not production-grade.
- iOS validation may remain unavailable without Apple hardware/signing access.
- No real patient data, clinical use, or public sharing is permitted.
