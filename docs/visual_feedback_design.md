# Visual Feedback Design

## Overlay

The overlay reuses the pose frames already extracted for analysis. OpenCV draws shoulder, hip, knee, and ankle markers plus shoulder/torso/pelvis/leg connections. Knee markers use a distinct color. When metrics exist for a frame, the video shows phase, mean knee angle, and at most one conservative warning prioritized as low confidence, possible valgus, then trunk lean.

Frames without a detected pose remain in the output video but are not annotated. This keeps audio-free video timing and avoids interpolating landmarks that MediaPipe did not observe. The output uses the CPU-friendly `mp4v` codec and is marked experimental because browser decoding support and landmark stability vary.

## Frame Detail

`include_frame_data=true` returns detected-pose frames containing frame index, seconds, mean knee angle, hip angle, trunk angle, phase, and an optional issue. Responses are capped at 300 evenly sampled rows. The default response omits this list to control payload size.

Phase is a transparent heuristic: knee angle below the depth threshold is `depth`, above the standing threshold is `standing`, and the intermediate region is labeled `descent` or `ascent` based on the preceding state. It is not a validated gait or rehabilitation phase classifier.

## Frontend Communication

Before upload, users see camera guidance for side/front views, full-body visibility, stability, lighting, and 3–5 comfortable repetitions. Results retain the summary cards and add PDF download, optional annotated preview, experimental-overlay note, and a dedicated educational-use warning. Wording describes possible observations and directs users toward licensed physiotherapist review.
