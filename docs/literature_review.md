# Literature Review

## 1. Introduction

Movena is an AI-powered physical therapy and rehabilitation platform focused on computer vision-based assessment of therapeutic exercise. The current MVP implements bodyweight squat analysis only. A later research roadmap covers six common activities: bodyweight squat, lunge, straight leg raise, glute bridge, step-up, and single-leg balance. These exercises are clinically relevant because they involve lower-limb strength, control, balance, hip-knee-ankle coordination, and observable compensations such as dynamic knee valgus, asymmetrical loading, trunk lean, limited range of motion, and unstable single-limb control.

The recent literature from 2023 to 2026 shows increasing interest in artificial intelligence, markerless motion capture, and human pose estimation for rehabilitation measurement. The central promise is not to replace physiotherapists, but to improve access to objective movement data, support remote monitoring, reduce manual documentation burden, and provide consistent feedback between clinical visits. In this context, Movena should be positioned as a clinical decision-support and progress-tracking tool. It should not be described as a diagnostic system, a substitute for clinical judgment, or a standalone treatment authority.

## 2. AI in Physical Rehabilitation

AI in rehabilitation has expanded from robotics and sensor-based monitoring toward multimodal platforms that combine movement capture, machine learning, patient engagement, and clinician-facing analytics. Recent digital musculoskeletal care studies and reviews emphasize that AI can help scale monitoring and personalize rehabilitation workflows when clinicians remain responsible for interpretation and care planning. For example, AI-assisted digital care models for chronic musculoskeletal conditions have been proposed as a way to support higher-volume care delivery, but their safety depends on escalation pathways, human review, and appropriate clinical governance.

From a rehabilitation science perspective, AI is most useful when it transforms raw movement data into clinically interpretable variables. These include repetition counts, range of motion estimates, phase timing, movement smoothness, asymmetry, stability, and deviation from a therapist-defined target pattern. Current research also shows growing use of graph neural networks, temporal attention, contrastive learning, and pose-sequence models for exercise quality assessment. These methods are attractive because rehabilitation exercises are inherently temporal: the quality of a squat or lunge depends not only on isolated joint positions, but also on movement sequence, control, speed, and consistency.

However, AI rehabilitation systems face important limitations. Many models are trained on small datasets, healthy participants, controlled camera conditions, or a narrow range of exercises. Clinical populations may move more slowly, use compensatory strategies, require assistive devices, or present with pain-limited motion. For Movena, this means that the MVP should avoid unsafe clinical claims and instead focus on transparent measurement support: pose tracking, rule-based or model-assisted movement quality indicators, confidence flags, and therapist-readable reports.

## 3. Computer Vision and Markerless Motion Capture

Markerless motion capture uses ordinary video to estimate body landmarks without reflective markers, suits, or dedicated laboratory systems. Recent surveys describe markerless human pose estimation as promising for biomedical use because it is portable, lower cost, and more feasible outside specialist motion laboratories. Avogaro et al. (2023) highlight applications in rehabilitation, posture, gait, and motor assessment, while also emphasizing that biomedical use remains under active investigation.

In clinical biomechanics, 2023-2025 work has moved beyond simple landmark detection toward full pipelines that include keypoint selection, trajectory smoothing, inverse kinematics, biomechanical constraints, and validation against optical motion capture or clinical reference systems. Cotton et al. (2023) argue that accurate markerless biomechanics requires careful choices across the pipeline, including modern keypoint detectors, dense biomechanically meaningful landmarks, anatomical constraints, and regularization. Unger et al. (2024) further demonstrate that markerless motion capture can approach optical motion capture for selected upper-limb rehabilitation kinematics when multi-camera capture and biomechanical modeling are used.

These findings are highly relevant to Movena. The MVP can reasonably begin with 2D or lightweight 3D pose estimation from a webcam or smartphone camera, but its documentation should acknowledge that full biomechanical equivalence to marker-based systems is not assumed. A practical rehabilitation product should therefore expose measurement confidence, camera-position guidance, and therapist review rather than hiding uncertainty behind a single score.

## 4. Human Pose Estimation for Exercise Assessment

Human pose estimation models detect body landmarks such as shoulders, hips, knees, ankles, and feet. Modern models include lightweight real-time approaches for consumer devices and larger transformer-based or multi-person systems for higher accuracy. RTMPose (Jiang et al., 2023) is an example of recent work emphasizing real-time deployment and efficient multi-person pose estimation. Biomedical and exercise-assessment studies often combine these pose landmarks with temporal models such as spatial-temporal graph convolutional networks because the skeleton can be represented naturally as joints connected over time.

For rehabilitation exercise assessment, pose estimation supports several MVP-level tasks:

- Detecting whether the user is visible and appropriately framed.
- Estimating hip, knee, and ankle positions during lower-limb exercises.
- Segmenting repetitions into start, descent, bottom, ascent, and end phases.
- Estimating simple joint angles and symmetry indicators.
- Identifying observable compensations that require therapist review.
- Generating structured summaries for clinical documentation.

