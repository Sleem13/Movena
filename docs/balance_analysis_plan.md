# Static Balance Analysis Plan

Status: Very important implementation task, first MVP pass complete in backend and frontend.

## Scope

Movena now supports a conservative `balance` analyzer for short static standing balance videos. The first pass estimates:

- visible hold duration,
- stance mode proxy: quiet standing, narrow/tandem stance, or unilateral stance,
- normalized body-sway proxy from shoulder/hip center relative to foot support,
- sway path and sway velocity,
- trunk lean,
- pelvis tilt,
- stance knee-angle variability,
- possible foot adjustment.

This is an educational postural-steadiness screen. It does not infer fall risk, vestibular impairment, neurological status, sensory integration, center of pressure, true center of mass, or treatment suitability from monocular video.

## Biomechanics Basis

Laboratory balance assessment commonly uses force plates to quantify center-of-pressure movement during quiet standing. Marker or depth-camera systems can estimate body-center movement and sway-like features, but they are still proxies unless validated against force-plate, motion-capture, or clinical assessment data.

For the MVP, static balance is estimated from a 2D pose contract:

- body-center proxy: weighted shoulder/hip midpoint,
- support-base proxy: midpoint of visible heel/toe landmarks,
- sway proxy: body-center displacement relative to support-base, normalized by body height,
- control proxies: trunk lean, pelvis level, knee variability, and foot movement.

## Public Balance Data Sources Reviewed

- PhysioNet KINECAL: 90 participants, clinically relevant balance and mobility movements, Kinect skeleton/depth data, falls-history metadata, clinical labels, and postural-sway metrics.
- PhysioNet Body Sway When Standing and Listening to Music Modified to Reinforce Virtual Reality Environment Motion: force-plate center-of-pressure data from 28 young adults standing for 60-second trials under visual/music conditions.
- Published postural-sway literature describing force plates as the key quantitative balance assessment method and CoP/body sway as standard posturography measures.
- Public normative-sway literature using inertial or force-plate measures; useful for validation planning, not yet embedded as clinical thresholds.

## Implementation Notes

- API endpoint: `/api/v1/analyze/balance`.
- Analyzer ID: `balance`.
- Primary result payload: existing `AnalysisResponse` plus optional `balance_metrics`.
- Scoring is transparent and conservative: hold duration, sway control, trunk control, pelvis control, knee stability, and pose visibility.
- Frontend shows balance in supported exercise selection and displays balance-specific metric cards in results.

## Next Validation Steps

- Collect consented side/front balance videos with controlled quiet standing, tandem, and single-leg protocols.
- Add explicit test-condition metadata: eyes open/closed, shoes, support surface, stance type, assistive support used.
- Compare pose-derived sway proxies against force-plate CoP datasets before any fall-risk or clinical interpretation.
- Have licensed physiotherapists review thresholds and feedback language before pilot use.

