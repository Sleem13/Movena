# External Beta Known Limitations

This is an invite-only beta candidate, not a public release or clinical service.

Movena currently supports only bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Choosing the wrong exercise or submitting another movement can produce rejection or irrelevant output.

- Camera view and framing strongly affect results. Side/front requirements differ by exercise and observed pattern.
- Pose estimation may miss or misplace landmarks. Low light, loose clothing, occlusion, cropped joints, background clutter, rapid motion, and camera movement reduce reliability.
- A `rejected` result means the recording, landmark visibility, movement, or repetition evidence was insufficient. It is not a diagnosis or evidence that the person cannot perform the exercise.
- Movement scores and angle summaries are engineering outputs, not clinical scores, impairment measures, or treatment recommendations.
- Confidence describes analysis/input reliability; it does not express diagnostic certainty.
- Rule-based analyzers remain primary. ML/DL outputs, where present, are experimental, not clinically validated, and must not override validity or safety gates. Exercise recognition is an optional suggestion, not the primary selector.
- Overlays/reports are temporary and can expire. Browser/codec, network, or artifact-link issues may prevent preview/download.
- Results depend on the processed frames and do not account for pain, history, load, fatigue, pathology, or the broader clinical context.
- The beta requires network access and a private backend; downtime, upload interruption, auth expiry, and device differences can affect testing.
- It is not for emergency use, injury diagnosis, treatment prescription, medical decision-making, or replacing assessment by a licensed physiotherapist.

Stop for pain, dizziness, numbness, instability, unusual discomfort, chest discomfort, unusual shortness of breath, or another concerning symptom and seek appropriate professional or urgent care.