Recent rehabilitation exercise quality assessment research uses public datasets such as KIMORE, UI-PRMD, and IRDS, often relying on skeleton sequences rather than raw video. Karlov et al. (2024) propose supervised contrastive learning for rehabilitation exercise quality assessment, addressing the challenge that many datasets contain limited samples per exercise type. Sherif and Hamdi (2025) propose error-guided pose augmentation to simulate clinically relevant movement errors and improve automated assessment. These studies support the idea that movement-quality scoring can improve when models learn clinically meaningful error patterns rather than only classifying exercise labels.

For Movena, this suggests a staged approach. The current MVP starts with interpretable pose-derived metrics and rule-based quality indicators for squat; the other five selected exercises remain roadmap items. Later versions can add supervised learning only after validated datasets and therapist-labeled examples become available.

## 5. Joint Angle Analysis and Movement Quality Scoring

Joint angle calculation is one of the most direct ways to translate pose landmarks into rehabilitation-relevant measurements. For 2D video, knee angle can be estimated from hip-knee-ankle landmark vectors, hip angle from shoulder-hip-knee vectors, and trunk lean from shoulder-hip alignment relative to the vertical image axis. These calculations are computationally simple and transparent, but they are sensitive to camera angle, depth motion, occlusion, clothing, lighting, body habitus, and landmark jitter.

The literature supports caution in interpreting joint angles from single-camera systems. Two-dimensional angles may not capture transverse-plane movement such as femoral internal rotation or dynamic knee valgus with full biomechanical accuracy. Multi-camera or RGB-D systems can improve spatial information, but at the cost of equipment complexity. Marusic et al. (2024) compare RGB-D data with pose estimates from RGB video for low back pain rehabilitation exercise assessment, illustrating the trade-off between clinical measurement richness and accessible deployment.

Movement quality scoring should therefore combine multiple evidence-informed indicators rather than relying on a single angle threshold. For knee rehabilitation exercises, Movena can use:

- Range of motion indicators, such as estimated knee flexion depth during squats and lunges.
- Alignment indicators, such as knee tracking relative to hip and ankle landmarks.
- Symmetry indicators, such as left-right timing, depth, and loading proxies.
- Stability indicators, such as landmark variability during single-leg balance.
- Tempo indicators, such as controlled descent and ascent duration.
- Confidence indicators, such as landmark visibility and camera-position quality.

Scores should be presented as decision-support summaries: for example, "possible reduced knee flexion depth" or "possible frontal-plane knee control issue detected." The system should avoid diagnostic wording such as "pathological movement" unless validated and reviewed by a qualified clinician.

## 6. Remote Physiotherapy and Home-Based Monitoring

Remote physiotherapy has become more prominent due to telehealth adoption, patient convenience, and the need for monitoring outside the clinic. Recent telehealth reviews suggest that allied health interventions can be delivered through remote modalities for selected use cases, but technology access, patient suitability, safety monitoring, and clinician oversight remain important. For rehabilitation, remote monitoring is particularly attractive because exercise adherence and technique quality are difficult to observe between visits.

Smartphone and webcam systems are especially relevant because they can be deployed without specialized equipment. The 2025 smartphone markerless motion-capture exergame literature highlights the same trade-offs that Movena must manage: real-time responsiveness, camera setup, accuracy, usability, and feedback design. Smartphone gait-analysis studies also show growing interest in mobile measurement for rehabilitation populations, although gait analysis differs from visual exercise scoring and cannot be directly generalized to all therapeutic exercises.

Home-based monitoring introduces uncontrolled variables. Patients may perform exercises in small rooms, with poor lighting, partial occlusion, camera tilt, or non-standard camera distance. For this reason, the MVP should include camera-position guidance, real-time visibility checks, and conservative feedback. A therapist-friendly report should distinguish between observed movement patterns and system confidence, making it clear when data quality is insufficient.

## 7. Current Limitations

The current literature reveals several limitations in AI-based exercise assessment and markerless motion capture:

- Many datasets are small, diagnosis-specific, or collected in controlled environments.
- Healthy-participant performance may not generalize to rehabilitation populations.
- Single-camera systems can struggle with depth, rotation, occlusion, and out-of-plane motion.
- Pose-estimation landmarks may be noisy during fast movement, loose clothing, or poor lighting.
- Automated movement scores are not always clinically interpretable.
- Few systems are validated specifically for lower-limb rehabilitation exercises such as squats, lunges, straight leg raises, glute bridges, step-ups, and single-leg balance.
- Published work often reports technical accuracy but less often evaluates therapist workflow, patient adherence, usability, report usefulness, or clinical decision impact.
- Safety, privacy, bias, and data governance remain central concerns for healthcare AI.

These limitations do not invalidate the use of computer vision in rehabilitation. Instead, they define the correct scope: measurement support, feedback assistance, adherence tracking, and structured reporting under clinician oversight.

