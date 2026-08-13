# Walking Gait Analysis Plan

Status: Very important implementation task, first MVP pass complete in backend and frontend.

## Scope

PhysioVision AI now supports a conservative `walking_gait_screen` analyzer for short walking videos. The first pass estimates:

- step/contact count from visible foot trajectory,
- complete same-side gait cycles,
- cadence in steps per minute,
- stance/swing timing percentage,
- left-right temporal symmetry,
- stride-time variability,
- normalized side-view foot excursion as a non-calibrated stride proxy,
- average visible knee range during gait cycles.

This is an educational screen, not a clinical gait-lab replacement. The system does not infer diagnosis, ground reaction force, joint moments, true walking speed, true step length, center of pressure, or treatment suitability from monocular video.

## Biomechanics Basis

The gait cycle is defined from one initial contact of a foot to the next initial contact of the same foot. Normal-speed adult walking is commonly described as approximately 60% stance and 40% swing, with cadence representing steps per unit time and symmetry reflecting left-right temporal/spatial consistency.

For the MVP, stance/swing timing is estimated from side-view foot motion relative to the pelvis:

- initial contact proxy: local maximum forward foot position relative to pelvis,
- toe-off proxy: local minimum trailing foot position between same-side contacts,
- gait cycle: interval between two same-side initial-contact proxies.

## Public Gait Data Sources Reviewed

- AAPM&R PM&R KnowledgeNow, "Biomechanics of Normal Gait": gait-cycle definitions, stance/swing timing, cadence, stride length, step length, base of support, symmetry, and limitations of observational versus quantitative gait analysis.
- PhysioNet Gait in Aging and Disease Database: stride interval time series from young adults, older adults, and older adults with Parkinson's disease.
- PhysioNet Multimodal Gait Dataset: synchronized EEG, EMG, IMU kinematics, force plates, and center-of-pressure data from 59 healthy adults walking at controlled treadmill speeds.
- Mendeley Data overground walking dataset: raw kinetic and full-body kinematic data from 57 healthy adults walking overground.
- Nature Scientific Data open biomechanics dataset: raw marker trajectory data and metadata from 1,798 healthy and injured participants during treadmill walking and/or running.
- Georgia Tech EPIC Lab open-source lower-limb biomechanics dataset: kinematics, kinetics, power, IMU, EMG, and goniometer signals across treadmill, level-ground, ramp, and stair locomotion contexts.

## Implementation Notes

- API endpoint: `/api/v1/analyze/gait`.
- Analyzer ID: `walking_gait_screen`.
- Primary result payload: existing `AnalysisResponse` plus optional `gait_metrics`.
- Scoring is transparent and conservative: gait phase timing, cadence, temporal symmetry, stride consistency, visible knee range, and pose visibility.
- Frontend shows gait in supported exercise selection and displays a gait-specific metric row in results.

## Next Validation Steps

- Collect consented pilot walking videos with side-view and front-view protocols.
- Add a calibration option for known walkway distance to report real walking speed and step/stride length.
- Compare pose-derived contact timing with public force/pressure/IMU gait datasets before clinical claims.
- Add clinical-review thresholds by population only after validation with licensed physiotherapists.

