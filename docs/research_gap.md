# Research Gap

## Core Gap

Recent literature shows rapid progress in AI-assisted rehabilitation, markerless motion capture, pose estimation, and remote monitoring. However, there remains a practical gap between technical feasibility and clinically useful physiotherapy tools. Many systems can estimate pose landmarks or classify movements, but fewer systems provide therapist-centered, interpretable, single-camera assessment of common lower-limb rehabilitation exercises in home or outpatient settings.

Movena addresses this gap by focusing on a constrained MVP for knee rehabilitation and lower-limb exercise assessment. The system is intended to support physiotherapists by generating movement metrics, compensation flags, progress summaries, and therapist-friendly reports. It does not replace clinical judgment, diagnose pathology, or prescribe treatment independently.

## Specific Gaps in Current Systems

### 1. Limited Lower-Limb Rehabilitation Specificity

Many pose-estimation systems are designed for general human movement, sports, fitness, gait, or broad activity recognition. Fewer are optimized for therapeutic lower-limb exercises such as bodyweight squats, lunges, straight leg raises, glute bridges, step-ups, and single-leg balance. These movements require exercise-specific logic because the relevant compensations differ across tasks.

### 2. Lack of Therapist-Friendly Interpretation

Technical systems often report model accuracy, classification labels, or raw kinematics. Physiotherapists need clinically readable information: what movement pattern was observed, how confident the system was, how performance changed over time, and whether the observation should be reviewed during treatment planning.

### 3. Single-Camera Home-Use Challenges

Single-camera systems are accessible but technically constrained. They are sensitive to lighting, camera angle, body orientation, occlusion, clothing, room size, and out-of-plane movement. Many studies are conducted under controlled conditions, which limits direct translation to home exercise monitoring.

### 4. Limited Clinical Validation of Automated Scores

Automated movement-quality scores may correlate with expert ratings in selected datasets, but broad clinical validity is still developing. For safe use, scores should be conservative, transparent, and reviewed by clinicians. A single numerical score should not be treated as a diagnosis or a complete measure of rehabilitation quality.

### 5. Weak Integration With Progress Tracking and Reporting

Remote rehabilitation tools often emphasize exercise delivery or real-time feedback but may underemphasize longitudinal reporting. Physiotherapists need session-to-session trends, adherence patterns, range-of-motion changes, and flagged compensations in a format that can support documentation and follow-up.

## How Movena Addresses the Gap

Movena addresses the research gap through a clinically scoped MVP:

- It focuses on knee rehabilitation and lower-limb exercises rather than broad general fitness.
- It uses markerless camera-based pose estimation to improve accessibility.
- It translates pose landmarks into interpretable metrics such as joint angles, repetition timing, symmetry, and stability.
- It flags possible compensations using conservative language and confidence indicators.
- It generates therapist-friendly reports for review, documentation, and progress monitoring.
- It clearly states that AI output supports physiotherapists and does not replace clinical judgment.

## Project Justification

The project is justified because home exercise performance is difficult to observe between clinic visits, while recent pose-estimation models make low-cost visual movement tracking technically feasible. A focused platform can help bridge this gap by giving physiotherapists structured information about exercise performance outside the clinic. The MVP's value lies in supporting measurement consistency, adherence monitoring, and clearer patient-therapist communication.

The knee rehabilitation focus is appropriate because lower-limb movement patterns are visually observable and clinically meaningful, yet current accessible tools often lack exercise-specific assessment and therapist-facing reporting. The implemented MVP starts with bodyweight squat only; the six-exercise set is a later research roadmap after the squat workflow is validated.

## Research Question

How can a single-camera AI system support physiotherapists in assessing lower-limb rehabilitation exercises by providing interpretable pose-derived metrics, conservative movement-quality indicators, and progress reports without replacing clinical judgment?

## MVP Design Implications

The research gap leads to the following product requirements. Only the squat-specific subset is implemented in the current MVP:

- Exercise-specific assessment profiles for squat, lunge, straight leg raise, glute bridge, step-up, and single-leg balance.
- Pose-landmark quality checks before scoring.
- Camera-position guidance for full-body or lower-body visibility.
- Transparent calculations for joint angles and repetition segmentation.
- Conservative compensation flags rather than diagnostic conclusions.
- Progress tracking across sessions.
- Therapist-facing report export with metrics, observations, and confidence notes.

## Final Gap Statement

There is a need for an accessible, clinically cautious, therapist-centered computer vision platform that analyzes common lower-limb rehabilitation exercises using ordinary cameras and converts pose data into interpretable movement-quality feedback and progress reports. Movena is designed to fill this gap by functioning as a physiotherapist support tool for knee rehabilitation assessment, not as a replacement for professional clinical evaluation.