## 8. Research Gap

The key research gap is the lack of accessible, therapist-centered, single-camera systems that provide interpretable lower-limb rehabilitation exercise analysis while explicitly managing uncertainty and clinical safety. Existing research demonstrates technical feasibility in pose estimation, markerless biomechanics, and automated exercise scoring, but many solutions are either laboratory-oriented, focused on general fitness, dependent on depth or multi-camera hardware, limited to narrow datasets, or insufficiently integrated into physiotherapy documentation workflows.

For knee rehabilitation, there is a need for tools that can analyze common therapeutic exercises using ordinary cameras, provide conservative movement-quality indicators, track progress over time, and generate reports that physiotherapists can review. There is also a need for systems that are transparent about limitations: camera position, landmark confidence, exercise suitability, and the fact that AI output does not replace clinical assessment.

## 9. Relevance to Movena

Movena directly addresses this gap by focusing on a constrained and clinically coherent MVP: lower-limb rehabilitation exercises commonly used in knee rehabilitation. Rather than attempting to diagnose conditions or prescribe treatment autonomously, the platform can support physiotherapists through structured movement observation.

The literature supports the following design priorities:

- Use markerless pose estimation because it improves accessibility compared with marker-based motion capture.
- Begin with transparent joint-angle and movement-quality features before relying on opaque scoring models.
- Include camera-position and landmark-confidence checks because single-camera systems are sensitive to setup.
- Use exercise-specific scoring logic because compensations differ across squats, lunges, straight leg raises, bridges, step-ups, and balance tasks.
- Design reports for therapists, including raw metrics, trend summaries, confidence notes, and flagged observations.
- Treat AI feedback as assistive and educational, not as definitive clinical judgment.

## 10. Project Justification

Movena is justified by the convergence of three needs. First, physiotherapists need practical ways to observe and quantify exercise performance outside the clinic. Second, patients performing home exercises benefit from accessible feedback that encourages correct performance and adherence. Third, recent advances in pose estimation make camera-based movement analysis feasible on consumer devices, provided the system is carefully scoped and clinically supervised.

The MVP is appropriately focused because knee rehabilitation exercises involve visible lower-limb mechanics that can be approximated from pose landmarks. A constrained exercise set also allows clearer validation, safer feedback, and more useful reports than a broad general-purpose fitness platform. By prioritizing therapist review, conservative scoring, and transparent limitations, Movena can contribute to digital rehabilitation without overstating clinical autonomy.

## 11. How This Literature Informs the MVP Design

The literature informs the MVP in the following concrete ways:

- The system should use pose landmarks to estimate lower-limb joint angles, repetition timing, and stability metrics.
- The first version should emphasize interpretable rules and thresholds, with machine-learning scoring added only after labeled data collection.
- Camera setup should be treated as part of the assessment pipeline, not as an afterthought.
- Each exercise should have a specific assessment profile: squat depth and knee tracking; lunge alignment and symmetry; straight leg raise control and range; glute bridge hip extension and pelvic symmetry; step-up control and knee alignment; single-leg balance sway and stability.
- Reports should include both performance metrics and confidence indicators.
- The UI and documentation should clearly state that the system supports physiotherapists and does not replace clinical judgment.

## 12. Conclusion

Recent literature from 2023 to 2026 supports the technical feasibility of AI-assisted, camera-based rehabilitation assessment, while also showing that clinical deployment requires caution. Markerless motion capture and pose estimation can improve access to movement measurement, but single-camera systems must manage uncertainty, environmental variation, and limits in biomechanical accuracy. For Movena, the most defensible path is a therapist-centered MVP that provides transparent lower-limb exercise metrics, conservative movement-quality flags, progress tracking, and report generation. This approach aligns with the evidence while avoiding unsafe medical claims.

## Suggested Summary for Other Project Materials

### README.md

Use a short paragraph: "Movena is grounded in recent 2023-2026 research on AI-assisted rehabilitation, markerless motion capture, human pose estimation, and remote physiotherapy. The literature supports accessible camera-based movement analysis as a decision-support tool for physiotherapists, while emphasizing the need for conservative scoring, transparent confidence indicators, and clinician oversight."

### Project Proposal

Summarize the literature as a problem-gap-solution argument. Explain that current systems show technical promise but remain limited by hardware cost, controlled datasets, poor home-environment robustness, and limited therapist-facing reporting. Position Movena as a focused MVP for knee rehabilitation that translates pose landmarks into interpretable movement metrics and progress reports.

### PowerPoint Presentation

Use four slides: background and need; current technologies and evidence; limitations and research gap; Movena MVP response. Keep the clinical safety message visible: "Supports physiotherapists; does not replace clinical judgment."

### Graduation or Project Defense

Frame the literature review as the rationale for design decisions. Emphasize why the project focuses on lower-limb exercises, why a single-camera MVP is useful but limited, why scoring is conservative, and why therapist-readable reports are central to the platform.
