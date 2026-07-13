# Pretrained Pose Model Strategy

## Scope and safety boundary

This sprint benchmarks pose-estimation backbones only. It does not replace the rule-based Squat Analyzer, train a deep model, or establish clinical validity.

Pose estimation localizes anatomical keypoints in an image. Biomechanics analysis turns those coordinates into angles, phases, repetition counts, quality rules, and feedback. A pretrained pose model therefore supplies measurements; it does not know whether a squat is safe, diagnose an injury, estimate tissue loading, or make a clinical decision. Those interpretations require separately validated definitions, camera protocols, reliability studies, and qualified clinical oversight.

## Candidate models

### MediaPipe Pose Landmarker / BlazePose

MediaPipe exposes 33 body landmarks, including heels and foot indices that are useful for lower-limb geometry. The Pose Landmarker result supports normalized image coordinates and world-coordinate landmarks. PhysioVision currently uses the compatible MediaPipe `solutions.pose` BlazePose pipeline and consumes shoulder, hip, knee, and ankle points. The benchmark adapter exposes all 33 points while leaving the production adapter unchanged. See Google's [33-landmark definition](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmark) and [PoseLandmarker result contract](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarkerResult).

### MoveNet Lightning

MoveNet Lightning is the latency-oriented single-person variant. It returns 17 COCO-style 2D keypoints with confidence scores and uses a 192 x 192 model input in Google's reference workflow. It is attractive for real-time and constrained-device experiments, but it omits heel and foot-index landmarks and provides no world-coordinate output. Google's reference describes Lightning as the faster, less accurate variant and reports real-time performance on many modern devices; PhysioVision must measure performance on its own CPU and videos rather than adopt that number as a guarantee. See the official [MoveNet tutorial](https://www.tensorflow.org/hub/tutorials/movenet).

### MoveNet Thunder

MoveNet Thunder uses the same 17-keypoint 2D output and a larger 256 x 256 reference input. Google positions it as the higher-accuracy, slower MoveNet variant. It is the more relevant MoveNet comparison when offline video quality matters more than minimum latency, but the reduced lower-foot landmark set remains a limitation for squat mechanics. See Google's [MoveNet overview and edge guidance](https://blog.tensorflow.org/2021/08/pose-estimation-and-classification-on-edge-devices-with-MoveNet-and-TensorFlow-Lite.html).

## Engineering comparison

| Model | Landmarks | 2D / 3D output | Relative speed | Expected landmark accuracy | Squat-analysis usefulness | Important limitations |
|---|---:|---|---|---|---|---|
| MediaPipe Pose Landmarker / BlazePose | 33 | Normalized 2D plus relative `z`; Pose Landmarker can also return world landmarks | Fast, designed for real-time use | Strong full-body baseline; must be measured on PhysioVision videos | Best MVP coverage for shoulders, hips, knees, ankles, heels, and feet | Monocular depth is estimated; sensitive to view, occlusion, lighting, motion blur, and subject framing |
| MoveNet Lightning | 17 | 2D coordinates and confidence | Fastest candidate; latency-oriented | Lower than Thunder by model design; dataset-specific result unknown | Useful for high-throughput 2D shoulder/hip/knee/ankle tracking | No world coordinates, heel, or foot-index landmarks; TensorFlow stack adds deployment weight |
| MoveNet Thunder | 17 | 2D coordinates and confidence | Slower than Lightning | Higher than Lightning by model design; dataset-specific result unknown | Useful higher-quality 17-point comparator for knee, hip, and trunk angles | Same reduced landmark set and 2D limitations; larger runtime cost |

“Expected accuracy” above is a relative engineering expectation, not a clinical accuracy claim. Public benchmark ranking does not establish angle validity, issue-detection validity, or reliability for the custom camera views and movement patterns in PhysioVision.

## Recommendation for PhysioVision AI

Keep MediaPipe Pose Landmarker / BlazePose as the default for now. Its 33 landmarks and lower-foot coverage support posture and angle analysis better than the 17-keypoint candidates for this MVP, and it already fits the CPU-oriented pipeline.

Benchmark MoveNet Lightning and Thunder only after adding a reviewed, optional TensorFlow Lite adapter and local model asset management. Promote a candidate only if the paired-video benchmark shows a meaningful gain in detection coverage, angle stability, runtime, or issue agreement without weakening the current data contract. Even then, retain the rule-based analyzer as the primary interpretation layer until separate clinical validation work is designed and completed.
