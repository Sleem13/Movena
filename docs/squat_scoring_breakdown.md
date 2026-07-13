# Squat Scoring Breakdown

The educational `movement_score` is an explainable weighted combination rather than a list of fixed penalties:

| Component | Weight | Evidence |
| --- | ---: | --- |
| Depth | 30% | Smoothed minimum knee angle relative to the 115° prototype threshold |
| Knee alignment | 25% | Ratio of possible valgus frames, moderated by pose quality and camera view |
| Trunk control | 20% | Average trunk angle during movement frames relative to 35° |
| Consistency | 15% | Variation in per-rep minimum angles or available bottom frames |
| Pose confidence | 10% | Pose-quality score |

The weights and thresholds are reviewable prototype parameters, not clinically validated cut-offs. Side-view valgus evidence receives a smaller score penalty because 2D lateral video is unsuitable for strong frontal-plane conclusions. Low-quality tracking similarly moderates the alignment penalty. User-facing wording remains observational and tentative.

`score_breakdown` makes each component visible. `analysis_confidence` must be consulted separately: a high movement score with low confidence means the recording should be reviewed or repeated, not that movement has been clinically cleared.
