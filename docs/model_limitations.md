# Model Limitations

- Only 16 labeled custom videos are available: 9 correct, 4 trunk lean, 2 shallow depth, and 1 knee valgus.
- The protected holdout has three videos and no knee-valgus example.
- Stratified cross-validation is impossible with singleton development classes.
- Videos may share participant, session, device, or environment characteristics; independence is not established.
- Labels originate from operational folders and are not fully independently adjudicated by physiotherapists.
- Aggregate features discard temporal ordering, rep boundaries, movement speed detail, and within-session trajectories.
- Camera view, tilt, distance, lighting, occlusion, clothing, and MediaPipe errors affect angles.
- The posture classes are not diagnoses, injuries, pathologies, or treatment recommendations.
- Confidence is model probability output, not calibrated clinical confidence.
- Holdout metrics from three examples are smoke-test evidence only and must not be advertised as accuracy.
- The rule-based analyzer remains the primary MVP behavior; ML inference is offline and experimental.

The model is not clinically validated, not diagnostic, and must not be used to make independent patient-care decisions.
