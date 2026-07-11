# Squat Rule Thresholds

The source of truth is `backend/app/core/exercise_thresholds.py`. These values are engineering heuristics for an educational prototype, not diagnostic cutoffs.

| Rule | Current value | Use | Rationale and limitation |
|---|---:|---|---|
| Standing knee angle | >160° | Completes a rep after depth | Approximates near-extension in 2D; camera perspective changes the estimate |
| Squat depth knee angle | <110° | Enters depth phase | Permissive prototype depth proxy; acceptable depth depends on goals, anatomy, mobility, and symptoms |
| Poor-depth ratio | <25% depth frames among squat frames | Flags `poor_depth` | Reduces one-frame decisions but is clip-duration and tracking dependent |
| Trunk lean | mean >35° from vertical | Flags `excessive_trunk_lean` | 2D view-dependent; forward lean can be normal for anatomy and squat style |
| Knee valgus margin | 0.035 normalized image width | Frame-level frontal-plane proxy | Not a joint-load measure and unreliable from side views or rotated cameras |
| Knee-valgus frame ratio | >25% | Flags `possible_knee_valgus` | Requires persistence, but remains a camera-sensitive proxy |
| Inconsistent depth | depth-angle SD >18° | Flags inconsistency | Short clips and mixed rep intent can inflate variability |
| Landmark visibility | frame mean <0.45 | Marks a low-confidence frame | MediaPipe visibility is model confidence, not clinical measurement quality |
| Low-confidence ratio | >40% | Adds confidence issue | Keeps partial clips usable while warning users |

Rep counting is a two-state transition: start `standing`, enter `depth` below 110°, and count only after returning above 160°. There is no time-based debounce, calibration, or person-specific range adjustment.

Score deductions are 20 points each for poor depth, excessive trunk lean, and possible knee valgus; 10 each for inconsistent movement and low landmark confidence. The final score is clamped to 0–100. The score is a product feedback indicator, not a clinical outcome score.

## Physiotherapist Review Required

- Confirm whether 110° is appropriate for the intended patient population and exercise instruction.
- Review trunk lean by camera view, limb/torso proportions, load, mobility, and permitted squat strategy.
- Determine whether the valgus proxy should be disabled unless a validated frontal view is known.
- Review every penalty and whether a single composite score should be shown at all.
- Define pain, balance, post-operative, and clinician-prescribed range exceptions before broader use.

## Safe Patient Wording

Use “possible movement issue detected” and “consider reviewing this with a licensed physiotherapist.” Never state that the system diagnosed injury, pathology, or a medical condition. Every report must say that the analysis is educational and does not replace clinical assessment.
