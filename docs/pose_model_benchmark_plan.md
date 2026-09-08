# Pose Model Benchmark Plan

## Objective

Compare pretrained landmark detectors on the same custom squat videos while holding the downstream Movena angle calculations and rule-based interpretation constant. This is an offline engineering benchmark, not model training or clinical validation.

## Backends and controls

- Default/control: MediaPipe BlazePose, 33 landmarks.
- Candidates: MoveNet Lightning and MoveNet Thunder, 17 landmarks.
- Run each backend against the identical decoded videos on the same machine, power mode, Python environment, and CPU/GPU policy.
- Record backend/model version, model asset checksum, operating system, processor, thread settings, and command.
- Run one warm-up video before timed runs. Repeat timed runs at least three times and report median runtime when MoveNet is implemented.
- Stratify results by label and camera view. Do not aggregate side-view and front-view results without also reporting each stratum.

## Metrics

| Metric | Definition | Interpretation |
|---|---|---|
| Frames processed | Number of readable decoded frames presented to the backend | Denominator and decoding sanity check |
| Pose detection success rate | Frames containing a pose / readable frames | Higher is better |
| Missing landmark rate | Missing expected landmark slots / (readable frames x backend landmark count) | Lower is better; includes frames with no pose |
| Average landmark visibility/confidence | Mean backend confidence across emitted landmarks | Compare trends cautiously because scores are not calibrated across model families |
| Angle smoothness | Mean of knee, hip, and trunk mean absolute second differences in degrees | Lower suggests less frame-to-frame jitter; it is not anatomical accuracy |
| Knee angle stability | Mean absolute second difference of the bilateral-average knee angle | Lower is smoother |
| Hip angle stability | Mean absolute second difference of the midpoint-based hip angle | Lower is smoother |
| Trunk angle stability | Mean absolute second difference of trunk inclination | Lower is smoother |
| Processing FPS | Readable frames / wall-clock inference runtime | Higher is faster on the tested hardware |
| Runtime per video | Wall-clock seconds spent in backend extraction | Lower is faster |
| Issue-detection agreement | Jaccard agreement between candidate and current MediaPipe-backed rule issue sets | Measures downstream consistency, not correctness |

Angle smoothness must also be inspected by movement phase. A perfectly smooth but biased trace can score well, and real squat motion creates legitimate angle changes. For a stronger study, annotate stable standing and bottom holds and calculate jitter within those intervals separately.

## Dataset protocol

1. Use only consented custom squat videos and preserve the curated label metadata.
2. Verify label and camera view before benchmarking; labels are not landmark ground truth.
3. Include correct, shallow-depth, knee-valgus, trunk-lean, and fast/uncontrolled examples where available.
4. Record resolution, FPS, duration, view, occlusion, lighting, and whether the full body is visible.
5. Never tune issue thresholds on the final comparison subset.

## Output and review

Run from the repository root:

```powershell
$env:POSE_BACKEND = "mediapipe"
python scripts/benchmark_pose_backends.py
```

Optional selectors:

```powershell
python scripts/benchmark_pose_backends.py --backend mediapipe --limit 3
python scripts/benchmark_pose_backends.py --backend movenet_lightning
python scripts/benchmark_pose_backends.py --backend movenet_thunder
```

The script writes:

- `reports/pose_backend_benchmark/pose_backend_metrics.csv`
- `reports/pose_backend_benchmark/pose_backend_summary.md`

MoveNet currently exits with an actionable deferred-backend message; it does not install TensorFlow or download a model automatically.

## Decision gate

A candidate is eligible for a later integration proposal only if it is reproducible, meets the deployment latency budget, does not materially increase missing landmarks, improves or maintains phase-specific angle stability, and has acceptable per-label issue agreement. Any change to the production default requires separate API compatibility, privacy, safety, and physiotherapist-reviewed validation. No benchmark result should be described as clinical validation.
