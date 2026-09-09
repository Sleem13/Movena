export const DEFAULT_LOCALE = "en";
export const LOCALE_STORAGE_KEY = "movena_locale";

export const SUPPORTED_LOCALES = [
  { code: "en", label: "English", direction: "ltr" },
  { code: "ar", label: "العربية", direction: "rtl" },
];

const exerciseText = {
  bodyweight_squat: {
    en: {
      name: "Bodyweight Squat",
      short: "squat",
      bodyRegion: "Lower body and trunk",
      family: "Squat",
      cameraView: "Side or front/diagonal view",
      landmarks: ["shoulders", "hips", "knees", "ankles", "feet"],
      description: "A controlled bodyweight squat through a comfortable range.",
      pattern: "Perform 3-5 controlled squats with the full body visible.",
      safety: "Stop if pain, dizziness, or unusual symptoms occur.",
    },
    ar: {
      name: "القرفصاء بوزن الجسم",
      short: "القرفصاء",
      bodyRegion: "الجزء السفلي من الجسم والجذع",
      family: "القرفصاء",
      cameraView: "من الجانب أو من الأمام بزاوية",
      landmarks: ["الكتفان", "الوركان", "الركبتان", "الكاحلان", "القدمان"],
      description: "حركة قرفصاء مضبوطة بوزن الجسم ضمن مدى مريح.",
      pattern: "نفذ 3-5 تكرارات قرفصاء مضبوطة مع ظهور الجسم بالكامل.",
      safety: "توقف إذا شعرت بألم أو دوخة أو أعراض غير معتادة.",
    },
  },
  sit_to_stand: {
    en: {
      name: "Sit-to-Stand",
      short: "sit-to-stand",
      bodyRegion: "Lower body and trunk",
      family: "Functional transfer",
      cameraView: "Side view preferred",
      landmarks: ["shoulders", "hips", "knees", "ankles", "chair"],
      description:
        "A controlled rise from a stable chair followed by a return to sitting.",
      pattern:
        "Show complete sitting, rising, standing, lowering, and return-to-sitting cycles.",
      safety:
        "Use a stable chair and stop if pain, dizziness, or unusual symptoms occur.",
    },
    ar: {
      name: "الجلوس إلى الوقوف",
      short: "الجلوس إلى الوقوف",
      bodyRegion: "الجزء السفلي من الجسم والجذع",
      family: "انتقال وظيفي",
      cameraView: "يفضل التصوير من الجانب",
      landmarks: ["الكتفان", "الوركان", "الركبتان", "الكاحلان", "الكرسي"],
      description: "قيام مضبوط من كرسي ثابت ثم عودة إلى الجلوس.",
      pattern:
        "أظهر دورات كاملة من الجلوس والقيام والوقوف والنزول والعودة إلى الجلوس.",
      safety:
        "استخدم كرسيا ثابتا وتوقف إذا شعرت بألم أو دوخة أو أعراض غير معتادة.",
    },
  },
  knee_extension: {
    en: {
      name: "Knee Extension",
      short: "knee extension",
      bodyRegion: "Knee and lower limb",
      family: "Seated open-chain movement",
      cameraView: "Side view preferred",
      landmarks: ["hip", "knee", "ankle"],
      description:
        "A seated knee extension from a flexed position and controlled return.",
      pattern: "Extend the knee comfortably, then return with control.",
      safety: "Use a secure chair and stop if pain or unusual symptoms occur.",
    },
    ar: {
      name: "مد الركبة",
      short: "مد الركبة",
      bodyRegion: "الركبة والطرف السفلي",
      family: "حركة مفتوحة السلسلة في وضع الجلوس",
      cameraView: "يفضل التصوير من الجانب",
      landmarks: ["الورك", "الركبة", "الكاحل"],
      description: "مد الركبة أثناء الجلوس من وضع الثني ثم العودة بتحكم.",
      pattern: "مد الركبة ضمن مدى مريح ثم العودة بتحكم.",
      safety: "استخدم كرسيا آمنا وتوقف إذا ظهر ألم أو أعراض غير معتادة.",
    },
  },
  shoulder_abduction: {
    en: {
      name: "Shoulder Abduction",
      short: "shoulder abduction",
      bodyRegion: "Shoulder and upper limb",
      family: "Upper-limb range of motion",
      cameraView: "Front view preferred",
      landmarks: ["shoulders", "elbows", "wrists", "trunk"],
      description:
        "An arm raise out to the side followed by a controlled return.",
      pattern:
        "Raise the arm outward through a comfortable range and return to the side.",
      safety: "Stop if pain, numbness, dizziness, or unusual symptoms occur.",
    },
    ar: {
      name: "إبعاد الكتف",
      short: "إبعاد الكتف",
      bodyRegion: "الكتف والطرف العلوي",
      family: "مدى حركة الطرف العلوي",
      cameraView: "يفضل التصوير من الأمام",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "الجذع"],
      description: "رفع الذراع إلى الجانب ثم العودة بتحكم.",
      pattern: "ارفع الذراع إلى الخارج ضمن مدى مريح ثم أعده إلى جانب الجسم.",
      safety: "توقف إذا شعرت بألم أو خدر أو دوخة أو أعراض غير معتادة.",
    },
  },
  hip_abduction: {
    en: {
      name: "Hip Abduction",
      short: "hip abduction",
      bodyRegion: "Hip and lower limb",
      family: "Standing lower-limb range of motion",
      cameraView: "Front view preferred",
      landmarks: ["pelvis", "hips", "knees", "ankles", "trunk"],
      description:
        "A standing leg movement away from the body followed by a controlled return.",
      pattern:
        "Move one leg outward through a comfortable range while keeping the setup stable.",
      safety:
        "Use safe support if needed and stop if pain, dizziness, or unusual symptoms occur.",
    },
    ar: {
      name: "إبعاد الورك",
      short: "إبعاد الورك",
      bodyRegion: "الورك والطرف السفلي",
      family: "مدى حركة الطرف السفلي أثناء الوقوف",
      cameraView: "يفضل التصوير من الأمام",
      landmarks: ["الحوض", "الوركان", "الركبتان", "الكاحلان", "الجذع"],
      description: "تحريك الساق بعيدا عن الجسم أثناء الوقوف ثم العودة بتحكم.",
      pattern:
        "حرك ساقا واحدة إلى الخارج ضمن مدى مريح مع الحفاظ على ثبات الوضع.",
      safety:
        "استخدم دعما آمنا عند الحاجة وتوقف إذا شعرت بألم أو دوخة أو أعراض غير معتادة.",
    },
  },
  shoulder_flexion: {
    en: {
      name: "Shoulder Flexion",
      short: "shoulder flexion",
      bodyRegion: "Shoulder and upper limb",
      family: "Upper-limb range of motion",
      cameraView: "Front or slight side view",
      landmarks: ["shoulders", "elbows", "wrists", "trunk"],
      description: "A forward arm raise followed by a controlled return.",
      pattern:
        "Raise the arm forward through a comfortable visible range and return to the side.",
      safety:
        "Stop if pain, numbness, dizziness, or unusual symptoms occur; the analyzer estimates visible 2D flexion only.",
    },
    ar: {
      name: "ثني الكتف",
      short: "ثني الكتف",
      bodyRegion: "الكتف والطرف العلوي",
      family: "مدى حركة الطرف العلوي",
      cameraView: "من الأمام أو الجانب بزاوية بسيطة",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "الجذع"],
      description: "رفع الذراع إلى الأمام ثم العودة بتحكم.",
      pattern:
        "ارفع الذراع إلى الأمام ضمن مدى مريح ظاهر ثم أعده إلى جانب الجسم.",
      safety:
        "توقف إذا شعرت بألم أو خدر أو دوخة أو أعراض غير معتادة؛ يقدر المحلل الثني المرئي ثنائي الأبعاد فقط.",
    },
  },
  walking_gait_screen: {
    en: {
      name: "Walking Gait Screen",
      short: "gait screen",
      bodyRegion: "Gait and lower-limb mobility",
      family: "Walking gait screen",
      cameraView: "Side view preferred",
      landmarks: ["shoulders", "hips", "knees", "ankles", "heels", "toes"],
      description:
        "A short walking pass used to estimate gait timing, stance/swing balance, cadence, and left-right symmetry.",
      pattern:
        "Walk at a comfortable pace across the frame for several steps with both feet visible.",
      safety:
        "Use a clear, obstacle-free path and stop if pain, dizziness, imbalance, or unusual symptoms occur.",
    },
    ar: {
      name: "فحص المشي",
      short: "فحص المشي",
      bodyRegion: "المشي وحركة الطرف السفلي",
      family: "فحص نمط المشي",
      cameraView: "يفضل التصوير من الجانب",
      landmarks: [
        "الكتفان",
        "الوركان",
        "الركبتان",
        "الكاحلان",
        "الكعبان",
        "أصابع القدم",
      ],
      description:
        "مقطع مشي قصير لتقدير توقيت المشي وتوازن الوقوف/التأرجح والإيقاع والتناظر بين الجانبين.",
      pattern:
        "امش بسرعة مريحة عبر إطار الكاميرا لعدة خطوات مع ظهور القدمين بوضوح.",
      safety:
        "استخدم مسارا واضحا وخاليا من العوائق وتوقف عند الألم أو الدوخة أو فقدان التوازن أو أي أعراض غير معتادة.",
    },
  },
  balance: {
    en: {
      name: "Static Balance Screen",
      short: "balance screen",
      bodyRegion: "Balance and postural control",
      family: "Static balance hold",
      cameraView: "Front or slight diagonal view",
      landmarks: ["shoulders", "hips", "knees", "ankles", "heels", "toes"],
      description:
        "A short standing balance hold used to estimate visible postural sway, trunk lean, pelvis level, knee steadiness, and foot adjustments.",
      pattern:
        "Hold a safe standing balance position for several seconds with a support surface nearby and the full body visible.",
      safety:
        "Use a stable support surface nearby and stop if pain, dizziness, imbalance, or unusual symptoms occur.",
    },
    ar: {
      name: "فحص التوازن الثابت",
      short: "فحص التوازن",
      bodyRegion: "التوازن والتحكم الوضعي",
      family: "ثبات توازن ثابت",
      cameraView: "من الأمام أو بزاوية أمامية بسيطة",
      landmarks: [
        "الكتفان",
        "الوركان",
        "الركبتان",
        "الكاحلان",
        "الكعبان",
        "أصابع القدم",
      ],
      description:
        "ثبات قصير في وضع الوقوف لتقدير التأرجح المرئي وميل الجذع ومستوى الحوض وثبات الركبة وتعديلات القدم.",
      pattern:
        "حافظ على وضع توازن آمن لعدة ثوان مع وجود سطح دعم قريب وظهور الجسم بالكامل.",
      safety:
        "استخدم سطح دعم ثابتا قريبا وتوقف عند الألم أو الدوخة أو فقدان التوازن أو أي أعراض غير معتادة.",
    },
  },
  push_up: {
    en: {
      name: "Push-Up",
      short: "push-up",
      bodyRegion: "Upper body and trunk",
      family: "Closed-chain upper-body movement",
      cameraView: "Side view preferred",
      landmarks: ["shoulders", "elbows", "wrists", "hips", "ankles"],
      description:
        "A controlled push-up through a comfortable range with the trunk supported as one unit.",
      pattern:
        "Bend and extend the elbows while the full body remains visible from the side.",
      safety:
        "Use an appropriate supported variation and stop if pain, dizziness, numbness, or unusual symptoms occur.",
    },
    ar: {
      name: "تمرين الضغط",
      short: "الضغط",
      bodyRegion: "الجزء العلوي والجذع",
      family: "حركة دفع مغلقة السلسلة",
      cameraView: "يفضل التصوير من الجانب",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "الوركان", "الكاحلان"],
      description: "تمرين ضغط مضبوط ضمن مدى مريح مع دعم الجذع كوحدة واحدة.",
      pattern: "اثن ومد المرفقين مع ظهور الجسم بالكامل من الجانب.",
      safety:
        "استخدم مستوى دعم مناسبا وتوقف عند الألم أو الدوخة أو الخدر أو أي أعراض غير معتادة.",
    },
  },
  shoulder_press: {
    en: {
      name: "Shoulder Press",
      short: "shoulder press",
      bodyRegion: "Shoulder, upper limb, and trunk",
      family: "Overhead press",
      cameraView: "Front or slight diagonal view",
      landmarks: ["shoulders", "elbows", "wrists", "hips"],
      description:
        "An overhead pressing movement distinct from shoulder abduction.",
      pattern:
        "Begin with flexed elbows visible, extend overhead, then return with control.",
      safety:
        "Use only a clinician-approved load or unloaded practice and stop if unusual symptoms occur.",
    },
    ar: {
      name: "ضغط الكتف",
      short: "ضغط الكتف",
      bodyRegion: "الكتف والطرف العلوي والجذع",
      family: "دفع فوق الرأس",
      cameraView: "من الأمام أو بزاوية أمامية بسيطة",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "الوركان"],
      description: "حركة دفع فوق الرأس تختلف عن إبعاد الكتف.",
      pattern:
        "ابدأ والمرفقان مثنيان وظاهران ثم مد الذراعين فوق الرأس وعد بتحكم.",
      safety:
        "استخدم حملا معتمدا من المختص أو تدرب دون حمل وتوقف عند ظهور أعراض غير معتادة.",
    },
  },
  bicep_curl: {
    en: {
      name: "Bicep Curl",
      short: "bicep curl",
      bodyRegion: "Elbow and upper limb",
      family: "Elbow flexion",
      cameraView: "Front or slight side view",
      landmarks: ["shoulders", "elbows", "wrists", "hips"],
      description:
        "A controlled elbow-flexion movement observed with conservative upper-arm and trunk rules.",
      pattern:
        "Begin with the elbow extended, flex through a comfortable visible range, then return with control.",
      safety:
        "Use only a clinician-approved load or unloaded practice; the analyzer cannot assess grip or safe load.",
    },
    ar: {
      name: "ثني العضلة ذات الرأسين",
      short: "ثني الذراع",
      bodyRegion: "المرفق والطرف العلوي",
      family: "ثني المرفق",
      cameraView: "من الأمام أو الجانب بزاوية بسيطة",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "الوركان"],
      description:
        "حركة ثني للمرفق يتم رصدها بقواعد محافظة لحركة العضد والجذع.",
      pattern: "ابدأ والمرفق ممدودا، ثم اثنه ضمن مدى مريح ظاهر، وعد بتحكم.",
      safety:
        "استخدم حملا معتمدا من المختص أو تدرب دون حمل؛ لا يقيم المحلل القبضة أو الحمل الآمن.",
    },
  },
  hammer_curl: {
    en: {
      name: "Hammer Curl",
      short: "hammer curl",
      bodyRegion: "Elbow, forearm, and upper limb",
      family: "Neutral-grip elbow flexion",
      cameraView: "Front or slight side view",
      landmarks: ["shoulders", "elbows", "wrists", "hands", "hips"],
      description:
        "A neutral-grip curl analyzed for visible elbow-flexion mechanics with grip-orientation limitations.",
      pattern:
        "Begin with the elbow extended, flex through a comfortable visible range, then return with control while keeping the thumb side oriented upward when visible.",
      safety:
        "Use only a clinician-approved load or unloaded practice; body pose cannot confirm neutral grip or safe load.",
    },
    ar: {
      name: "تمرين المطرقة",
      short: "تمرين المطرقة",
      bodyRegion: "المرفق والساعد والطرف العلوي",
      family: "ثني المرفق بقبضة محايدة",
      cameraView: "من الأمام أو الجانب بزاوية بسيطة",
      landmarks: ["الكتفان", "المرفقان", "المعصمان", "اليدان", "الوركان"],
      description:
        "ثني مرفق بقبضة محايدة يحلل ميكانيكا ثني المرفق المرئية مع قيود في تأكيد اتجاه القبضة.",
      pattern:
        "ابدأ والمرفق ممدودا، ثم اثنه ضمن مدى مريح ظاهر، وعد بتحكم مع إبقاء جهة الإبهام إلى أعلى عندما تكون مرئية.",
      safety:
        "استخدم حملا معتمدا من المختص أو تدرب دون حمل؛ لا تؤكد وضعية الجسم القبضة المحايدة أو الحمل الآمن.",
    },
  },
};

export const MESSAGES = {
  en: {
    "upload.subjectSwitch":
      "More than one person may have been tracked. For best reliability, record only the person being analyzed and keep coaches or bystanders outside the frame.",
    "camera.tip.singleSubject": "One person only",
    "camera.tip.singleSubjectText":
      "Keep coaches, spotters, and bystanders outside the frame so pose tracking cannot switch subjects.",
    "upload.identifyInstead": "Identify from video",
    "upload.closeIdentification": "Close identification",
    "upload.identificationLoading": "Checking recognition model",
    "upload.recognitionReadyTitle": "Suggestion confirmed — video ready",
    "upload.recognitionReadyText":
      "The same video is selected for the {exercise} analyzer. Review the options and start analysis; there is no need to choose the file again.",
    "upload.autoRerouteNotice":
      "The selected {selected} analyzer did not detect a valid movement. Video recognition suggested {suggested} with {confidence} confidence, so Movena automatically analyzed the video with that analyzer.",
    "results.autoRoutedTitle": "Exercise recognized and assessed",
    "results.recognitionReviewTitle": "Exercise recognized — review needed",
    "language.label": "Language",
    "theme.label": "Color theme",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "theme.system": "System",
    "nav.home": "Home",
    "nav.exercises": "Exercises",
    "nav.analyze": "Analyze",
    "nav.results": "Results",
    "nav.history": "History",
    "nav.therapist": "Therapist",
    "nav.coach": "Live Coaching",
    "nav.about": "About",
    "nav.profile": "Profile",
    "nav.login": "Log in",
    "nav.admin": "Users & access",
    "nav.workflow": "Operations Dashboard",
    "nav.overview": "Overview",
    "nav.analyzeMovement": "Movement check",
    "nav.sessions": "Movement reviews",
    "nav.patients": "Patient caseload",
    "nav.security": "Profile & security",
    "nav.collapse": "Collapse",
    "nav.expand": "Expand navigation",
    "nav.openMenu": "Open navigation",
    "nav.skipContent": "Skip to content",
    "nav.workspace": "Platform",
    "nav.care": "Rehabilitation",
    "nav.today": "Today",
    "nav.tools": "Administration",
    "nav.myRehabilitation": "My rehabilitation",
    "nav.exerciseSupport": "Exercise support",
    "nav.clinicalWorkspace": "Clinical workspace",
    "nav.movementReview": "Movement review",
    "nav.operations": "Operations",
    "nav.platformTools": "Platform tools",
    "nav.progress": "Progress & activity",
    "nav.movementCheck": "Movement check",
    "nav.movementReviews": "Movement reviews",
    "nav.caseload": "Caseload",
    "nav.recoveryShort": "Recovery coaching",
    "nav.moreTools": "More tools",
    "nav.exerciseLibrary": "Exercise library",
    "nav.dashboard": "Dashboard",
    "nav.todaysPlan": "Today's Plan",
    "nav.myExercises": "My Exercises",
    "nav.aiExerciseCoach": "AI Exercise Coach",
    "nav.progressReports": "Progress & Reports",
    "nav.aiMovementReview": "AI Movement Review",
    "nav.operationsDashboard": "Operations Dashboard",
    "nav.userAdministration": "User Administration",
    "nav.analytics": "Analytics",
    "nav.movementAnalysis": "Movement Analysis",
    "nav.rehabPolicy": "RehabRL Decision Support",
    "nav.recoveryCoaching": "Recovery & Lifestyle Coaching",
    "nav.account": "Account",
    "role.patient": "Patient",
    "role.therapist": "Physiotherapist",
    "role.admin": "Administrator",
    "role.superAdmin": "Super Administrator",
    "role.support": "Support",
    "role.user": "Platform user",
    "workspace.greeting": "Welcome back, {name}",
    "workspace.subtitle":
      "Monitor rehabilitation activity and continue the next care task.",
    "workspace.viewSessions": "Review movement activity",
    "workspace.recentSessions": "Recent movement activity",
    "workspace.patient": "Patient",
    "workspace.recorded": "Recorded",
    "workspace.assignedPatient": "Assigned patient",
    "workspace.personalSession": "Personal session",
    "workspace.viewAllSessions": "View all movement activity",
    "workspace.status": "Platform readiness",
    "workspace.emailVerified": "Email verified",
    "workspace.accountAccess": "Account access",
    "workspace.accessEnabled": "Enabled",
    "workspace.protectedAdmin": "Protected super administrator",
    "workspace.role": "Role: {role}",
    "workspace.analysisReady": "Movement intelligence available",
    "workspace.viewSecurity": "View profile & security",
    "workspace.continueWorkflow": "Continue your workflow",
    "workspace.stepUpload": "Capture exercise evidence",
    "workspace.stepUploadHelp":
      "Import a video of the person performing the exercise.",
    "workspace.stepAnalyze": "Run a movement check",
    "workspace.stepAnalyzeHelp":
      "Use Movena movement intelligence for the selected exercise.",
    "workspace.stepReview": "Review movement observations",
    "workspace.stepReviewHelp":
      "AI-assisted analysis highlights movement observations for review.",
    "workspace.stepSave": "Save or export results",
    "workspace.stepSaveHelp":
      "Save the session or export results for reporting.",
    "workspace.stepPatient": "Review patient history",
    "workspace.stepPatientHelp":
      "Associate and review saved history when the workflow supports it.",
    "brand.tagline": "Movement intelligence for therapist-guided recovery",
    "footer.product": "Move Better, Recover Together.",
    "footer.disclaimer":
      "This analysis does not replace assessment, diagnosis, or treatment by a licensed professional.",
    "status.supported": "Supported",
    "status.planned": "Planned — not available yet",
    "status.notAvailable": "Not available",
    "status.experimental": "Experimental",
    "status.recognitionResearch": "Recognition research",
    "common.notAvailable": "Not available",
    "common.unavailable": "Unavailable",
    "common.unknown": "Unknown",
    "common.none": "None",
    "common.detected": "Detected",
    "common.review": "Review",
    "common.clear": "Clear",
    "common.refresh": "Refresh",
    "common.close": "Close",
    "common.download": "Download",
    "common.exercise": "Exercise",
    "common.status": "Status",
    "common.date": "Date",
    "common.score": "Score",
    "common.confidence": "Confidence",
    "common.reps": "Reps",
    "common.role": "Role",
    "common.email": "Email",
    "auth.loginIdentifier": "Username or email",
    "common.password": "Password",
    "common.displayName": "Display name",
    "common.username": "Username",
    "common.loading": "Loading",
    "common.analyzing": "Analyzing",
    "common.success": "Success",
    "common.rejected": "Rejected",
    "home.badge": "Connected rehabilitation platform",
    "home.titlePrefix": "Rehabilitation care that",
    "home.titleHighlight": "stays connected.",
    "home.description":
      "Bring therapist-led plans, daily exercise tracking, remote follow-up, and Movena movement intelligence into one continuous rehabilitation journey.",
    "home.start": "Access platform",
    "home.accessPlatform": "Access platform",
    "home.getStarted": "Get started",
    "home.openWorkspace": "Open care workspace",
    "home.openAnalyzer": "Open care workspace",
    "home.howNav": "How it works",
    "home.benefitsNav": "Benefits",
    "home.safetyNav": "Safety",
    "home.how": "See how it works",
    "home.featureRule": "Therapist-led rehabilitation",
    "home.featureClaims": "AI-assisted, never autonomous",
    "home.featureUploads": "Private movement review",
    "home.exampleEyebrow": "Example session",
    "home.exampleSummary": "Rule-based movement summary",
    "home.complete": "Complete",
    "home.movementScore": "Movement score",
    "home.completedReps": "Completed reps",
    "home.kneeTrend": "Knee angle trend",
    "home.liveSample": "Live sample",
    "home.liveAnalysis": "Live analysis",
    "home.poseTracking": "Pose tracking",
    "home.kneeAngle": "Knee 92°",
    "home.liveMeasurements": "Live joint measurements",
    "home.kneeLabel": "Knee",
    "home.hipLabel": "Hip",
    "home.trunkLabel": "Trunk",
    "home.pauseDemo": "Pause movement demo",
    "home.playDemo": "Play movement demo",
    "home.angleTrends": "Angle trends",
    "home.clearFeedback": "Clear feedback",
    "home.pdfExport": "Shareable reports",
    "home.benefitsTitle": "One rehabilitation journey, from plan to follow-up.",
    "home.benefitTrends":
      "Connect daily adherence, pain, and movement activity to the rehabilitation plan.",
    "home.benefitFeedback":
      "Keep patients and therapists aligned with clear check-ins and movement observations.",
    "home.benefitReports":
      "Turn rehabilitation activity into clinician-reviewed progress summaries.",
    "home.howEyebrow": "How it works",
    "home.howTitle": "A connected path from plan to progress",
    "home.howDescription":
      "The care plan leads the experience; Movena supports the moments where movement evidence helps.",
    "home.stepUploadTitle": "Follow today's plan",
    "home.stepUploadDescription":
      "See the prescribed dosage, instructions, precautions, and next care task.",
    "home.stepReviewTitle": "Complete a guided movement check",
    "home.stepReviewDescription":
      "When requested, Movena estimates reps, angles, and movement observations.",
    "home.stepDiscussTitle": "Share progress with your therapist",
    "home.stepDiscussDescription":
      "Combine check-ins and movement evidence for professional review and follow-up.",
    "home.safetyEyebrow": "Important safety boundary",
    "home.safetyTitle":
      "Built to support a conversation, not replace clinical care.",
    "home.safetyDescription":
      "Results are educational estimates and must not be used for diagnosis, treatment decisions, or emergency guidance.",
    "home.analyzeVideo": "Analyze a video",
    "upload.eyebrow": "Movement analyzer",
    "upload.title": "Upload a movement video",
    "upload.description":
      "Choose a clear recording for the rule-based {exercise} analyzer.",
    "upload.patientEyebrow": "Exercise support",
    "upload.patientTitle": "AI Exercise Coach",
    "upload.patientDescription":
      "Record or upload your assigned exercise for AI-assisted movement feedback.",
    "upload.reviewEyebrow": "Movement review",
    "upload.reviewTitle": "Movement Analysis",
    "upload.reviewDescription":
      "Upload a {exercise} video for AI-assisted review.",
    "upload.advancedOptions": "Advanced options",
    "upload.exerciseHelp":
      "Select the movement shown in the recording. Manual selection remains primary.",
    "upload.supportedGroup": "Supported",
    "upload.plannedGroup": "Planned — not available yet",
    "upload.recommendedView": "Recommended view",
    "upload.requiredVisibility": "Required visibility",
    "upload.instruction": "Instruction",
    "upload.safety": "Safety",
    "upload.cardTitle": "{exercise} video upload",
    "upload.fileTypes": "MP4, MOV, AVI, MKV, or WEBM · Maximum 100 MB",
    "upload.drag": "Drag and drop your {exercise} video",
    "upload.browse": "or click to browse files",
    "upload.selected": "{size} MB selected",
    "upload.chooseVideo": "Choose a {exercise} exercise video",
    "upload.errorTitle": "Analysis could not start",
    "upload.warningTitle": "Review warning before continuing",
    "upload.subjectSwitchOverrideHelp":
      "Continue only if the recording still clearly follows the intended person. The report will include this warning for manual review.",
    "upload.subjectSwitchAutoProceed":
      "Continuing automatically with this warning included in the report.",
    "upload.proceedWithWarning": "Proceed with warning",
    "upload.temporary":
      "Uploads are processed temporarily and are not patient records.",
    "upload.analyze": "Analyze {exercise}",
    "upload.analyzeMovement": "Analyze movement",
    "upload.cancelAnalysis": "Cancel analysis",
    "upload.cancelled": "Analysis cancelled. Your video remains selected.",
    "upload.movement": "Movement",
    "upload.chooseExercise": "Choose an exercise",
    "upload.pickerEyebrow": "Exercise selection",
    "upload.pickerTitle": "Which exercise is shown?",
    "upload.pickerDescription":
      "Choose the movement in your video so Movena can apply the correct analysis. Your selected video will remain in place.",
    "upload.noExerciseTitle": "Choose an exercise before analysis",
    "upload.noExerciseDescription":
      "Select from the supported movements now, or upload your video first and we'll ask before analysis.",
    "upload.progressProcessing": "Processing movement...",
    "upload.progressUploading": "Uploading video...",
    "upload.progressHelp":
      "Keep this page open while pose landmarks and selected artifacts are prepared.",
    "upload.noFile": "Select a video before starting analysis.",
    "upload.loginRequired": "Please log in before analyzing a video.",
    "upload.unsupported":
      "Unsupported video format. Please upload MP4, MOV, AVI, MKV, or WEBM.",
    "upload.network": "Could not connect to the analysis server.",
    "upload.timeout":
      "The analysis took longer than the cloud connection allows. Your video remains selected; retry with optional artifacts disabled.",
    "upload.genericError":
      "Unable to analyze this video. Check the backend and try again.",
    "upload.qualityTitle": "Recording quality check",
    "upload.qualityChecking": "Checking recording quality…",
    "upload.qualityLocal":
      "Runs locally in your browser; the video is not uploaded for this check.",
    "upload.qualityUnavailable": "Automatic quality check unavailable",
    "upload.qualityUnavailableHelp":
      "You can continue, but review the recording manually before analysis.",
    "upload.quality.pass": "Recording looks ready",
    "upload.quality.warn": "Review the recording",
    "upload.quality.fail": "Choose a clearer recording",
    "upload.qualityBadge.pass": "Ready",
    "upload.qualityBadge.warn": "Review",
    "upload.qualityBadge.fail": "Action needed",
    "upload.qualityCheck.duration": "Duration",
    "upload.qualityCheck.resolution": "Resolution",
    "upload.qualityCheck.framing": "Frame shape",
    "upload.qualityCheck.lighting": "Lighting estimate",
    "upload.qualityCheck.motion": "Visible motion",
    "upload.qualityBlockingHelp":
      "This recording is too short or too low-resolution for reliable processing. Choose another video to continue.",
    "upload.qualityWarningHelp":
      "Analysis remains available. Confirm that the person and required joints stay clearly visible throughout the movement.",
    "options.title": "Analysis options",
    "options.description":
      "Choose optional artifacts and detail. The rule-based analysis always runs.",
    "options.selectAll": "Select all",
    "options.clearAll": "Clear all",
    "options.overlayTitle": "Annotated video",
    "options.overlayDescription": "Draw a pose overlay for movement review.",
    "options.reportTitle": "PDF session report",
    "options.reportDescription": "Create a temporary downloadable report.",
    "options.frameDataTitle": "Angle trend data",
    "options.frameDataDescription":
      "Include sampled frame-level angles for charts.",
    "options.mlTitle": "ML second opinion",
    "options.mlDescription":
      "Request an optional experimental second opinion when a configured model provider is available.",
    "options.saveTitle": "Save session history",
    "options.saveDescription":
      "Save this analysis to your protected session history.",
    "options.mlUnavailable":
      "No {exercise} ML model is available; rule-based analysis remains primary.",
    "options.modelReady": "Ready",
    "options.modelUnavailable": "Unavailable",
    "camera.recordingTips": "Recording tips",
    "camera.title": "Camera placement guide",
    "camera.visible": "Keep {landmarks} visible.",
    "camera.frame":
      "Keep the lens near the movement area and all required joints fully framed.",
    "camera.lighting":
      "Use good lighting; avoid strong backlight and moving backgrounds.",
    "camera.checklist": "Visibility checklist",
    "camera.tip.side": "Side view",
    "camera.tip.sideSquat": "Best for squat depth and trunk lean.",
    "camera.tip.front": "Front view",
    "camera.tip.frontSquat": "Best for reviewing possible knee valgus.",
    "camera.tip.fullBody": "Full body visible",
    "camera.tip.fullBodyText":
      "Keep shoulders, hips, knees, ankles, and feet in frame.",
    "camera.tip.stableBright": "Stable and bright",
    "camera.tip.stableBrightText":
      "Use a fixed camera position with even lighting.",
    "camera.tip.reps": "Record 3-5 reps",
    "camera.tip.repsText": "Move at a comfortable, controlled pace when safe.",
    "camera.tip.clearJoint": "Clear joint outline",
    "camera.tip.clearJointText": "Avoid very loose clothing when possible.",
    "camera.tip.chairView": "Side or oblique view",
    "camera.tip.chairViewText":
      "Place the phone on a stable surface beside the chair when possible.",
    "camera.tip.bodyChair": "Body and chair visible",
    "camera.tip.bodyChairText":
      "Show the full body or at least shoulders, hips, knees, ankles, and chair.",
    "camera.tip.stableChair": "Use a stable chair",
    "camera.tip.stableChairText":
      "Confirm the chair is secure before recording.",
    "camera.tip.chairRepsText":
      "Show complete sitting, rising, standing, lowering, and return-to-sitting cycles.",
    "camera.tip.stop": "Stop when needed",
    "camera.tip.stopText":
      "Stop if pain, dizziness, or unusual discomfort occurs.",
    "camera.tip.kneeViewText":
      "Place the camera beside the exercising leg so the hip, knee, and ankle remain visible.",
    "camera.tip.seated": "Seated position visible",
    "camera.tip.seatedText":
      "Show the chair, thigh, lower leg, and foot throughout the recording.",
    "camera.tip.secureChair": "Stable chair",
    "camera.tip.kneeStableText":
      "Use even lighting and avoid clothing that hides the knee outline.",
    "camera.tip.kneeRepsText":
      "Begin with the knee flexed, extend comfortably, then return to the start position.",
    "camera.tip.shoulderViewText":
      "Place the camera in front so the shoulder, elbow, wrist, and trunk remain visible.",
    "camera.tip.pushUpSideText":
      "Place the camera side-on so the shoulder, elbow, wrist, hip, and ankle line remains visible.",
    "camera.tip.pushUpSupportText":
      "Use a stable floor or support surface and an appropriate supported variation.",
    "camera.tip.pushUpRepsText":
      "Begin in support, bend the elbows through a comfortable range, extend, and repeat with control.",
    "camera.tip.pressViewText":
      "Place the camera in front or slightly diagonal so both arms and the trunk remain visible overhead.",
    "camera.tip.pressPostureText":
      "Keep the camera fixed and the trunk visible throughout the overhead movement.",
    "camera.tip.pressRepsText":
      "Begin with flexed elbows, extend overhead, then return to the visible starting position with control.",
    "camera.tip.curlViewText":
      "Place the camera in front or slightly to the side so the shoulder, elbow, wrist, and trunk remain visible.",
    "camera.tip.curlPostureText":
      "Keep the trunk and upper arm visible; body pose cannot verify grip orientation or resistance.",
    "camera.tip.curlRepsText":
      "Begin with the elbow extended, flex through a comfortable range, then return to extension with control.",
    "camera.tip.hammerStableText":
      "Use even lighting and keep the hand visible when possible; grip orientation may still be unavailable.",
    "camera.tip.hammerRepsText":
      "Curl with a neutral hand position when visible, then return to extension with control.",
    "camera.tip.flexionViewText":
      "Place the camera in front or slightly to the side so the shoulder, elbow, wrist, and trunk remain visible.",
    "camera.tip.flexionPostureText":
      "Stand tall with the trunk steady and the arm beginning near the side.",
    "camera.tip.flexionRepsText":
      "Begin with the arm near the side, raise it forward comfortably, then return.",
    "camera.tip.upperBody": "Upper body visible",
    "camera.tip.upperBodyText":
      "Keep both shoulders, both arms, and the hips in frame.",
    "camera.tip.stablePosture": "Stable posture",
    "camera.tip.armStableText":
      "Use even lighting and clothing that does not hide the arm outline.",
    "camera.tip.shoulderRepsText":
      "Begin with the arm near the side, raise it outward comfortably, then return.",
    "camera.tip.shoulderStopText":
      "Stop if pain, dizziness, numbness, or unusual discomfort occurs.",
    "camera.tip.hipViewText":
      "Place the camera in front so the pelvis, hip, knee, ankle, and trunk remain visible.",
    "camera.tip.lowerBody": "Full lower body visible",
    "camera.tip.lowerBodyText":
      "Keep both hips and the moving leg in frame from pelvis to foot.",
    "camera.tip.stableSupport": "Stable support",
    "camera.tip.hipStableText":
      "Use even lighting and clothing that does not hide the hip and leg outline.",
    "camera.tip.hipRepsText":
      "Begin near neutral, move one leg outward comfortably, then return.",
    "camera.tip.gaitSideText":
      "Place the camera side-on so both legs can be tracked as the person walks across the frame.",
    "camera.tip.gaitLowerBodyText":
      "Keep hips, knees, ankles, heels, and toes visible for both legs.",
    "camera.tip.clearPath": "Clear path",
    "camera.tip.clearPathText":
      "Use an obstacle-free walking path with enough room for several comfortable steps.",
    "camera.tip.steps": "Record several steps",
    "camera.tip.gaitStepsText":
      "Capture a steady walking pass with at least two same-side gait cycles when safe.",
    "camera.tip.gaitStableText":
      "Use a fixed camera position with even lighting and minimal motion blur.",
    "camera.tip.gaitStopText":
      "Stop if pain, dizziness, imbalance, or unusual discomfort occurs.",
    "camera.tip.balanceViewText":
      "Place the camera in front or slightly diagonal so the trunk, pelvis, legs, and feet remain visible.",
    "camera.tip.balanceFullBodyText":
      "Keep shoulders, hips, knees, ankles, heels, and toes in frame throughout the hold.",
    "camera.tip.balanceSupportText":
      "Keep a stable counter, rail, or chair nearby without blocking the body.",
    "camera.tip.hold": "Hold steady",
    "camera.tip.balanceHoldText":
      "Capture several seconds of a safe standing balance hold without stepping when possible.",
    "camera.tip.balanceStableText":
      "Use a fixed camera position with even lighting and minimal background movement.",
    "camera.tip.balanceStopText":
      "Stop if pain, dizziness, imbalance, or unusual discomfort occurs.",
    "exercises.eyebrow": "Exercise library",
    "exercises.title": "Exercise library",
    "exercises.description":
      "Choose an exercise to review your movement.",
    "exercises.researchTitle": "Exercise coaching expansion is in research",
    "exercises.researchDescription":
      "Pose-data preparation and a versioned XGBoost recognition path are implemented. Push-up, shoulder-press, bicep-curl, hammer-curl, and shoulder-flexion analyzers use conservative analysis paths with visible-pose limitations.",
    "exercises.researchBadge": "Suggestion only",
    "exercises.search": "Search exercises",
    "exercises.posePreview": "movement preview diagram",
    "exercises.searchPlaceholder": "Search exercises",
    "exercises.clearFilters": "Clear filters",
    "exercises.researchAndPlanned": "Research and planned exercises",
    "exercises.pages": "Exercise pages",
    "exercises.next": "Next exercises",
    "exercises.previous": "Previous exercises",
    "exercises.availability": "Availability",
    "exercises.allAvailability": "All availability",
    "exercises.supportedOnly": "Supported only",
    "exercises.plannedOnly": "Planned only",
    "exercises.bodyRegion": "Body region",
    "exercises.allRegions": "All regions",
    "exercises.matchCount": "{count} {label} {verb} your filters.",
    "exercises.matchVerbSingular": "matches",
    "exercises.matchVerbPlural": "match",
    "exercises.matchSingular": "exercise",
    "exercises.matchPlural": "exercises",
    "exercises.noMatch": "No exercises match",
    "exercises.noMatchDescription":
      "Clear filters or try a broader search term.",
    "exercises.supportedTitle": "Available exercises",
    "exercises.supportedDescription":
      "Available for rule-based video analysis now.",
    "exercises.availableCount": "{count} available",
    "exercises.noSupported": "No supported exercises in this view",
    "exercises.adjustSupported":
      "Adjust filters to include available analyzers.",
    "exercises.plannedTitle": "Planned exercises",
    "exercises.plannedDescription":
      "Roadmap coverage only; these analyzers are not active.",
    "exercises.plannedCount": "{count} planned",
    "exercises.noPlanned": "No planned exercises in this view",
    "exercises.adjustPlanned": "Adjust filters to include roadmap exercises.",
    "exercises.analyzeThis": "Analyze this exercise",
    "exercises.startExercise": "Start Exercise",
    "exercises.reviewExercise": "View & Analyze",
    "auth.loginEyebrow": "Welcome back",
    "auth.loginTitle": "Log in to Movena",
    "auth.loginDescription":
      "Use your account to securely access the platform.",
    "auth.warning":
      "Protect patient privacy. Only enter information you are authorized to process and follow your organization's consent and data-handling policies.",
    "auth.sideEyebrow": "Secure platform access",
    "auth.sideTitle": "Continue your movement review workspace.",
    "auth.sideDescription":
      "Access saved sessions, exercise analysis tools, and therapist-facing review surfaces.",
    "auth.sideWarning":
      "Use Movena in accordance with your organization's privacy, consent, and record-retention policies.",
    "auth.expired": "Your session may have expired. Please log in again.",
    "auth.invalid": "Please check your username/email and password.",
    "auth.network":
      "Cannot reach the login server. Confirm the backend is running, then try again.",
    "auth.unavailable": "Login is temporarily unavailable.",
    "auth.loggingIn": "Logging in...",
    "auth.login": "Log in",
    "auth.needAccount": "Need an account?",
    "auth.createOne": "Create one",
    "auth.backToLogin": "Back to login",
    "auth.registerBadge": "Secure platform access",
    "auth.registerTitle": "Create your account",
    "auth.registerDescription": "Set up your secure Movena workspace.",
    "auth.created": "Account created. You can log in immediately.",
    "auth.registerFailed": "Registration failed.",
    "auth.displayPlaceholder": "Your name",
    "auth.usernamePlaceholder": "your.username",
    "auth.usernameHelp":
      "Use 3–64 letters, numbers, dots, hyphens, or underscores. You can use this username to log in.",
    "auth.passwordHelp": "Use at least 8 characters.",
    "auth.acceptTerms":
      "I accept the Terms of Use and understand this platform does not replace medical judgment.",
    "auth.acceptPrivacy":
      "I have read and accept the Privacy Policy and consent to processing my care data.",
    "auth.creating": "Creating account...",
    "auth.createAccount": "Create account",
    "auth.forgotPassword": "Forgot password?",
    "auth.resendVerification": "Resend verification",
    "auth.managedAccessHelp":
      "Email verification and recovery are temporarily managed by your super administrator.",
    "profile.title": "Profile",
    "profile.developmentUser": "Movena user",
    "profile.logout": "Log out",
    "profile.workflowDescription":
      "Monitor the care journey, operational exceptions, privacy requests, and audit activity from one de-identified view.",
    "profile.openWorkflow": "Open Operations Dashboard",
    "workflow.eyebrow": "Super Admin operations",
    "workflow.title": "Operations Dashboard",
    "workflow.description":
      "Monitor the complete care journey, surface operational exceptions, and coordinate accountable follow-up without exposing clinical details.",
    "workflow.metrics": "Platform metrics",
    "workflow.metric.users": "Total users",
    "workflow.metric.patients": "Patients",
    "workflow.metric.active_assignments": "Active assignments",
    "workflow.metric.appointments": "Appointments",
    "workflow.metric.paid_orders": "Paid orders",
    "workflow.railTitle": "Care delivery workflow",
    "workflow.railDescription":
      "Live operational status across the patient journey",
    "workflow.stage.account_consent": "Account & consent",
    "workflow.stage.therapist_assignment": "Therapist assignment",
    "workflow.stage.care_plan": "Care plan",
    "workflow.stage.appointment": "Appointment",
    "workflow.stage.payment": "Payment",
    "workflow.stage.follow_up": "Follow-up",
    "workflow.total": "total",
    "workflow.onTrack": "On track",
    "workflow.needAttention": "need attention",
    "workflow.attentionQueue": "Needs attention",
    "workflow.deidentified": "De-identified operational references only",
    "workflow.type": "Workflow type",
    "workflow.type.privacy_request": "Privacy request",
    "workflow.type.assignment": "Assignment",
    "workflow.type.care_plan": "Care plan",
    "workflow.type.appointment": "Appointment",
    "workflow.type.payment": "Payment",
    "workflow.type.password_recovery": "Password recovery",
    "workflow.allWorkflows": "All workflows",
    "workflow.allPriorities": "All priorities",
    "workflow.priority": "Priority",
    "workflow.priority.high": "High",
    "workflow.priority.medium": "Medium",
    "workflow.priority.low": "Low",
    "workflow.workflow": "Workflow",
    "workflow.reference": "Reference",
    "workflow.owner": "Owner",
    "workflow.age": "Age",
    "workflow.action": "Action",
    "workflow.review": "Review",
    "workflow.reviewing": "Reviewing",
    "workflow.queueEmpty": "No matching exceptions",
    "workflow.queueEmptyDescription":
      "Try another filter or refresh the workflow snapshot.",
    "workflow.today": "Today in Cairo",
    "workflow.appointments": "Appointments",
    "workflow.paymentExceptions": "Payment exceptions",
    "workflow.pending_orders": "Pending orders",
    "workflow.failed_payments": "Failed payments",
    "workflow.pending_refunds": "Pending refunds",
    "workflow.privacyRequests": "Privacy requests",
    "workflow.pending": "pending",
    "workflow.export": "Export",
    "workflow.correction": "Correction",
    "workflow.deletion": "Deletion",
    "workflow.recentAudit": "Recent audit activity",
    "workflow.auditDescription":
      "Sensitive operational changes, recorded for accountability",
    "workflow.actor": "Actor",
    "workflow.event": "Event",
    "workflow.resource": "Resource",
    "workflow.when": "Cairo time",
    "workflow.noAudit": "No audit activity yet",
    "workflow.refresh": "Refresh",
    "workflow.manageUsers": "Manage users",
    "workflow.generatedAt": "Updated",
    "workflow.loading": "Loading workflow…",
    "workflow.loadError": "The workflow snapshot could not be loaded.",
    "workflow.tryAgain": "Try again",
    "results.emptyTitle": "No analysis results yet",
    "results.emptyDescription":
      "Upload a supported exercise video to create a movement dashboard.",
    "results.goAnalyze": "Go to Analyze",
    "results.rejectedEyebrow": "Recording rejected",
    "results.completeEyebrow": "Analysis complete",
    "results.rejectedTitle": "{exercise} recording could not be scored",
    "results.reportTitle": "{exercise} report",
    "results.rejectedDescription":
      "Review the recording guidance and try again with a complete {movement} sequence.",
    "results.completeDescription":
      "Review movement metrics, visual evidence, feedback, and known limitations from this session.",
    "results.savedSession": "Saved session",
    "results.sessionStored":
      "Session {session} · saved to your session history",
    "results.viewHistory": "View Session History",
    "results.continueCheckIn": "Continue exercise check-in",
    "results.metrics": "Analysis key metrics",
    "results.movementScore": "Movement score",
    "results.analysisConfidence": "Analysis confidence",
    "results.totalReps": "Total reps",
    "results.averageKnee": "Average knee",
    "results.averageHip": "Average hip",
    "results.averageTrunk": "Average trunk",
    "results.averageShoulder": "Average shoulder",
    "results.averageElbow": "Average elbow",
    "results.averageHipAbduction": "Average hip abduction",
    "results.gaitCadence": "Cadence",
    "results.gaitCycles": "Gait cycles",
    "results.gaitStanceSwing": "Stance / swing",
    "results.gaitSymmetry": "Temporal symmetry",
    "results.gaitStrideVariability": "Stride variability",
    "results.gaitKneeRange": "Knee range",
    "results.balanceDuration": "Hold duration",
    "results.balanceMode": "Stance mode",
    "results.balanceSway": "Sway RMS",
    "results.balanceVelocity": "Sway velocity",
    "results.balanceTrunkLean": "Max trunk lean",
    "results.unitStepsMin": "steps/min",
    "results.unitSeconds": "sec",
    "results.unitNormalized": "normalized",
    "results.unitPercent": "%",
    "results.detectedIssues": "Detected issues",
    "results.reliability": "Reliability",
    "results.confidenceLabel": "{level} confidence",
    "results.repCountConfidence": "Rep count confidence",
    "results.partialIgnored": "{count} partial {cycle} ignored",
    "results.cycleSingular": "cycle",
    "results.cyclePlural": "cycles",
    "results.poseQuality": "Pose quality",
    "results.framesDetected": "{level} · {rate}% frames detected",
    "results.qualityNotMeasured": "Recording quality was not measured.",
    "results.reviewQuality": "Review recording quality",
    "results.noConfidenceWarnings":
      "No additional confidence warnings were returned.",
    "results.explainableScore": "Explainable score",
    "results.scoreBreakdown": "Score breakdown",
    "results.breakdown.completion": "Completion",
    "results.breakdown.movementControl": "Movement control",
    "results.breakdown.trunkControl": "Trunk control",
    "results.breakdown.consistency": "Consistency",
    "results.breakdown.poseConfidence": "Pose confidence",
    "results.breakdown.extensionRange": "Extension range",
    "results.breakdown.flexionRange": "Flexion range",
    "results.breakdown.visibility": "Visibility",
    "results.breakdown.repCompletion": "Rep completion",
    "results.breakdown.abductionRange": "Abduction range",
    "results.breakdown.depth": "Depth",
    "results.breakdown.kneeAlignment": "Knee alignment",
    "results.breakdown.pelvisTrunkStability": "Pelvis/trunk stability",
    "results.breakdown.gaitPhase": "Gait phase timing",
    "results.breakdown.cadence": "Cadence",
    "results.breakdown.symmetry": "Temporal symmetry",
    "results.breakdown.strideConsistency": "Stride consistency",
    "results.breakdown.kinematicRange": "Kinematic range",
    "results.breakdown.holdDuration": "Hold duration",
    "results.breakdown.swayControl": "Sway control",
    "results.breakdown.pelvisControl": "Pelvis control",
    "results.breakdown.kneeStability": "Knee stability",
    "results.unitDegrees": "degrees",
    "results.breakdownUnavailable": "Score breakdown unavailable",
    "results.breakdownOlder": "This analysis used an older API response.",
    "results.repReview": "Rep count review",
    "results.manualReview": "Manual review recommended",
    "results.lowConfidenceText":
      "The movement was detected, but rep count confidence is low due to noisy pose tracking or inconsistent visibility.",
    "results.partialText":
      "{count} meaningful incomplete movement {cycle} {verb} ignored and did not change the completed rep count.",
    "results.trimSquat":
      "Review camera setup and consider trimming the video to only the squat set.",
    "results.trimExercise":
      "Review camera setup and consider trimming the video to only the recorded exercise set.",
    "results.sessionOverview": "Session overview",
    "results.observationCount": "{count} {label}",
    "results.observationSingular": "observation",
    "results.observationPlural": "observations",
    "results.noMajorFlags": "No major flags",
    "results.scoreDisclaimer":
      "A rule-based session summary, not a diagnosis or clinical outcome measure.",
    "results.videoReview": "Video review",
    "results.videoReviewHelp":
      "Compare the source recording with the generated pose overlay.",
    "results.originalUpload": "Original upload",
    "results.annotatedPreview": "Annotated movement preview",
    "results.originalPreviewUnavailable": "Original preview unavailable",
    "results.originalPreviewHelp":
      "Local previews are available immediately after uploading in this browser session.",
    "results.annotatedLoadFailed": "Annotated preview could not be loaded",
    "results.annotatedNotGenerated":
      "No annotated preview was generated for this analysis.",
    "results.loadingAnnotated": "Preparing annotated preview",
    "results.retryPreview": "Retry preview",
    "results.artifactExpired":
      "The temporary artifact may have expired. Retry the analysis to generate a new overlay.",
    "results.enableOverlay":
      "Enable Annotated video on the upload page to request an experimental 2D skeleton overlay.",
    "results.videoUnsupported": "Your browser does not support video playback.",
    "results.overlayHelp":
      "Experimental 2D overlay; markers and phase labels may shift with occlusion, motion blur, or camera angle.",
    "results.noIssues":
      "No major movement issues were flagged by the current rules.",
    "results.summaryFeedback": "Summary and feedback",
    "results.noSummary": "No summary returned.",
    "results.correctiveFeedback": "Corrective feedback",
    "results.noFeedback": "No corrective feedback returned.",
    "results.mlTitle": "ML second opinion",
    "results.mlHelp": "Optional experimental comparison",
    "results.mlBadge": "Experimental · not clinically validated",
    "results.mlVerifiedBadge": "Verified artifact · therapist review required",
    "results.experimentalQuality": "Experimental quality",
    "results.predictedLabel": "Predicted label",
    "results.model": "Model",
    "results.modelMode": "Model mode",
    "results.providerStatus": "Provider status",
    "results.baselineUnavailable": "Baseline unavailable",
    "results.mlPrimary": "Rule-based analysis remains primary",
    "results.mlWarning":
      "This output is experimental and must not guide clinical decisions.",
    "results.mlDisagreement": "Experimental ML disagreement",
    "results.knownLimitations": "Known limitations",
    "results.noLimitations": "No additional limitations returned.",
    "results.medicalDisclaimer": "Medical disclaimer",
    "results.disclaimer":
      "Movena supports exercise monitoring and does not replace assessment by a licensed physiotherapist. This educational analysis does not provide diagnosis or treatment.",
    "results.downloadPdf": "Download PDF report",
    "results.downloadOverlay": "Download annotated video",
    "results.exportJson": "Export JSON",
    "results.analyzeAnother": "Analyze another video",
    "results.recordingReview": "Recording needs review",
    "results.noValidMovement": "No valid {exercise} movement detected",
    "results.tryAgain": "Try recording again",
    "results.tryAgainBodyweightSquat":
      "Record full body, 3–5 squat reps, stable camera, good lighting.",
    "results.tryAgainSitToStand":
      "Show the body and stable chair from a side or oblique view for 3-5 complete repetitions.",
    "results.tryAgainKneeExtension":
      "Use a stable side view with the seated hip, knee, ankle, and moving lower leg visible for 3-5 complete repetitions.",
    "results.tryAgainShoulderAbduction":
      "Use a stable front view with the shoulder, elbow, wrist, and trunk visible for 3-5 complete repetitions.",
    "results.tryAgainHipAbduction":
      "Use a stable front view with the pelvis, hip, knee, ankle, and trunk visible for 3-5 complete repetitions.",
    "results.tryAgainWalkingGaitScreen":
      "Use a stable side view with the full lower body and both feet visible for several comfortable walking steps.",
    "results.tryAgainBalance":
      "Use a stable front or slight diagonal view with the full body and feet visible for a safe standing balance hold.",
    "results.tryAgainPushUp":
      "Use a stable side view with shoulders, elbows, wrists, hips, and ankles visible in a supported push-up position for 3-5 complete repetitions.",
    "results.tryAgainShoulderPress":
      "Use a stable front or slight diagonal view with the shoulders, elbows, wrists, and trunk visible for 3-5 complete repetitions.",
    "results.tryAgainBicepCurl":
      "Use a stable front or slight side view with the shoulder, elbow, wrist, and trunk visible for 3-5 complete repetitions.",
    "results.tryAgainHammerCurl":
      "Use a stable front or slight side view with the shoulder, elbow, wrist, hand, and trunk visible for 3-5 complete repetitions.",
    "results.tryAgainShoulderFlexion":
      "Use a stable front or slight side view with the shoulder, elbow, wrist, and trunk visible for 3-5 forward arm raises.",
    "chart.outOf100": "out of 100",
    "chart.angleUnavailable": "Angle trends unavailable",
    "chart.angleHelp":
      "Enable Angle trend data before analysis to include sampled frame-level measurements.",
    "chart.angleTrend": "Angle trend",
    "chart.angleTrendDescription":
      "Sampled angle estimates across the analyzed video.",
    "chart.issueBreakdown": "Issue breakdown",
    "chart.issueBreakdownDescription":
      "Summary flags or sampled frame issue counts.",
    "chart.movementProfile": "Movement profile",
    "chart.movementProfileDescription":
      "Normalized descriptive values from this session.",
    "chart.repQuality": "Rep quality",
    "chart.repQualityDescription":
      "Individual repetition scoring requires rep-level API data.",
    "chart.angleAria": "Movement angle trends",
    "chart.start": "Start",
    "chart.end": "End",
    "chart.noIssueBreakdown": "No issue breakdown",
    "chart.noIssueHelp": "No movement issues were returned in this analysis.",
    "chart.sampledFrames": "{count} sampled frames",
    "chart.profileAria": "Descriptive movement profile radar",
    "chart.normalized":
      "Normalized descriptive profile for this session, not a validated clinical scale.",
    "chart.repPlanned": "Rep-level quality is planned",
    "chart.repHelp":
      "The current API returns total repetitions but not individual rep scores.",
    "chart.rep": "Rep {count}",
    "chart.score": "Score",
    "chart.knee": "Knee",
    "chart.hip": "Hip",
    "chart.shoulder": "Shoulder",
    "chart.visibility": "Visibility",
    "chart.trunk": "Trunk",
    "chart.issueLoad": "Issue load",
    "history.eyebrow": "Session history",
    "history.title": "Saved sessions",
    "history.description":
      "Review movement-analysis metadata saved to your protected session history.",
    "history.patientTitle": "Progress & Reports",
    "history.patientDescription":
      "Review your saved exercise activity and shared movement reports.",
    "history.therapistTitle": "Movement Review History",
    "history.loadError": "Session history could not be loaded.",
    "history.detailError": "Saved session detail could not be loaded.",
    "history.allExercises": "All exercises",
    "history.allStatuses": "All statuses",
    "history.newest": "Newest first",
    "history.oldest": "Oldest first",
    "history.unavailable": "History unavailable",
    "history.loading": "Loading sessions",
    "history.emptyTitle":
      "No saved sessions yet. Analyze a video and enable Save Session.",
    "history.emptyDescription":
      "Only analysis metadata is stored locally; uploaded videos are not retained.",
    "history.noFlags": "No saved issue flags.",
    "history.viewDetails": "View details",
    "history.hideDetails": "Hide details",
    "history.loadingDetail": "Loading details",
    "history.report": "Report",
    "history.overlay": "Overlay",
    "history.detail": "Saved session detail",
    "history.noSummary": "No summary was saved.",
    "history.reportViewer": "Session report",
    "history.overlayViewer": "Annotated overlay",
    "history.loadingArtifact": "Loading artifact",
    "history.artifactUnavailable": "Artifact unavailable",
    "history.artifactExpired":
      "This temporary artifact has expired or was removed. Run the analysis again to generate a new one.",
    "history.artifactError":
      "The artifact could not be loaded. Check the backend connection and try again.",
    "history.compareAction": "Compare",
    "history.compareTitle": "Compare saved sessions",
    "history.compareSelectSecond":
      "Select another session of the same exercise to compare.",
    "history.compareDescription":
      "Review recorded differences between two sessions of the same movement.",
    "history.compareClear": "Clear comparison",
    "history.compareLoading": "Loading comparison",
    "history.compareError": "The selected session details could not be loaded.",
    "history.compareSameExercise": "Choose sessions from the same exercise.",
    "history.compareEarlier": "Earlier session",
    "history.compareLater": "Later session",
    "history.compareScore": "Movement score",
    "history.compareReps": "Repetitions",
    "history.compareKnee": "Average knee angle",
    "history.compareHip": "Average hip angle",
    "history.compareTrunk": "Average trunk angle",
    "history.compareShoulder": "Average shoulder angle",
    "history.compareElbow": "Average elbow angle",
    "history.compareDisclaimer":
      "Differences are descriptive product observations, not recovery percentages or evidence of clinical improvement or deterioration.",
    "history.notice":
      "Protect patient privacy and save only information you are authorized to process. Movena analysis should not be used as the sole clinical record.",
    "therapist.eyebrow": "Clinical workspace",
    "therapist.title": "Clinical Dashboard",
    "therapist.description":
      "Review patients, movement sessions, and rehabilitation progress.",
    "therapist.welcome": "Welcome back, Dr. {name}",
    "therapist.reviewPatients": "Review Patients",
    "therapist.analyzeMovement": "Analyze Movement",
    "therapist.viewSessions": "View Sessions",
    "therapist.warningTitle": "Privacy and clinical-use notice",
    "therapist.warning":
      "Only process patient information with appropriate authorization and consent, and follow your organization's privacy and retention policies. AI feedback supports exercise monitoring and does not replace assessment by a licensed physiotherapist.",
    "therapist.noPermission": "You do not have permission to view this page.",
    "therapist.login": "Please log in to continue.",
    "therapist.loadError": "Therapist dashboard data could not be loaded.",
    "therapist.profileCreateError": "Patient profile could not be created.",
    "therapist.detailError": "Patient profile details could not be loaded.",
    "therapist.dashboard": "Dashboard",
    "therapist.patients": "Patient profiles",
    "therapist.errorTitle": "Dashboard error",
    "therapist.loading": "Loading dashboard",
    "therapist.totalPatients": "Total patients",
    "therapist.totalSessions": "Total sessions",
    "therapist.lowConfidenceSessions": "Low-confidence sessions",
    "therapist.commonIssue": "Most common issue",
    "therapist.recentSessions": "Recent sessions",
    "therapist.scoreTrend": "Movement score trend",
    "therapist.scoreTrendDescription":
      "Scores from the latest saved sessions, ordered over time.",
    "therapist.noScoredSessions":
      "Scored sessions will appear here after movement analysis.",
    "therapist.noSavedSessions": "No saved sessions yet.",
    "therapist.commonIssues": "Common detected issues",
    "therapist.noIssueHistory": "No detected issue history.",
    "therapist.sessionsByExercise": "Sessions by exercise",
    "therapist.exerciseDistributionDescription":
      "A visual comparison of saved analysis volume by movement.",
    "therapist.issueFrequencyDescription":
      "How often each observation appears across saved sessions.",
    "therapist.lowConfidenceByExercise": "Low-confidence sessions by exercise",
    "therapist.noLowConfidence": "No low-confidence sessions.",
    "therapist.createProfile": "Create patient profile",
    "therapist.profileHelp":
      "Use the patient identifier approved by your organization and avoid unnecessary identifying details.",
    "therapist.profileName": "Patient display name or identifier",
    "therapist.profilePlaceholder": "Example: Patient 1042",
    "therapist.createProfileButton": "Create profile",
    "therapist.emptyProfiles": "No patient profiles yet",
    "therapist.emptyProfilesDescription":
      "Create a managed patient profile to organize authorized movement sessions.",
    "therapist.savedSessionCount": "{count} saved {label}",
    "therapist.sessionSingular": "session",
    "therapist.sessionPlural": "sessions",
    "therapist.viewProfile": "View profile",
    "therapist.backToProfiles": "Back to profiles",
    "therapist.developmentProfile": "Patient profile",
    "therapist.averageScore": "Average score",
    "therapist.averageConfidence": "Average confidence",
    "therapist.exerciseHistory": "Exercise session history",
    "therapist.noAssignedSessions": "No sessions assigned to this profile.",
    "therapist.detectedIssueCounts": "Detected issue counts",
    "therapist.observationCount": "{count} source values",
    "therapist.provenanceTitle": "Progress data provenance",
    "therapist.provenanceSummary":
      "Longitudinal values are calculated only from saved sessions assigned to this profile. Latest saved session: {date}. These trends are product observations, not recovery percentages.",
    "therapist.noProvenance":
      "No saved sessions are assigned yet, so progress metrics are intentionally empty.",
    "therapist.rowReps": "{value} reps",
    "therapist.rowScore": "score {value}",
    "therapist.rowConfidence": "confidence {value}",
    "therapist.productionNotice":
      "Access is role-protected. Follow your organization's consent, privacy, retention, and clinical-governance requirements.",
    "therapist.createPlan": "Create exercise plan",
    "therapist.planHelp":
      "Document the clinician-authored prescription separately from AI movement observations.",
    "therapist.planTitle": "Plan title",
    "therapist.planNotes": "Clinical notes (optional)",
    "therapist.planExercise": "Exercise {count}",
    "therapist.removeExercise": "Remove exercise",
    "therapist.exercise": "Exercise",
    "therapist.sets": "Sets",
    "therapist.reps": "Reps",
    "therapist.days_per_week": "Days/week",
    "therapist.instructions": "Patient instructions (optional)",
    "therapist.addExercise": "Add another exercise",
    "therapist.savePlan": "Assign plan",
    "therapist.savingPlan": "Saving plan",
    "therapist.planSaveError": "The exercise plan could not be saved.",
    "therapist.planStatusError": "The plan status could not be updated.",
    "therapist.assignedPlans": "Assigned exercise plans",
    "therapist.assignedPlansHelp":
      "Current and previous clinician-authored prescriptions.",
    "therapist.noPlans": "No exercise plans assigned",
    "therapist.noPlansHelp":
      "Create the first plan to document sets, repetitions, frequency, and instructions.",
    "therapist.planStatus.active": "Active",
    "therapist.planStatus.paused": "Paused",
    "therapist.planStatus.completed": "Completed",
    "therapist.activate": "Activate",
    "therapist.pause": "Pause",
    "therapist.complete": "Complete",
    "therapist.prescription": "{sets} sets × {reps} reps · {days} days/week",
    "therapist.baselineComparison": "Baseline and latest session",
    "therapist.baselineHelp":
      "Compare the first and latest scored sessions for each exercise using saved movement-analysis observations.",
    "therapist.scoredSessions": "{count} scored sessions",
    "therapist.scoredSession": "{count} scored session",
    "therapist.baseline": "Baseline",
    "therapist.latest": "Latest",
    "therapist.observedChange": "Observed change",
    "therapist.comparisonAria":
      "{exercise}: baseline score {baseline}, latest score {latest}",
    "therapist.repsComparison":
      "Repetitions: {baseline} at baseline → {latest} latest ({delta})",
    "therapist.needAnotherSession": "One more scored session is needed",
    "therapist.noScoredExerciseSessions":
      "No scored sessions for this exercise",
    "therapist.currentBaseline": "Current baseline: {score} on {date}.",
    "therapist.scoreRequired":
      "Complete and save a scored analysis to establish a baseline.",
    "therapist.noBaselineData": "No baseline data yet",
    "therapist.noBaselineHelp":
      "Assign saved analysis sessions to this profile to begin a per-exercise comparison.",
    "therapist.baselineDisclaimer":
      "Score and repetition differences are descriptive product observations. They are not recovery percentages and do not establish clinical improvement or deterioration.",
    "about.eyebrow": "About the product",
    "about.title": "Movement insight with a clear safety boundary",
    "about.description":
      "Movena is movement intelligence for therapist-guided recovery, combining computer-vision landmarks, explicit biomechanics rules, and optional assisted-review tools.",
    "about.safetyTitle": "Safety before certainty",
    "about.safetyText":
      "Results stay conservative, disclose limitations, and never claim diagnosis.",
    "about.transparentTitle": "Transparent interpretation",
    "about.transparentText":
      "Pretrained pose models estimate landmarks; explicit rules interpret movement mechanics.",
    "about.conversationTitle": "Built for conversation",
    "about.conversationText":
      "Reports help users and reviewers discuss movement together, not replace professional assessment.",
    "about.readyTitle": "Ready to review a movement?",
    "about.readyText":
      "Use a stable, full-body recording for the clearest educational report.",
    "about.openAnalyzer": "Open analyzer",
    "speech.listen": "Listen to feedback",
    "speech.stop": "Stop audio",
    "speech.unavailable": "Spoken feedback is not supported by this browser.",
    "speech.statusComplete": "{exercise} analysis complete.",
    "speech.statusRejected":
      "The {exercise} recording was rejected and could not be scored.",
    "speech.reps": "Completed repetitions: {count}.",
    "speech.score": "Movement score: {score} out of 100.",
    "speech.confidence": "Analysis confidence: {level}.",
    "speech.feedbackIntro": "Feedback:",
    "speech.limitationsIntro": "Important limitations:",
    "speech.disclaimer":
      "This educational analysis does not provide diagnosis or treatment and does not replace a licensed professional.",
    "coach.eyebrow": "AI movement tools",
    "coach.title": "Exercise coaching lab",
    "coach.description":
      "A local camera and model-readiness workspace for developing future real-time coaching without activating unvalidated movement feedback.",
    "coach.cameraTitle": "Local camera capture",
    "coach.cameraHelp":
      "Camera access starts only after you press start. Audio is disabled and no stream is uploaded.",
    "coach.videoLabel": "Local camera preview",
    "coach.start": "Start camera",
    "coach.stop": "Stop camera",
    "coach.status.idle": "Idle",
    "coach.status.requesting": "Requesting camera",
    "coach.status.active": "Camera active",
    "coach.status.stopped": "Stopped",
    "coach.errorTitle": "Camera unavailable",
    "coach.noCameraError":
      "No camera was detected on this device. You can still identify or analyze an exercise by uploading a video below.",
    "coach.permissionDeniedError":
      "Camera permission is blocked. Allow camera access in your browser and Windows privacy settings, then try again. Video upload remains available.",
    "coach.cameraBusyError":
      "The camera is unavailable or already being used by another application. Close other camera apps and try again, or upload a video below.",
    "coach.cameraConstraintsError":
      "The connected camera could not provide a compatible video stream. Try another camera or upload a video below.",
    "coach.unsupported":
      "This browser does not support camera capture for the technical spike.",
    "coach.permissionError": "Camera access was blocked or could not start.",
    "coach.safetyTitle": "Technical spike only",
    "coach.safetyText":
      "No video or audio is uploaded, no frames are retained, and this page does not provide clinical guidance.",
    "coach.derivedTitle": "Derived local signals",
    "coach.samples": "Samples",
    "coach.brightness": "Brightness",
    "coach.visibility": "Visibility proxy",
    "coach.latency": "Mean elapsed time",
    "coach.landmarksIdle":
      "The on-device pose model loads when the camera starts.",
    "coach.landmarksLoading": "Loading the on-device pose model...",
    "coach.landmarksError":
      "The on-device pose model could not start. Check your connection and browser WebAssembly support, then restart the camera.",
    "coach.landmarksEnabled":
      "On-device pose tracking active: {count} landmarks, average confidence {confidence}.",
    "coach.modelTitle": "Recognition model readiness",
    "coach.modelAvailable": "Candidate models ready",
    "coach.modelPending": "Artifact pending",
    "coach.complete": "Real-time coaching ready",
    "coach.modelDescription":
      "The installed XGBoost and temporal GRU candidates can suggest an exercise. They never start an analyzer or replace manual selection.",
    "coach.stepData":
      "40-feature pose-data contract and preparation pipeline implemented",
    "coach.stepRecognition":
      "XGBoost and temporal GRU candidates trained with video-grouped holdouts",
    "coach.stepAnalyzers":
      "Conservative push-up, shoulder-press, bicep-curl, hammer-curl, and shoulder-flexion analyzers implemented with visible-pose limitations",
    "coach.stepRealtime":
      "Authenticated streaming, rep events, and persistence pending",
    "coach.stepAnalyzersComplete":
      "Conservative analyzers implemented; hammer-curl hand-orientation evidence active",
    "coach.stepRealtimeComplete":
      "Authenticated streaming, rep events, and metadata-only persistence implemented",
    "coach.exerciseMode": "Live exercise",
    "coach.bicepCurl": "Bicep curl",
    "coach.hammerCurl": "Hammer curl",
    "coach.overlayLabel": "Live pose overlay",
    "coach.overlayActive": "Live overlay",
    "coach.overlayWaiting": "Overlay starts with camera",
    "coach.cameraView": "Camera view",
    "coach.setup": "Setup",
    "coach.movement": "Movement",
    "coach.note": "Note",
    "coach.liveAngle": "Joint angle",
    "coach.exercise.bicep_curl": "Bicep curl",
    "coach.exercise.bicep_curl.view":
      "Front or slight side view; show shoulders, elbows, wrists, and hips.",
    "coach.exercise.bicep_curl.setup":
      "Stand tall with the working elbow extended and close to your side.",
    "coach.exercise.bicep_curl.motion":
      "Bend the elbow through a comfortable range, then lower with control.",
    "coach.exercise.bicep_curl.note":
      "Keep the upper arm steady. The camera cannot assess load safety or pain.",
    "coach.exercise.hammer_curl": "Hammer curl",
    "coach.exercise.hammer_curl.view":
      "Front or slight side view with the hand and full working arm visible.",
    "coach.exercise.hammer_curl.setup":
      "Start with the elbow extended and thumb facing upward.",
    "coach.exercise.hammer_curl.motion":
      "Curl while maintaining a neutral hand position, then return slowly.",
    "coach.exercise.hammer_curl.note":
      "Grip orientation is an estimate and may be unavailable when the hand is obscured.",
    "coach.exercise.bodyweight_squat": "Bodyweight squat",
    "coach.exercise.bodyweight_squat.view":
      "Side or front-diagonal view; keep shoulders, hips, knees, and ankles in frame.",
    "coach.exercise.bodyweight_squat.setup":
      "Stand in a comfortable stance with enough clear space around you.",
    "coach.exercise.bodyweight_squat.motion":
      "Lower with control until the knees visibly bend, then return to standing.",
    "coach.exercise.bodyweight_squat.note":
      "Use a stable support if needed. Stop for pain, dizziness, or unusual symptoms.",
    "coach.exercise.shoulder_press": "Shoulder press",
    "coach.exercise.shoulder_press.view":
      "Front or slight diagonal view with both hands visible overhead.",
    "coach.exercise.shoulder_press.setup":
      "Begin with elbows bent and hands near shoulder height.",
    "coach.exercise.shoulder_press.motion":
      "Press upward until the elbows extend, then return with control.",
    "coach.exercise.shoulder_press.note":
      "Practice unloaded or use only a clinician-approved load.",
    "coach.exercise.shoulder_abduction": "Lateral raise",
    "coach.exercise.shoulder_abduction.view":
      "Front view; show both arms and the trunk from hips to hands.",
    "coach.exercise.shoulder_abduction.setup":
      "Stand tall with arms resting by your sides and elbows relaxed.",
    "coach.exercise.shoulder_abduction.motion":
      "Raise the arms outward toward shoulder height, then lower slowly.",
    "coach.exercise.shoulder_abduction.note":
      "Move only through a comfortable range and avoid shrugging toward the ears.",
    "coach.liveReps": "Live reps",
    "coach.livePhase": "Phase",
    "coach.liveGrip": "Grip evidence",
    "coach.liveCue": "Live coaching cue",
    "coach.cue.idle": "Start the camera to begin live rep tracking.",
    "coach.cue.connecting": "Connecting the live counter…",
    "coach.cue.tracking": "Pose tracking is active.",
    "coach.cue.seekingStart":
      "Stand tall and keep your working joints visible.",
    "coach.cue.ready": "Ready — begin the next repetition.",
    "coach.cue.working": "Continue through a comfortable movement range.",
    "coach.cue.returning": "Return to the starting position with control.",
    "coach.cue.saved": "Session complete. The derived summary has been saved.",
    "coach.lastRepAnalysis":
      "Rep {rep} counted · {duration}s · {range}° movement range",
    "coach.loginRequired":
      "Log in before starting an authenticated coaching session. Camera quality and local landmark tracking remain available without streaming.",
    "coach.sessionSaved":
      "The derived session summary was saved. Camera frames and landmark sequences were not retained.",
    "coach.recognitionTitle": "Identify an exercise from video",
    "coach.recognitionDescription":
      "Upload a short movement clip for the temporal model to rank likely exercises. Review and confirm the suggestion before opening an analyzer.",
    "coach.candidateReady": "Temporal candidate ready",
    "coach.recognitionChoose": "Choose a movement video",
    "coach.recognitionSelected": "{size} MB selected",
    "coach.recognitionFormats": "MP4, MOV, AVI, MKV, or WEBM · Maximum 100 MB",
    "coach.recognitionTemporary":
      "The upload is processed temporarily and removed after recognition.",
    "coach.recognitionAction": "Identify exercise",
    "coach.recognitionProcessing": "Identifying",
    "coach.recognitionErrorTitle": "Recognition could not finish",
    "coach.recognitionError":
      "Unable to identify this video. Check the recording and try again.",
    "coach.recognitionEmptyTitle": "Suggestion results appear here",
    "coach.recognitionEmptyText":
      "The model returns its top exercise candidates with confidence. A suggestion does not assess form or safety.",
    "coach.recognitionSuggestion": "Suggested exercise",
    "coach.recognitionConfidence": "Model confidence {confidence}",
    "coach.uncertainBadge": "Low confidence",
    "coach.uncertainTitle": "Choose the exercise manually",
    "coach.uncertainText":
      "Confidence is below the calibrated {threshold} acceptance threshold, so this suggestion cannot be confirmed.",
    "coach.confirmSuggestion": "Confirm {exercise} and continue",
    "coach.confirmingSuggestion": "Recording confirmation",
    "coach.confirmationAuditTitle": "Confirmation could not be recorded",
    "coach.confirmationAuditError":
      "Please try again. The analyzer was not opened because the recognition confirmation was not saved.",
    "coach.noAnalyzerTitle": "Analyzer unavailable",
    "coach.noAnalyzerText":
      "This label can be recognized, but Movena does not have an active coaching analyzer for it.",
  },
  ar: {
    "workspace.stepAnalyze": "نفّذ فحص الحركة",
    "workspace.stepAnalyzeHelp":
      "استخدم ذكاء الحركة من Movena للتمرين المحدد.",
    "workspace.stepPatient": "مراجعة سجل المريض",
    "workspace.stepPatientHelp":
      "اربط السجل المحفوظ وراجعه عندما يدعم سير العمل ذلك.",
    "upload.subjectSwitch":
      "ربما تم تتبع أكثر من شخص. للحصول على موثوقية أفضل، صوّر الشخص المراد تحليله فقط وأبقِ المدرب أو المارة خارج الإطار.",
    "camera.tip.singleSubject": "شخص واحد فقط",
    "camera.tip.singleSubjectText":
      "أبقِ المدربين والمساعدين والمارة خارج الإطار حتى لا ينتقل تتبع الوضعية بين الأشخاص.",
    "upload.identifyInstead": "تعرّف على التمرين من الفيديو",
    "upload.recognitionReadyTitle": "تم تأكيد الاقتراح — الفيديو جاهز",
    "upload.closeIdentification": "إغلاق التعرف",
    "upload.identificationLoading": "جار التحقق من نموذج التعرف",
    "upload.recognitionReadyText":
      "تم اختيار الفيديو نفسه لمحلل {exercise}. راجع الخيارات وابدأ التحليل؛ لا حاجة لاختيار الملف مرة ثانية.",
    "upload.autoRerouteNotice":
      "لم يرصد محلل {selected} المحدد حركة صالحة. اقترح التعرف على الفيديو {suggested} بثقة {confidence}، لذلك حلل Movena الفيديو تلقائيا باستخدام ذلك المحلل.",
    "results.autoRoutedTitle": "تم التعرف على التمرين وتقييمه",
    "results.recognitionReviewTitle":
      "تم التعرف على التمرين — يحتاج إلى مراجعة",
    "language.label": "اللغة",
    "theme.label": "نمط الألوان",
    "theme.light": "فاتح",
    "theme.dark": "داكن",
    "theme.system": "إعداد الجهاز",
    "nav.home": "الرئيسية",
    "nav.exercises": "التمارين",
    "nav.analyze": "التحليل",
    "nav.results": "النتائج",
    "nav.history": "السجل",
    "nav.therapist": "المعالج",
    "nav.coach": "التدريب المباشر",
    "nav.about": "حول",
    "nav.profile": "الملف الشخصي",
    "nav.login": "تسجيل الدخول",
    "nav.admin": "المستخدمون والصلاحيات",
    "nav.workflow": "لوحة العمليات",
    "nav.overview": "نظرة عامة",
    "nav.analyzeMovement": "فحص الحركة",
    "nav.sessions": "مراجعات الحركة",
    "nav.patients": "قائمة المرضى",
    "nav.security": "الملف الشخصي والأمان",
    "nav.collapse": "طي القائمة",
    "nav.expand": "توسيع القائمة",
    "nav.openMenu": "فتح القائمة",
    "nav.skipContent": "انتقل إلى المحتوى",
    "nav.workspace": "المنصة",
    "nav.care": "التأهيل",
    "nav.today": "اليوم",
    "nav.tools": "الإدارة",
    "nav.myRehabilitation": "برنامج التأهيل",
    "nav.exerciseSupport": "دعم التمارين",
    "nav.clinicalWorkspace": "مساحة العمل السريرية",
    "nav.movementReview": "مراجعة الحركة",
    "nav.operations": "التشغيل",
    "nav.platformTools": "أدوات المنصة",
    "nav.progress": "التقدم والنشاط",
    "nav.movementCheck": "فحص الحركة",
    "nav.movementReviews": "مراجعات الحركة",
    "nav.caseload": "قائمة المرضى",
    "nav.recoveryShort": "تدريب التعافي",
    "nav.moreTools": "أدوات إضافية",
    "nav.exerciseLibrary": "مكتبة التمارين",
    "nav.dashboard": "لوحة التحكم",
    "nav.todaysPlan": "خطة اليوم",
    "nav.myExercises": "تماريني",
    "nav.aiExerciseCoach": "مدرب التمارين الذكي",
    "nav.progressReports": "التقدم والتقارير",
    "nav.aiMovementReview": "مراجعة الحركة الذكية",
    "nav.operationsDashboard": "لوحة العمليات",
    "nav.userAdministration": "إدارة المستخدمين",
    "nav.analytics": "التحليلات",
    "nav.movementAnalysis": "تحليل الحركة",
    "nav.rehabPolicy": "دعم قرار التأهيل الذكي",
    "nav.recoveryCoaching": "تدريب التعافي ونمط الحياة",
    "nav.account": "الحساب",
    "role.patient": "مريض",
    "role.therapist": "أخصائي علاج طبيعي",
    "role.admin": "مسؤول النظام",
    "role.superAdmin": "المسؤول الأعلى",
    "role.support": "الدعم",
    "role.user": "مستخدم المنصة",
    "workspace.greeting": "مرحبًا بعودتك، {name}",
    "workspace.subtitle": "تابع نشاط التأهيل وانتقل إلى مهمة الرعاية التالية.",
    "workspace.viewSessions": "مراجعة نشاط الحركة",
    "workspace.recentSessions": "أحدث نشاط للحركة",
    "workspace.patient": "المريض",
    "workspace.recorded": "وقت التسجيل",
    "workspace.assignedPatient": "مريض معيّن",
    "workspace.personalSession": "جلسة شخصية",
    "workspace.viewAllSessions": "عرض كل نشاط الحركة",
    "workspace.status": "جاهزية المنصة",
    "workspace.emailVerified": "تم التحقق من البريد الإلكتروني",
    "workspace.accountAccess": "الوصول إلى الحساب",
    "workspace.accessEnabled": "مفعّل",
    "workspace.protectedAdmin": "مدير عام محمي",
    "workspace.role": "الدور: {role}",
    "workspace.analysisReady": "ذكاء الحركة متاح",
    "workspace.viewSecurity": "عرض الملف الشخصي والأمان",
    "workspace.continueWorkflow": "تابع سير العمل",
    "workspace.stepUpload": "سجّل أداء التمرين",
    "workspace.stepUploadHelp": "استورد فيديو للشخص أثناء أداء التمرين.",
    "workspace.stepReview": "راجع ملاحظات الحركة",
    "workspace.stepReviewHelp":
      "يسلط التحليل المدعوم بالذكاء الاصطناعي الضوء على ملاحظات الحركة للمراجعة.",
    "workspace.stepSave": "احفظ النتائج أو صدّرها",
    "workspace.stepSaveHelp": "احفظ الجلسة أو صدّر النتائج لإعداد التقارير.",
    "brand.tagline": "ذكاء الحركة للتعافي بإرشاد المعالج",
    "footer.product": "تحرّك بشكل أفضل. تعافَ مع فريقك.",
    "footer.disclaimer":
      "هذا التحليل لا يغني عن التقييم أو التشخيص أو العلاج بواسطة مختص مرخص.",
    "status.supported": "مدعوم",
    "status.planned": "مخطط له - غير متاح بعد",
    "status.notAvailable": "غير متاح",
    "status.experimental": "تجريبي",
    "status.recognitionResearch": "بحث التعرف",
    "common.notAvailable": "غير متاح",
    "common.unavailable": "غير متاح",
    "common.unknown": "غير معروف",
    "common.none": "لا يوجد",
    "common.detected": "تم الرصد",
    "common.review": "مراجعة",
    "common.clear": "مسح",
    "common.refresh": "تحديث",
    "common.close": "إغلاق",
    "common.download": "تنزيل",
    "common.exercise": "التمرين",
    "common.status": "الحالة",
    "common.date": "التاريخ",
    "common.score": "النتيجة",
    "common.confidence": "الثقة",
    "common.reps": "التكرارات",
    "common.role": "الدور",
    "common.email": "البريد الإلكتروني",
    "auth.loginIdentifier": "اسم المستخدم أو البريد الإلكتروني",
    "common.password": "كلمة المرور",
    "common.displayName": "اسم العرض",
    "common.username": "اسم المستخدم",
    "common.loading": "جاري التحميل",
    "common.analyzing": "جاري التحليل",
    "common.success": "ناجح",
    "common.rejected": "مرفوض",
    "home.badge": "منصة تأهيل مترابطة",
    "home.titlePrefix": "رعاية تأهيلية",
    "home.titleHighlight": "تبقى متصلة.",
    "home.description":
      "اجمع خطط المعالج ومتابعة التمارين اليومية والمتابعة عن بُعد وذكاء الحركة من Movena في رحلة تأهيل واحدة متصلة.",
    "home.start": "الدخول إلى المنصة",
    "home.accessPlatform": "الدخول إلى المنصة",
    "home.getStarted": "ابدأ الآن",
    "home.openWorkspace": "فتح مساحة الرعاية",
    "home.openAnalyzer": "فتح مساحة الرعاية",
    "home.howNav": "كيف تعمل",
    "home.benefitsNav": "المزايا",
    "home.safetyNav": "السلامة",
    "home.how": "كيف يعمل",
    "home.featureRule": "تأهيل يقوده المعالج",
    "home.featureClaims": "ذكاء مساعد لا يتخذ قرارات علاجية",
    "home.featureUploads": "مراجعة خاصة للحركة",
    "home.exampleEyebrow": "جلسة مثال",
    "home.exampleSummary": "ملخص حركة قائم على القواعد",
    "home.complete": "مكتمل",
    "home.movementScore": "نتيجة الحركة",
    "home.completedReps": "التكرارات المكتملة",
    "home.kneeTrend": "اتجاه زاوية الركبة",
    "home.liveSample": "عينة مباشرة",
    "home.liveAnalysis": "تحليل مباشر",
    "home.poseTracking": "تتبّع الوضعية",
    "home.kneeAngle": "الركبة 92°",
    "home.liveMeasurements": "قياسات المفاصل المباشرة",
    "home.kneeLabel": "الركبة",
    "home.hipLabel": "الورك",
    "home.trunkLabel": "الجذع",
    "home.pauseDemo": "إيقاف محاكاة الحركة",
    "home.playDemo": "تشغيل محاكاة الحركة",
    "home.angleTrends": "اتجاهات الزوايا",
    "home.clearFeedback": "ملاحظات واضحة",
    "home.pdfExport": "تقارير قابلة للمشاركة",
    "home.benefitsTitle": "رحلة تأهيل واحدة من الخطة إلى المتابعة.",
    "home.benefitTrends":
      "اربط الالتزام اليومي والألم ونشاط الحركة بخطة التأهيل.",
    "home.benefitFeedback":
      "حافظ على وضوح التواصل بين المريض والمعالج عبر تسجيلات وملاحظات حركة سهلة.",
    "home.benefitReports": "حوّل نشاط التأهيل إلى ملخصات تقدم يراجعها المختص.",
    "home.howEyebrow": "كيف يعمل",
    "home.howTitle": "مسار متصل من الخطة إلى التقدم",
    "home.howDescription":
      "تقود خطة الرعاية التجربة، ويدعم Movena اللحظات التي تفيد فيها أدلة الحركة.",
    "home.stepUploadTitle": "اتبع خطة اليوم",
    "home.stepUploadDescription":
      "اطّلع على الجرعة والتعليمات والاحتياطات ومهمة الرعاية التالية.",
    "home.stepReviewTitle": "أكمل فحص حركة موجّهًا",
    "home.stepReviewDescription":
      "عند طلب المعالج، يقدّر Movena التكرارات والزوايا وملاحظات الحركة.",
    "home.stepDiscussTitle": "شارك تقدمك مع المعالج",
    "home.stepDiscussDescription":
      "اجمع التسجيلات اليومية وأدلة الحركة للمراجعة المهنية والمتابعة.",
    "home.safetyEyebrow": "حد مهم للسلامة",
    "home.safetyTitle": "مصمم لدعم النقاش، لا لاستبدال الرعاية السريرية.",
    "home.safetyDescription":
      "النتائج تقديرات تعليمية ولا يجوز استخدامها للتشخيص أو قرارات العلاج أو إرشادات الطوارئ.",
    "home.analyzeVideo": "حلل فيديو",
    "upload.eyebrow": "محلل الحركة",
    "upload.title": "ارفع فيديو حركة",
    "upload.description":
      "اختر تسجيلا واضحا لمحلل {exercise} القائم على القواعد.",
    "upload.patientEyebrow": "دعم التمارين",
    "upload.patientTitle": "مدرب التمارين الذكي",
    "upload.patientDescription":
      "سجّل أو ارفع التمرين الموصوف لك للحصول على ملاحظات حركة مدعومة بالذكاء الاصطناعي.",
    "upload.reviewEyebrow": "مراجعة الحركة",
    "upload.reviewTitle": "تحليل الحركة",
    "upload.reviewDescription":
      "ارفع فيديو لتمرين {exercise} لمراجعته بمساعدة الذكاء الاصطناعي.",
    "upload.advancedOptions": "خيارات متقدمة",
    "upload.exerciseHelp":
      "اختر الحركة الظاهرة في التسجيل. يظل الاختيار اليدوي هو الأساس.",
    "upload.supportedGroup": "مدعوم",
    "upload.plannedGroup": "مخطط له - غير متاح بعد",
    "upload.recommendedView": "زاوية التصوير الموصى بها",
    "upload.requiredVisibility": "الأجزاء المطلوب ظهورها",
    "upload.instruction": "التعليمات",
    "upload.safety": "السلامة",
    "upload.cardTitle": "رفع فيديو {exercise}",
    "upload.fileTypes":
      "MP4 أو MOV أو AVI أو MKV أو WEBM · الحد الأقصى 100 ميجابايت",
    "upload.drag": "اسحب وأسقط فيديو {exercise}",
    "upload.browse": "أو اضغط لاختيار ملف",
    "upload.selected": "تم اختيار {size} ميجابايت",
    "upload.chooseVideo": "اختر فيديو تمرين {exercise}",
    "upload.errorTitle": "تعذر بدء التحليل",
    "upload.warningTitle": "راجع التحذير قبل المتابعة",
    "upload.subjectSwitchOverrideHelp":
      "تابع فقط إذا كان التسجيل ما زال يتبع الشخص المقصود بوضوح. سيتضمن التقرير هذا التحذير للمراجعة اليدوية.",
    "upload.subjectSwitchAutoProceed":
      "تتم المتابعة تلقائيا مع تضمين هذا التحذير في التقرير.",
    "upload.proceedWithWarning": "المتابعة مع التحذير",
    "upload.temporary": "تتم معالجة الملفات مؤقتا ولا تعد سجلات مرضى.",
    "upload.analyze": "حلل {exercise}",
    "upload.analyzeMovement": "حلل الحركة",
    "upload.cancelAnalysis": "إلغاء التحليل",
    "upload.cancelled": "تم إلغاء التحليل. يظل الفيديو المختار محفوظًا.",
    "upload.movement": "الحركة",
    "upload.chooseExercise": "اختر تمرينًا",
    "upload.pickerEyebrow": "اختيار التمرين",
    "upload.pickerTitle": "ما التمرين الظاهر؟",
    "upload.pickerDescription":
      "اختر الحركة الظاهرة في الفيديو ليطبق Movena التحليل الصحيح. سيظل الفيديو المختار محفوظًا.",
    "upload.noExerciseTitle": "اختر تمرينًا قبل التحليل",
    "upload.noExerciseDescription":
      "اختر من الحركات المدعومة الآن، أو ارفع الفيديو أولًا وسنطلب منك الاختيار قبل التحليل.",
    "upload.progressProcessing": "جاري معالجة الحركة...",
    "upload.progressUploading": "جاري رفع الفيديو...",
    "upload.progressHelp":
      "أبق هذه الصفحة مفتوحة أثناء تجهيز نقاط الوضع والملفات المختارة.",
    "upload.noFile": "اختر فيديو قبل بدء التحليل.",
    "upload.loginRequired": "يرجى تسجيل الدخول قبل تحليل الفيديو.",
    "upload.unsupported":
      "صيغة الفيديو غير مدعومة. يرجى رفع MP4 أو MOV أو AVI أو MKV أو WEBM.",
    "upload.network": "تعذر الاتصال بخادم التحليل.",
    "upload.timeout":
      "استغرق التحليل وقتًا أطول من اتصال الخدمة السحابية. يظل الفيديو المختار محفوظًا؛ أعد المحاولة بعد تعطيل الملفات الاختيارية.",
    "upload.genericError":
      "تعذر تحليل هذا الفيديو. تحقق من الخادم الخلفي وحاول مرة أخرى.",
    "upload.qualityTitle": "فحص جودة التسجيل",
    "upload.qualityChecking": "جارٍ فحص جودة التسجيل…",
    "upload.qualityLocal":
      "يعمل الفحص محليًا داخل متصفحك ولا يتم رفع الفيديو بسببه.",
    "upload.qualityUnavailable": "الفحص التلقائي للجودة غير متاح",
    "upload.qualityUnavailableHelp":
      "يمكنك المتابعة، لكن راجع التسجيل يدويًا قبل التحليل.",
    "upload.quality.pass": "التسجيل يبدو جاهزًا",
    "upload.quality.warn": "راجع التسجيل",
    "upload.quality.fail": "اختر تسجيلًا أوضح",
    "upload.qualityBadge.pass": "جاهز",
    "upload.qualityBadge.warn": "مراجعة",
    "upload.qualityBadge.fail": "يلزم إجراء",
    "upload.qualityCheck.duration": "المدة",
    "upload.qualityCheck.resolution": "الدقة",
    "upload.qualityCheck.framing": "شكل الإطار",
    "upload.qualityCheck.lighting": "تقدير الإضاءة",
    "upload.qualityCheck.motion": "الحركة الظاهرة",
    "upload.qualityBlockingHelp":
      "التسجيل قصير جدًا أو منخفض الدقة بما لا يسمح بمعالجة موثوقة. اختر فيديو آخر للمتابعة.",
    "upload.qualityWarningHelp":
      "يظل التحليل متاحًا. تأكد من وضوح الشخص والمفاصل المطلوبة طوال الحركة.",
    "options.title": "خيارات التحليل",
    "options.description":
      "اختر الملفات والتفاصيل الاختيارية. التحليل القائم على القواعد يعمل دائما.",
    "options.selectAll": "تحديد الكل",
    "options.clearAll": "إلغاء تحديد الكل",
    "options.overlayTitle": "فيديو مع تعليقات مرئية",
    "options.overlayDescription": "رسم طبقة وضعية للمراجعة الحركية.",
    "options.reportTitle": "تقرير جلسة PDF",
    "options.reportDescription": "إنشاء تقرير مؤقت قابل للتنزيل.",
    "options.frameDataTitle": "بيانات اتجاه الزوايا",
    "options.frameDataDescription":
      "تضمين عينات زوايا على مستوى الإطارات للرسوم.",
    "options.mlTitle": "رأي ثان من نموذج تعلم آلي",
    "options.mlDescription":
      "طلب رأي ثان تجريبي اختياري عند توفر مزود نموذج مهيأ.",
    "options.saveTitle": "حفظ سجل الجلسة",
    "options.saveDescription": "احفظ هذا التحليل في سجل جلساتك المحمي.",
    "options.mlUnavailable":
      "لا يتوفر نموذج تعلم آلي لتمرين {exercise}؛ يبقى التحليل القائم على القواعد هو الأساس.",
    "options.modelReady": "جاهز",
    "options.modelUnavailable": "غير متاح",
    "camera.recordingTips": "نصائح التسجيل",
    "camera.title": "دليل وضع الكاميرا",
    "camera.visible": "حافظ على ظهور {landmarks}.",
    "camera.frame":
      "اجعل العدسة قريبة من منطقة الحركة وكل المفاصل المطلوبة داخل الإطار.",
    "camera.lighting":
      "استخدم إضاءة جيدة وتجنب الإضاءة الخلفية القوية والخلفيات المتحركة.",
    "camera.checklist": "قائمة التحقق من الظهور",
    "camera.tip.side": "تصوير جانبي",
    "camera.tip.sideSquat": "الأفضل لمراجعة عمق القرفصاء وميل الجذع.",
    "camera.tip.front": "تصوير أمامي",
    "camera.tip.frontSquat": "الأفضل لمراجعة احتمال انحراف الركبة للداخل.",
    "camera.tip.fullBody": "ظهور الجسم بالكامل",
    "camera.tip.fullBodyText":
      "أبق الكتفين والوركين والركبتين والكاحلين والقدمين داخل الإطار.",
    "camera.tip.stableBright": "ثبات وإضاءة جيدة",
    "camera.tip.stableBrightText": "استخدم موضع كاميرا ثابتا مع إضاءة متساوية.",
    "camera.tip.reps": "سجل 3-5 تكرارات",
    "camera.tip.repsText": "تحرك بوتيرة مريحة ومضبوطة عندما يكون ذلك آمنا.",
    "camera.tip.clearJoint": "وضوح حدود المفاصل",
    "camera.tip.clearJointText": "تجنب الملابس الواسعة جدا قدر الإمكان.",
    "camera.tip.chairView": "تصوير جانبي أو مائل",
    "camera.tip.chairViewText":
      "ضع الهاتف على سطح ثابت بجانب الكرسي عند الإمكان.",
    "camera.tip.bodyChair": "ظهور الجسم والكرسي",
    "camera.tip.bodyChairText":
      "أظهر الجسم بالكامل أو على الأقل الكتفين والوركين والركبتين والكاحلين والكرسي.",
    "camera.tip.stableChair": "استخدم كرسيا ثابتا",
    "camera.tip.stableChairText": "تأكد من ثبات الكرسي قبل التسجيل.",
    "camera.tip.chairRepsText":
      "أظهر دورات كاملة من الجلوس والقيام والوقوف والنزول والعودة إلى الجلوس.",
    "camera.tip.stop": "توقف عند الحاجة",
    "camera.tip.stopText": "توقف إذا شعرت بألم أو دوخة أو انزعاج غير معتاد.",
    "camera.tip.kneeViewText":
      "ضع الكاميرا بجانب الساق التي تتمرن بحيث يبقى الورك والركبة والكاحل ظاهرين.",
    "camera.tip.seated": "ظهور وضع الجلوس",
    "camera.tip.seatedText": "أظهر الكرسي والفخذ والساق والقدم طوال التسجيل.",
    "camera.tip.secureChair": "كرسي ثابت",
    "camera.tip.kneeStableText":
      "استخدم إضاءة متساوية وتجنب الملابس التي تخفي حدود الركبة.",
    "camera.tip.kneeRepsText":
      "ابدأ والركبة مثنية، ثم مدها براحة، ثم عد إلى وضع البداية.",
    "camera.tip.shoulderViewText":
      "ضع الكاميرا أمامك بحيث يبقى الكتف والمرفق والمعصم والجذع ظاهرين.",
    "camera.tip.pushUpSideText":
      "ضع الكاميرا من الجانب بحيث يبقى خط الكتف والمرفق والمعصم والورك والكاحل ظاهرا.",
    "camera.tip.pushUpSupportText":
      "استخدم أرضية أو سطح دعم ثابت واختر مستوى دعم مناسبا.",
    "camera.tip.pushUpRepsText":
      "ابدأ في وضع الدعم، واثن المرفقين ضمن مدى مريح، ثم مدهما وكرر بتحكم.",
    "camera.tip.pressViewText":
      "ضع الكاميرا أمامك أو بزاوية بسيطة بحيث تبقى الذراعان والجذع ظاهرين فوق الرأس.",
    "camera.tip.pressPostureText":
      "ثبت الكاميرا وأبق الجذع ظاهرا طوال الحركة فوق الرأس.",
    "camera.tip.pressRepsText":
      "ابدأ والمرفقان مثنيان، ثم مد الذراعين فوق الرأس وعد إلى وضع البداية الظاهر بتحكم.",
    "camera.tip.curlViewText":
      "ضع الكاميرا أمامك أو إلى الجانب بزاوية بسيطة بحيث يبقى الكتف والمرفق والمعصم والجذع ظاهرين.",
    "camera.tip.curlPostureText":
      "أبق الجذع والعضد ظاهرين؛ لا تستطيع وضعية الجسم التحقق من اتجاه القبضة أو المقاومة.",
    "camera.tip.curlRepsText":
      "ابدأ والمرفق ممدودا، ثم اثنه ضمن مدى مريح، وعد إلى المد بتحكم.",
    "camera.tip.hammerStableText":
      "استخدم إضاءة متساوية وأبق اليد ظاهرة عند الإمكان؛ قد يبقى اتجاه القبضة غير متاح.",
    "camera.tip.hammerRepsText":
      "اثن المرفق مع وضع يد محايد عندما يكون مرئيا، ثم عد إلى المد بتحكم.",
    "camera.tip.flexionViewText":
      "ضع الكاميرا أمامك أو إلى الجانب بزاوية بسيطة بحيث يبقى الكتف والمرفق والمعصم والجذع ظاهرين.",
    "camera.tip.flexionPostureText":
      "قف منتصبا مع ثبات الجذع وابدأ والذراع قرب الجانب.",
    "camera.tip.flexionRepsText":
      "ابدأ والذراع قرب الجانب، ارفعه إلى الأمام براحة، ثم أعده.",
    "camera.tip.upperBody": "ظهور الجزء العلوي من الجسم",
    "camera.tip.upperBodyText": "أبق الكتفين والذراعين والوركين داخل الإطار.",
    "camera.tip.stablePosture": "وضعية ثابتة",
    "camera.tip.armStableText":
      "استخدم إضاءة متساوية وملابس لا تخفي حدود الذراع.",
    "camera.tip.shoulderRepsText":
      "ابدأ والذراع قرب الجانب، ارفعه للخارج براحة، ثم أعده.",
    "camera.tip.shoulderStopText":
      "توقف إذا شعرت بألم أو دوخة أو خدر أو انزعاج غير معتاد.",
    "camera.tip.hipViewText":
      "ضع الكاميرا أمامك بحيث يبقى الحوض والورك والركبة والكاحل والجذع ظاهرين.",
    "camera.tip.lowerBody": "ظهور الجزء السفلي بالكامل",
    "camera.tip.lowerBodyText":
      "أبق الوركين والساق المتحركة داخل الإطار من الحوض إلى القدم.",
    "camera.tip.stableSupport": "دعم ثابت",
    "camera.tip.hipStableText":
      "استخدم إضاءة متساوية وملابس لا تخفي حدود الورك والساق.",
    "camera.tip.hipRepsText":
      "ابدأ من وضع قريب من الحياد، حرك ساقا واحدة للخارج براحة، ثم أعدها.",
    "camera.tip.gaitSideText":
      "ضع الكاميرا من الجانب بحيث يمكن تتبع الساقين أثناء المشي عبر الإطار.",
    "camera.tip.gaitLowerBodyText":
      "أبق الوركين والركبتين والكاحلين والكعبين وأصابع القدم ظاهرين للساقين.",
    "camera.tip.clearPath": "مسار واضح",
    "camera.tip.clearPathText":
      "استخدم مسارا خاليا من العوائق مع مساحة كافية لعدة خطوات مريحة.",
    "camera.tip.steps": "سجل عدة خطوات",
    "camera.tip.gaitStepsText":
      "التقط مرورا ثابتا للمشي مع دورتين على الأقل للجانب نفسه عندما يكون ذلك آمنا.",
    "camera.tip.gaitStableText":
      "استخدم موضع كاميرا ثابت وإضاءة متساوية وقلل ضبابية الحركة.",
    "camera.tip.gaitStopText":
      "توقف إذا شعرت بألم أو دوخة أو فقدان توازن أو انزعاج غير معتاد.",
    "camera.tip.balanceViewText":
      "ضع الكاميرا من الأمام أو بزاوية بسيطة بحيث يبقى الجذع والحوض والساقان والقدمان ظاهرين.",
    "camera.tip.balanceFullBodyText":
      "أبق الكتفين والوركين والركبتين والكاحلين والكعبين وأصابع القدم داخل الإطار طوال الثبات.",
    "camera.tip.balanceSupportText":
      "أبق سطحا ثابتا مثل كرسي أو حاجز قريب دون حجب الجسم.",
    "camera.tip.hold": "اثبت بهدوء",
    "camera.tip.balanceHoldText":
      "التقط عدة ثوان من وضع توازن آمن دون خطوات عند الإمكان.",
    "camera.tip.balanceStableText":
      "استخدم موضع كاميرا ثابت وإضاءة متساوية مع تقليل حركة الخلفية.",
    "camera.tip.balanceStopText":
      "توقف إذا شعرت بألم أو دوخة أو فقدان توازن أو انزعاج غير معتاد.",
    "exercises.eyebrow": "مكتبة التمارين",
    "exercises.title": "مكتبة التمارين",
    "exercises.description":
      "اختر تمرينا لمراجعة حركتك.",
    "exercises.researchTitle": "توسع التدريب على التمارين قيد البحث",
    "exercises.researchDescription":
      "تم تنفيذ إعداد بيانات الوضعية ومسار XGBoost للتعرف. تستخدم تمارين الضغط وضغط الكتف وثني الذراع وتمرين المطرقة وثني الكتف مسارات تحليل محافظة مع قيود الوضعية المرئية.",
    "exercises.researchBadge": "اقتراح فقط",
    "exercises.search": "بحث في التمارين",
    "exercises.posePreview": "رسم توضيحي للحركة",
    "exercises.searchPlaceholder":
      "ابحث حسب الحركة أو المنطقة أو زاوية الكاميرا",
    "exercises.availability": "الإتاحة",
    "exercises.allAvailability": "كل حالات الإتاحة",
    "exercises.supportedOnly": "المدعومة فقط",
    "exercises.plannedOnly": "المخطط لها فقط",
    "exercises.bodyRegion": "منطقة الجسم",
    "exercises.allRegions": "كل مناطق الجسم",
    "exercises.clearFilters": "مسح عوامل التصفية",
    "exercises.researchAndPlanned": "البحث والتمارين المخطط لها",
    "exercises.pages": "صفحات التمارين",
    "exercises.next": "التمارين التالية",
    "exercises.previous": "التمارين السابقة",
    "exercises.matchCount": "{count} {label} {verb} عوامل التصفية.",
    "exercises.matchVerbSingular": "يطابق",
    "exercises.matchVerbPlural": "تطابق",
    "exercises.matchSingular": "تمرين",
    "exercises.matchPlural": "تمارين",
    "exercises.noMatch": "لا توجد تمارين مطابقة",
    "exercises.noMatchDescription": "امسح عوامل التصفية أو جرب عبارة بحث أوسع.",
    "exercises.supportedTitle": "التمارين المدعومة",
    "exercises.supportedDescription":
      "متاحة الآن لتحليل الفيديو القائم على القواعد.",
    "exercises.availableCount": "{count} متاح",
    "exercises.noSupported": "لا توجد تمارين مدعومة في هذا العرض",
    "exercises.adjustSupported": "عدل عوامل التصفية لتضمين المحللات المتاحة.",
    "exercises.plannedTitle": "التمارين المخطط لها",
    "exercises.plannedDescription":
      "تغطية ضمن خارطة الطريق فقط؛ هذه المحللات غير مفعلة.",
    "exercises.plannedCount": "{count} مخطط له",
    "exercises.noPlanned": "لا توجد تمارين مخطط لها في هذا العرض",
    "exercises.adjustPlanned": "عدل عوامل التصفية لتضمين تمارين خارطة الطريق.",
    "exercises.analyzeThis": "حلل هذا التمرين",
    "exercises.startExercise": "ابدأ التمرين",
    "exercises.reviewExercise": "عرض وتحليل",
    "auth.loginEyebrow": "مرحبا بعودتك",
    "auth.loginTitle": "تسجيل الدخول إلى Movena",
    "auth.loginDescription": "استخدم حسابك للوصول الآمن إلى المنصة.",
    "auth.warning":
      "احم خصوصية المرضى. أدخل فقط المعلومات المصرح لك بمعالجتها واتبع سياسات الموافقة والتعامل مع البيانات في مؤسستك.",
    "auth.sideEyebrow": "وصول آمن إلى المنصة",
    "auth.sideTitle": "تابع مساحة مراجعة الحركة الخاصة بك.",
    "auth.sideDescription":
      "ادخل إلى الجلسات المحفوظة وأدوات تحليل التمارين وواجهات المراجعة الموجهة للمعالج.",
    "auth.sideWarning":
      "استخدم Movena وفقا لسياسات الخصوصية والموافقة والاحتفاظ بالسجلات في مؤسستك.",
    "auth.expired": "ربما انتهت جلستك. يرجى تسجيل الدخول مرة أخرى.",
    "auth.invalid":
      "يرجى التحقق من اسم المستخدم/البريد الإلكتروني وكلمة المرور.",
    "auth.network":
      "تعذر الوصول إلى خادم تسجيل الدخول. تأكد من تشغيل الخادم ثم حاول مرة أخرى.",
    "auth.unavailable": "تسجيل الدخول غير متاح مؤقتًا.",
    "auth.loggingIn": "جاري تسجيل الدخول...",
    "auth.login": "تسجيل الدخول",
    "auth.needAccount": "تحتاج إلى حساب؟",
    "auth.createOne": "أنشئ واحدا",
    "auth.backToLogin": "العودة إلى تسجيل الدخول",
    "auth.registerBadge": "وصول آمن إلى المنصة",
    "auth.registerTitle": "إنشاء حسابك",
    "auth.registerDescription": "أنشئ مساحة عملك الآمنة على Movena.",
    "auth.created": "تم إنشاء الحساب. يمكنك تسجيل الدخول فورًا.",
    "auth.registerFailed": "فشل التسجيل.",
    "auth.displayPlaceholder": "اسمك",
    "auth.usernamePlaceholder": "your.username",
    "auth.usernameHelp":
      "استخدم من 3 إلى 64 حرفًا أو رقمًا أو نقطة أو شرطة أو شرطة سفلية. يمكنك استخدام اسم المستخدم لتسجيل الدخول.",
    "auth.passwordHelp": "استخدم 8 أحرف على الأقل.",
    "auth.acceptTerms":
      "أوافق على شروط الاستخدام وأفهم أن المنصة لا تستبدل الحكم الطبي.",
    "auth.acceptPrivacy":
      "قرأت سياسة الخصوصية وأوافق عليها وعلى معالجة بيانات الرعاية الخاصة بي.",
    "auth.creating": "جاري إنشاء الحساب...",
    "auth.createAccount": "إنشاء الحساب",
    "auth.forgotPassword": "هل نسيت كلمة المرور؟",
    "auth.resendVerification": "إعادة إرسال التحقق",
    "auth.managedAccessHelp":
      "يدير المسؤول الأعلى التحقق من البريد واستعادة الحساب مؤقتًا.",
    "profile.title": "الملف الشخصي",
    "profile.developmentUser": "مستخدم Movena",
    "profile.logout": "تسجيل الخروج",
    "profile.workflowDescription":
      "راقب رحلة الرعاية والاستثناءات التشغيلية وطلبات الخصوصية وسجل التدقيق من واجهة واحدة منزوعة الهوية.",
    "profile.openWorkflow": "فتح لوحة العمليات",
    "workflow.eyebrow": "عمليات المسؤول الأعلى",
    "workflow.title": "لوحة العمليات",
    "workflow.description":
      "راقب رحلة الرعاية كاملة، واكتشف الاستثناءات التشغيلية، ونسّق المتابعة المسؤولة دون كشف التفاصيل السريرية.",
    "workflow.metrics": "مؤشرات المنصة",
    "workflow.metric.users": "إجمالي المستخدمين",
    "workflow.metric.patients": "المرضى",
    "workflow.metric.active_assignments": "الإسنادات النشطة",
    "workflow.metric.appointments": "المواعيد",
    "workflow.metric.paid_orders": "الطلبات المدفوعة",
    "workflow.railTitle": "سير تقديم الرعاية",
    "workflow.railDescription": "الحالة التشغيلية المباشرة عبر رحلة المريض",
    "workflow.stage.account_consent": "الحساب والموافقة",
    "workflow.stage.therapist_assignment": "إسناد المعالج",
    "workflow.stage.care_plan": "خطة الرعاية",
    "workflow.stage.appointment": "الموعد",
    "workflow.stage.payment": "الدفع",
    "workflow.stage.follow_up": "المتابعة",
    "workflow.total": "إجمالي",
    "workflow.onTrack": "على المسار",
    "workflow.needAttention": "تحتاج متابعة",
    "workflow.attentionQueue": "تحتاج إلى متابعة",
    "workflow.deidentified": "مراجع تشغيلية منزوعة الهوية فقط",
    "workflow.type": "نوع سير العمل",
    "workflow.type.privacy_request": "طلب خصوصية",
    "workflow.type.assignment": "إسناد",
    "workflow.type.care_plan": "خطة رعاية",
    "workflow.type.appointment": "موعد",
    "workflow.type.payment": "دفع",
    "workflow.type.password_recovery": "استعادة كلمة المرور",
    "workflow.allWorkflows": "كل مسارات العمل",
    "workflow.allPriorities": "كل الأولويات",
    "workflow.priority": "الأولوية",
    "workflow.priority.high": "عالية",
    "workflow.priority.medium": "متوسطة",
    "workflow.priority.low": "منخفضة",
    "workflow.workflow": "سير العمل",
    "workflow.reference": "المرجع",
    "workflow.owner": "المسؤول",
    "workflow.age": "المدة",
    "workflow.action": "الإجراء",
    "workflow.review": "مراجعة",
    "workflow.reviewing": "تتم مراجعة",
    "workflow.queueEmpty": "لا توجد استثناءات مطابقة",
    "workflow.queueEmptyDescription": "جرّب مرشحًا آخر أو حدّث لقطة سير العمل.",
    "workflow.today": "اليوم بتوقيت القاهرة",
    "workflow.appointments": "المواعيد",
    "workflow.paymentExceptions": "استثناءات الدفع",
    "workflow.pending_orders": "طلبات معلقة",
    "workflow.failed_payments": "مدفوعات فاشلة",
    "workflow.pending_refunds": "مبالغ مستردة معلقة",
    "workflow.privacyRequests": "طلبات الخصوصية",
    "workflow.pending": "معلقة",
    "workflow.export": "تصدير",
    "workflow.correction": "تصحيح",
    "workflow.deletion": "حذف",
    "workflow.recentAudit": "أحدث نشاطات التدقيق",
    "workflow.auditDescription": "التغييرات التشغيلية الحساسة مسجلة للمساءلة",
    "workflow.actor": "المنفذ",
    "workflow.event": "الحدث",
    "workflow.resource": "المورد",
    "workflow.when": "توقيت القاهرة",
    "workflow.noAudit": "لا يوجد نشاط تدقيق بعد",
    "workflow.refresh": "تحديث",
    "workflow.manageUsers": "إدارة المستخدمين",
    "workflow.generatedAt": "آخر تحديث",
    "workflow.loading": "جارٍ تحميل سير العمل…",
    "workflow.loadError": "تعذر تحميل لقطة سير العمل.",
    "workflow.tryAgain": "إعادة المحاولة",
    "results.emptyTitle": "لا توجد نتائج تحليل بعد",
    "results.emptyDescription":
      "ارفع فيديو تمرين مدعوم لإنشاء لوحة تحليل الحركة.",
    "results.goAnalyze": "الانتقال إلى التحليل",
    "results.rejectedEyebrow": "تم رفض التسجيل",
    "results.completeEyebrow": "اكتمل التحليل",
    "results.rejectedTitle": "تعذر تقييم تسجيل {exercise}",
    "results.reportTitle": "تقرير {exercise}",
    "results.rejectedDescription":
      "راجع إرشادات التسجيل وحاول مرة أخرى بتسلسل كامل لحركة {movement}.",
    "results.completeDescription":
      "راجع مؤشرات الحركة والأدلة المرئية والملاحظات والقيود المعروفة من هذه الجلسة.",
    "results.savedSession": "جلسة محفوظة",
    "results.sessionStored": "الجلسة {session} · محفوظة في سجل جلساتك",
    "results.viewHistory": "عرض سجل الجلسات",
    "results.continueCheckIn": "متابعة تسجيل التمرين",
    "results.metrics": "المؤشرات الرئيسية للتحليل",
    "results.movementScore": "نتيجة الحركة",
    "results.analysisConfidence": "ثقة التحليل",
    "results.totalReps": "إجمالي التكرارات",
    "results.averageKnee": "متوسط الركبة",
    "results.averageHip": "متوسط الورك",
    "results.averageTrunk": "متوسط الجذع",
    "results.averageShoulder": "متوسط الكتف",
    "results.averageElbow": "متوسط المرفق",
    "results.averageHipAbduction": "متوسط إبعاد الورك",
    "results.gaitCadence": "الإيقاع",
    "results.gaitCycles": "دورات المشي",
    "results.gaitStanceSwing": "الوقوف / التأرجح",
    "results.gaitSymmetry": "التناظر الزمني",
    "results.gaitStrideVariability": "تغير زمن الخطوة",
    "results.gaitKneeRange": "مدى الركبة",
    "results.balanceDuration": "مدة الثبات",
    "results.balanceMode": "وضعية الثبات",
    "results.balanceSway": "جذر متوسط التأرجح",
    "results.balanceVelocity": "سرعة التأرجح",
    "results.balanceTrunkLean": "أقصى ميل للجذع",
    "results.unitStepsMin": "خطوة/دقيقة",
    "results.unitSeconds": "ثانية",
    "results.unitNormalized": "معياري",
    "results.unitPercent": "%",
    "results.detectedIssues": "الملاحظات المرصودة",
    "results.reliability": "الموثوقية",
    "results.confidenceLabel": "ثقة {level}",
    "results.repCountConfidence": "ثقة عد التكرارات",
    "results.partialIgnored": "تم تجاهل {count} {cycle} جزئي",
    "results.cycleSingular": "دورة",
    "results.cyclePlural": "دورات",
    "results.poseQuality": "جودة الوضعية",
    "results.framesDetected": "{level} · رصد {rate}% من الإطارات",
    "results.qualityNotMeasured": "لم يتم قياس جودة التسجيل.",
    "results.reviewQuality": "راجع جودة التسجيل",
    "results.noConfidenceWarnings": "لم ترجع تحذيرات إضافية للثقة.",
    "results.explainableScore": "نتيجة قابلة للتفسير",
    "results.scoreBreakdown": "تفصيل النتيجة",
    "results.breakdown.completion": "الإكمال",
    "results.breakdown.movementControl": "التحكم في الحركة",
    "results.breakdown.trunkControl": "التحكم في الجذع",
    "results.breakdown.consistency": "الثبات",
    "results.breakdown.poseConfidence": "ثقة الوضعية",
    "results.breakdown.extensionRange": "مدى المد",
    "results.breakdown.flexionRange": "مدى الثني",
    "results.breakdown.visibility": "الظهور",
    "results.breakdown.repCompletion": "إكمال التكرار",
    "results.breakdown.abductionRange": "مدى الإبعاد",
    "results.breakdown.depth": "العمق",
    "results.breakdown.kneeAlignment": "محاذاة الركبة",
    "results.breakdown.pelvisTrunkStability": "ثبات الحوض/الجذع",
    "results.breakdown.gaitPhase": "توقيت مراحل المشي",
    "results.breakdown.cadence": "الإيقاع",
    "results.breakdown.symmetry": "التناظر الزمني",
    "results.breakdown.strideConsistency": "ثبات زمن الخطوة",
    "results.breakdown.kinematicRange": "مدى الحركة",
    "results.breakdown.holdDuration": "مدة الثبات",
    "results.breakdown.swayControl": "التحكم في التأرجح",
    "results.breakdown.pelvisControl": "تحكم الحوض",
    "results.breakdown.kneeStability": "ثبات الركبة",
    "results.unitDegrees": "درجة",
    "results.breakdownUnavailable": "تفصيل النتيجة غير متاح",
    "results.breakdownOlder": "استخدم هذا التحليل استجابة API أقدم.",
    "results.repReview": "مراجعة عد التكرارات",
    "results.manualReview": "يوصى بالمراجعة اليدوية",
    "results.lowConfidenceText":
      "تم رصد الحركة، لكن ثقة عد التكرارات منخفضة بسبب تتبع وضعية مشوش أو ظهور غير ثابت.",
    "results.partialText":
      "تم تجاهل {count} {cycle} حركة غير مكتملة ولم يتغير عدد التكرارات المكتملة.",
    "results.trimSquat":
      "راجع إعداد الكاميرا وفكر في قص الفيديو ليشمل مجموعة القرفصاء فقط.",
    "results.trimExercise":
      "راجع إعداد الكاميرا وفكر في قص الفيديو ليشمل مجموعة التمرين المسجلة فقط.",
    "results.sessionOverview": "نظرة عامة على الجلسة",
    "results.observationCount": "{count} {label}",
    "results.observationSingular": "ملاحظة",
    "results.observationPlural": "ملاحظات",
    "results.noMajorFlags": "لا توجد إشارات رئيسية",
    "results.scoreDisclaimer":
      "ملخص جلسة قائم على القواعد، وليس تشخيصا أو مقياس نتيجة سريرية.",
    "results.videoReview": "مراجعة الفيديو",
    "results.videoReviewHelp": "قارن التسجيل الأصلي بطبقة الوضعية الناتجة.",
    "results.originalUpload": "الرفع الأصلي",
    "results.annotatedPreview": "معاينة الحركة المعلّمة",
    "results.originalPreviewUnavailable": "المعاينة الأصلية غير متاحة",
    "results.originalPreviewHelp":
      "المعاينات المحلية متاحة مباشرة بعد الرفع في جلسة المتصفح هذه.",
    "results.annotatedLoadFailed": "تعذر تحميل المعاينة المعلّمة",
    "results.annotatedNotGenerated": "لم يتم إنشاء معاينة معلّمة لهذا التحليل.",
    "results.loadingAnnotated": "جارٍ تجهيز المعاينة المعلّمة",
    "results.retryPreview": "إعادة محاولة المعاينة",
    "results.artifactExpired":
      "ربما انتهت صلاحية الملف المؤقت. أعد التحليل لإنشاء طبقة جديدة.",
    "results.enableOverlay":
      "فعّل خيار الفيديو المعلّم في صفحة الرفع لطلب طبقة هيكل ثنائية الأبعاد تجريبية.",
    "results.videoUnsupported": "متصفحك لا يدعم تشغيل الفيديو.",
    "results.overlayHelp":
      "طبقة ثنائية الأبعاد تجريبية؛ قد تتحرك العلامات وتسميات المراحل مع الحجب أو ضبابية الحركة أو زاوية الكاميرا.",
    "results.noIssues": "لم ترصد القواعد الحالية مشكلات حركة رئيسية.",
    "results.summaryFeedback": "الملخص والملاحظات",
    "results.noSummary": "لم يرجع ملخص.",
    "results.correctiveFeedback": "ملاحظات تصحيحية",
    "results.noFeedback": "لم ترجع ملاحظات تصحيحية.",
    "results.mlTitle": "رأي ثان من نموذج تعلم آلي",
    "results.mlHelp": "مقارنة تجريبية اختيارية",
    "results.mlBadge": "تجريبي · غير موثق سريريا",
    "results.mlVerifiedBadge": "ملف متحقق منه · مراجعة المعالج مطلوبة",
    "results.experimentalQuality": "الجودة التجريبية",
    "results.predictedLabel": "التصنيف المتوقع",
    "results.model": "النموذج",
    "results.modelMode": "وضع النموذج",
    "results.providerStatus": "حالة المزود",
    "results.baselineUnavailable": "خط الأساس غير متاح",
    "results.mlPrimary": "يبقى التحليل القائم على القواعد هو الأساس",
    "results.mlWarning":
      "هذه المخرجات تجريبية ولا يجوز أن توجه القرارات السريرية.",
    "results.mlDisagreement": "اختلاف تجريبي مع نموذج التعلم الآلي",
    "results.knownLimitations": "القيود المعروفة",
    "results.noLimitations": "لا توجد قيود إضافية مرجعة.",
    "results.medicalDisclaimer": "تنبيه طبي",
    "results.disclaimer":
      "يدعم Movena متابعة التمارين ولا يغني عن تقييم أخصائي علاج طبيعي مرخص. هذا التحليل التعليمي لا يقدم تشخيصا أو علاجا.",
    "results.downloadPdf": "تنزيل تقرير PDF",
    "results.downloadOverlay": "تنزيل الفيديو المعلّم",
    "results.exportJson": "تصدير JSON",
    "results.analyzeAnother": "تحليل فيديو آخر",
    "results.recordingReview": "يحتاج التسجيل إلى مراجعة",
    "results.noValidMovement": "لم يتم رصد حركة {exercise} صالحة",
    "results.tryAgain": "حاول التسجيل مرة أخرى",
    "results.tryAgainBodyweightSquat":
      "سجل الجسم بالكامل، 3-5 تكرارات قرفصاء، كاميرا ثابتة، وإضاءة جيدة.",
    "results.tryAgainSitToStand":
      "أظهر الجسم والكرسي الثابت من زاوية جانبية أو مائلة لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainKneeExtension":
      "استخدم زاوية جانبية ثابتة تظهر الورك والركبة والكاحل والساق المتحركة أثناء الجلوس لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainShoulderAbduction":
      "استخدم زاوية أمامية ثابتة تظهر الكتف والمرفق والمعصم والجذع لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainHipAbduction":
      "استخدم زاوية أمامية ثابتة تظهر الحوض والورك والركبة والكاحل والجذع لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainWalkingGaitScreen":
      "استخدم زاوية جانبية ثابتة تظهر الطرف السفلي بالكامل والقدمين لعدة خطوات مشي مريحة.",
    "results.tryAgainBalance":
      "استخدم زاوية أمامية ثابتة أو مائلة قليلا تظهر الجسم بالكامل والقدمين أثناء ثبات توازن آمن.",
    "results.tryAgainPushUp":
      "استخدم زاوية جانبية ثابتة تظهر الكتفين والمرفقين والمعصمين والوركين والكاحلين في وضع ضغط مدعوم لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainShoulderPress":
      "استخدم زاوية أمامية أو مائلة قليلا تظهر الكتفين والمرفقين والمعصمين والجذع لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainBicepCurl":
      "استخدم زاوية أمامية أو جانبية قليلا تظهر الكتف والمرفق والمعصم والجذع لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainHammerCurl":
      "استخدم زاوية أمامية أو جانبية قليلا تظهر الكتف والمرفق والمعصم واليد والجذع لمدة 3-5 تكرارات كاملة.",
    "results.tryAgainShoulderFlexion":
      "استخدم زاوية أمامية أو جانبية قليلا تظهر الكتف والمرفق والمعصم والجذع لمدة 3-5 رفعات أمامية للذراع.",
    "chart.outOf100": "من 100",
    "chart.angleUnavailable": "اتجاهات الزوايا غير متاحة",
    "chart.angleHelp":
      "فعّل بيانات اتجاه الزوايا قبل التحليل لتضمين قياسات على مستوى الإطارات.",
    "chart.angleTrend": "اتجاه الزاوية",
    "chart.angleTrendDescription":
      "تقديرات زوايا مأخوذة من عينات عبر الفيديو المحلل.",
    "chart.issueBreakdown": "تفصيل الملاحظات",
    "chart.issueBreakdownDescription":
      "ملخص الإشارات أو عدد الملاحظات في الإطارات العينية.",
    "chart.movementProfile": "ملف الحركة",
    "chart.movementProfileDescription": "قيم وصفية معيارية من هذه الجلسة.",
    "chart.repQuality": "جودة التكرار",
    "chart.repQualityDescription":
      "يتطلب تقييم كل تكرار بيانات على مستوى التكرارات من API.",
    "chart.angleAria": "اتجاهات زوايا الحركة",
    "chart.start": "البداية",
    "chart.end": "النهاية",
    "chart.noIssueBreakdown": "لا يوجد تفصيل للملاحظات",
    "chart.noIssueHelp": "لم ترجع ملاحظات حركة في هذا التحليل.",
    "chart.sampledFrames": "{count} إطار عينة",
    "chart.profileAria": "مخطط وصفي لملف الحركة",
    "chart.normalized":
      "ملف وصفي معياري لهذه الجلسة، وليس مقياسا سريريا موثقا.",
    "chart.repPlanned": "جودة كل تكرار مخطط لها",
    "chart.repHelp":
      "يرجع API الحالي إجمالي التكرارات ولا يرجع درجات لكل تكرار.",
    "chart.rep": "تكرار {count}",
    "chart.score": "النتيجة",
    "chart.knee": "الركبة",
    "chart.hip": "الورك",
    "chart.shoulder": "الكتف",
    "chart.visibility": "الظهور",
    "chart.trunk": "الجذع",
    "chart.issueLoad": "حمل الملاحظات",
    "history.eyebrow": "سجل الجلسات",
    "history.title": "الجلسات المحفوظة",
    "history.description":
      "راجع بيانات تحليل الحركة الوصفية المحفوظة في سجل جلساتك المحمي.",
    "history.patientTitle": "التقدم والتقارير",
    "history.patientDescription":
      "راجع نشاط تمارينك المحفوظ وتقارير الحركة المشتركة.",
    "history.therapistTitle": "سجل مراجعات الحركة",
    "history.loadError": "تعذر تحميل سجل الجلسات.",
    "history.detailError": "تعذر تحميل تفاصيل الجلسة المحفوظة.",
    "history.allExercises": "كل التمارين",
    "history.allStatuses": "كل الحالات",
    "history.newest": "الأحدث أولا",
    "history.oldest": "الأقدم أولا",
    "history.unavailable": "السجل غير متاح",
    "history.loading": "جاري تحميل الجلسات",
    "history.emptyTitle":
      "لا توجد جلسات محفوظة بعد. حلل فيديو وفعّل حفظ الجلسة.",
    "history.emptyDescription":
      "يتم حفظ بيانات التحليل الوصفية فقط محليا؛ لا يتم الاحتفاظ بالفيديوهات المرفوعة.",
    "history.noFlags": "لا توجد إشارات محفوظة للملاحظات.",
    "history.viewDetails": "عرض التفاصيل",
    "history.hideDetails": "إخفاء التفاصيل",
    "history.loadingDetail": "جاري تحميل التفاصيل",
    "history.report": "التقرير",
    "history.overlay": "الطبقة المعلّمة",
    "history.detail": "تفاصيل الجلسة المحفوظة",
    "history.noSummary": "لم يتم حفظ ملخص.",
    "history.reportViewer": "تقرير الجلسة",
    "history.overlayViewer": "الطبقة المرئية المشروحة",
    "history.loadingArtifact": "جاري تحميل الملف",
    "history.artifactUnavailable": "الملف غير متاح",
    "history.artifactExpired":
      "انتهت صلاحية هذا الملف المؤقت أو تمت إزالته. أعد التحليل لإنشاء ملف جديد.",
    "history.artifactError":
      "تعذر تحميل الملف. تحقق من اتصال الخادم وحاول مرة أخرى.",
    "history.compareAction": "مقارنة",
    "history.compareTitle": "مقارنة الجلسات المحفوظة",
    "history.compareSelectSecond":
      "اختر جلسة أخرى لنفس التمرين لإجراء المقارنة.",
    "history.compareDescription": "راجع الفروق المسجلة بين جلستين لنفس الحركة.",
    "history.compareClear": "مسح المقارنة",
    "history.compareLoading": "جارٍ تحميل المقارنة",
    "history.compareError": "تعذر تحميل تفاصيل الجلسات المختارة.",
    "history.compareSameExercise": "اختر جلسات من نفس التمرين.",
    "history.compareEarlier": "الجلسة الأقدم",
    "history.compareLater": "الجلسة الأحدث",
    "history.compareScore": "نتيجة الحركة",
    "history.compareReps": "التكرارات",
    "history.compareKnee": "متوسط زاوية الركبة",
    "history.compareHip": "متوسط زاوية الورك",
    "history.compareTrunk": "متوسط زاوية الجذع",
    "history.compareShoulder": "متوسط زاوية الكتف",
    "history.compareElbow": "متوسط زاوية المرفق",
    "history.compareDisclaimer":
      "الفروق ملاحظات وصفية من المنتج، وليست نسب تعافٍ أو دليلًا على تحسن أو تدهور سريري.",
    "history.notice":
      "احم خصوصية المرضى واحفظ فقط المعلومات المصرح لك بمعالجتها. لا ينبغي استخدام تحليل Movena كسجل سريري وحيد.",
    "therapist.eyebrow": "مساحة العمل السريرية",
    "therapist.title": "لوحة العمل السريرية",
    "therapist.description": "راجع المرضى وجلسات الحركة وتقدم برامج التأهيل.",
    "therapist.welcome": "مرحبًا بعودتك، د. {name}",
    "therapist.reviewPatients": "مراجعة المرضى",
    "therapist.analyzeMovement": "تحليل الحركة",
    "therapist.viewSessions": "عرض الجلسات",
    "therapist.warningTitle": "إشعار الخصوصية والاستخدام السريري",
    "therapist.warning":
      "عالج معلومات المرضى فقط بتفويض وموافقة مناسبين، واتبع سياسات الخصوصية والاحتفاظ بالبيانات في مؤسستك. تدعم ملاحظات الذكاء الاصطناعي متابعة التمارين ولا تستبدل تقييم أخصائي علاج طبيعي مرخص.",
    "therapist.noPermission": "ليست لديك صلاحية لعرض هذه الصفحة.",
    "therapist.login": "يرجى تسجيل الدخول للمتابعة.",
    "therapist.loadError": "تعذر تحميل بيانات لوحة المعالج.",
    "therapist.profileCreateError": "تعذر إنشاء ملف المريض.",
    "therapist.detailError": "تعذر تحميل تفاصيل ملف المريض.",
    "therapist.dashboard": "لوحة المعلومات",
    "therapist.patients": "ملفات المستخدمين",
    "therapist.errorTitle": "خطأ في اللوحة",
    "therapist.loading": "جاري تحميل اللوحة",
    "therapist.totalPatients": "إجمالي الملفات",
    "therapist.totalSessions": "إجمالي الجلسات",
    "therapist.lowConfidenceSessions": "جلسات منخفضة الثقة",
    "therapist.commonIssue": "أكثر ملاحظة شيوعا",
    "therapist.recentSessions": "الجلسات الأخيرة",
    "therapist.scoreTrend": "اتجاه نتائج الحركة",
    "therapist.scoreTrendDescription":
      "نتائج أحدث الجلسات المحفوظة مرتبة بمرور الوقت.",
    "therapist.noScoredSessions": "ستظهر نتائج الجلسات هنا بعد تحليل الحركة.",
    "therapist.noSavedSessions": "لا توجد جلسات محفوظة بعد.",
    "therapist.commonIssues": "الملاحظات المرصودة الشائعة",
    "therapist.noIssueHistory": "لا يوجد سجل للملاحظات المرصودة.",
    "therapist.sessionsByExercise": "الجلسات حسب التمرين",
    "therapist.exerciseDistributionDescription":
      "مقارنة مرئية لعدد التحليلات المحفوظة حسب الحركة.",
    "therapist.issueFrequencyDescription":
      "مدى تكرار كل ملاحظة عبر الجلسات المحفوظة.",
    "therapist.lowConfidenceByExercise": "الجلسات منخفضة الثقة حسب التمرين",
    "therapist.noLowConfidence": "لا توجد جلسات منخفضة الثقة.",
    "therapist.createProfile": "إنشاء ملف مريض",
    "therapist.profileHelp":
      "استخدم معرّف المريض المعتمد في مؤسستك وتجنب التفاصيل التعريفية غير الضرورية.",
    "therapist.profileName": "اسم عرض المريض أو المعرّف",
    "therapist.profilePlaceholder": "مثال: مريض 1042",
    "therapist.createProfileButton": "إنشاء ملف",
    "therapist.emptyProfiles": "لا توجد ملفات مرضى بعد",
    "therapist.emptyProfilesDescription":
      "أنشئ ملف مريض مُدارا لتنظيم جلسات الحركة المصرح بها.",
    "therapist.savedSessionCount": "{count} {label} محفوظة",
    "therapist.sessionSingular": "جلسة",
    "therapist.sessionPlural": "جلسات",
    "therapist.viewProfile": "عرض الملف",
    "therapist.backToProfiles": "العودة إلى الملفات",
    "therapist.developmentProfile": "ملف مريض",
    "therapist.averageScore": "متوسط النتيجة",
    "therapist.averageConfidence": "متوسط الثقة",
    "therapist.exerciseHistory": "سجل جلسات التمرين",
    "therapist.noAssignedSessions": "لا توجد جلسات مرتبطة بهذا الملف.",
    "therapist.detectedIssueCounts": "عدد الملاحظات المرصودة",
    "therapist.observationCount": "{count} قيم مصدرية",
    "therapist.provenanceTitle": "مصدر بيانات التقدم",
    "therapist.provenanceSummary":
      "تحسب القيم الطولية فقط من الجلسات المحفوظة والمرتبطة بهذا الملف. أحدث جلسة محفوظة: {date}. هذه الاتجاهات ملاحظات منتج وليست نسب تعاف.",
    "therapist.noProvenance":
      "لا توجد جلسات محفوظة مرتبطة بعد، لذلك تبقى مقاييس التقدم فارغة عمدا.",
    "therapist.rowReps": "{value} تكرارات",
    "therapist.rowScore": "النتيجة {value}",
    "therapist.rowConfidence": "الثقة {value}",
    "therapist.productionNotice":
      "الوصول محمي حسب الأدوار. اتبع متطلبات الموافقة والخصوصية والاحتفاظ والحوكمة السريرية في مؤسستك.",
    "therapist.createPlan": "إنشاء خطة تمارين",
    "therapist.planHelp":
      "وثّق وصف المعالج بشكل مستقل عن ملاحظات تحليل الحركة الآلي.",
    "therapist.planTitle": "عنوان الخطة",
    "therapist.planNotes": "ملاحظات سريرية (اختياري)",
    "therapist.planExercise": "التمرين {count}",
    "therapist.removeExercise": "حذف التمرين",
    "therapist.exercise": "التمرين",
    "therapist.sets": "المجموعات",
    "therapist.reps": "التكرارات",
    "therapist.days_per_week": "أيام/أسبوع",
    "therapist.instructions": "تعليمات للمريض (اختياري)",
    "therapist.addExercise": "إضافة تمرين آخر",
    "therapist.savePlan": "تعيين الخطة",
    "therapist.savingPlan": "جارٍ حفظ الخطة",
    "therapist.planSaveError": "تعذر حفظ خطة التمارين.",
    "therapist.planStatusError": "تعذر تحديث حالة الخطة.",
    "therapist.assignedPlans": "خطط التمارين المعيّنة",
    "therapist.assignedPlansHelp":
      "الوصفات الحالية والسابقة التي كتبها المعالج.",
    "therapist.noPlans": "لا توجد خطط تمارين معيّنة",
    "therapist.noPlansHelp":
      "أنشئ أول خطة لتوثيق المجموعات والتكرارات ومعدل الأسبوع والتعليمات.",
    "therapist.planStatus.active": "نشطة",
    "therapist.planStatus.paused": "متوقفة مؤقتًا",
    "therapist.planStatus.completed": "مكتملة",
    "therapist.activate": "تفعيل",
    "therapist.pause": "إيقاف مؤقت",
    "therapist.complete": "إكمال",
    "therapist.prescription":
      "{sets} مجموعات × {reps} تكرارات · {days} أيام/أسبوع",
    "therapist.baselineComparison": "خط الأساس وأحدث جلسة",
    "therapist.baselineHelp":
      "قارن أول جلسة مسجلة بنتيجة مع أحدث جلسة لكل تمرين باستخدام ملاحظات تحليل الحركة المحفوظة.",
    "therapist.scoredSessions": "{count} جلسات بنتيجة",
    "therapist.scoredSession": "جلسة واحدة بنتيجة",
    "therapist.baseline": "خط الأساس",
    "therapist.latest": "الأحدث",
    "therapist.observedChange": "التغير المرصود",
    "therapist.comparisonAria":
      "{exercise}: نتيجة خط الأساس {baseline}، وأحدث نتيجة {latest}",
    "therapist.repsComparison":
      "التكرارات: {baseline} في خط الأساس ← {latest} حاليًا ({delta})",
    "therapist.needAnotherSession": "يلزم تسجيل جلسة أخرى بنتيجة",
    "therapist.noScoredExerciseSessions": "لا توجد جلسات بنتيجة لهذا التمرين",
    "therapist.currentBaseline": "خط الأساس الحالي: {score} بتاريخ {date}.",
    "therapist.scoreRequired": "أكمل واحفظ تحليلًا بنتيجة لتحديد خط الأساس.",
    "therapist.noBaselineData": "لا توجد بيانات لخط الأساس بعد",
    "therapist.noBaselineHelp":
      "اربط جلسات التحليل المحفوظة بهذا الملف لبدء المقارنة حسب التمرين.",
    "therapist.baselineDisclaimer":
      "فروق النتائج والتكرارات ملاحظات وصفية من المنتج، وليست نسب تعافٍ ولا تثبت تحسنًا أو تدهورًا سريريًا.",
    "about.eyebrow": "حول المنتج",
    "about.title": "فهم الحركة مع حد واضح للسلامة",
    "about.description":
      "Movena هي ذكاء الحركة للتعافي بإرشاد المعالج، وتجمع بين نقاط الوضعية من الرؤية الحاسوبية وقواعد الميكانيكا الحيوية الصريحة وأدوات المراجعة المساعدة الاختيارية.",
    "about.safetyTitle": "السلامة قبل اليقين",
    "about.safetyText": "تبقى النتائج محافظة وتعرض القيود ولا تدعي التشخيص.",
    "about.transparentTitle": "تفسير شفاف",
    "about.transparentText":
      "تقدر نماذج الوضعية المدربة مسبقا النقاط، وتفسر القواعد الصريحة ميكانيكا الحركة.",
    "about.conversationTitle": "مصمم للحوار",
    "about.conversationText":
      "تساعد التقارير المستخدمين والمراجعين على مناقشة الحركة معا، ولا تستبدل التقييم المهني.",
    "about.readyTitle": "جاهز لمراجعة حركة؟",
    "about.readyText":
      "استخدم تسجيلا ثابتا يظهر الجسم بوضوح للحصول على أوضح تقرير تعليمي.",
    "about.openAnalyzer": "افتح المحلل",
    "speech.listen": "استمع إلى الملاحظات",
    "speech.stop": "إيقاف الصوت",
    "speech.unavailable": "الملاحظات الصوتية غير مدعومة في هذا المتصفح.",
    "speech.statusComplete": "اكتمل تحليل {exercise}.",
    "speech.statusRejected": "تم رفض تسجيل {exercise} وتعذر تقييمه.",
    "speech.reps": "التكرارات المكتملة: {count}.",
    "speech.score": "نتيجة الحركة: {score} من 100.",
    "speech.confidence": "ثقة التحليل: {level}.",
    "speech.feedbackIntro": "الملاحظات:",
    "speech.limitationsIntro": "قيود مهمة:",
    "speech.disclaimer":
      "هذا التحليل تعليمي ولا يقدم تشخيصا أو علاجا ولا يستبدل المختص المرخص.",
    "coach.eyebrow": "أدوات الحركة بالذكاء الاصطناعي",
    "coach.title": "مختبر التدريب على التمارين",
    "coach.description":
      "مساحة للكاميرا المحلية وجاهزية النموذج لتطوير تدريب لحظي مستقبلي دون تفعيل ملاحظات حركة غير معتمدة.",
    "coach.cameraTitle": "التقاط كاميرا محلي",
    "coach.cameraHelp":
      "تبدأ الكاميرا فقط بعد الضغط على زر البدء. الصوت معطل ولا يتم رفع البث.",
    "coach.videoLabel": "معاينة الكاميرا المحلية",
    "coach.start": "تشغيل الكاميرا",
    "coach.stop": "إيقاف الكاميرا",
    "coach.status.idle": "خامل",
    "coach.status.requesting": "طلب الكاميرا",
    "coach.status.active": "الكاميرا نشطة",
    "coach.status.stopped": "متوقفة",
    "coach.errorTitle": "الكاميرا غير متاحة",
    "coach.noCameraError":
      "لم يتم اكتشاف كاميرا على هذا الجهاز. لا يزال بإمكانك التعرف على التمرين أو تحليله برفع فيديو أدناه.",
    "coach.permissionDeniedError":
      "تم حظر إذن الكاميرا. اسمح بالوصول إلى الكاميرا من المتصفح وإعدادات خصوصية Windows ثم حاول مرة أخرى. يظل رفع الفيديو متاحا.",
    "coach.cameraBusyError":
      "الكاميرا غير متاحة أو يستخدمها تطبيق آخر. أغلق تطبيقات الكاميرا الأخرى وحاول مجددا، أو ارفع فيديو أدناه.",
    "coach.cameraConstraintsError":
      "تعذر على الكاميرا المتصلة توفير بث فيديو متوافق. جرب كاميرا أخرى أو ارفع فيديو أدناه.",
    "coach.unsupported":
      "هذا المتصفح لا يدعم التقاط الكاميرا لهذه التجربة التقنية.",
    "coach.permissionError": "تم حظر الوصول إلى الكاميرا أو تعذر تشغيلها.",
    "coach.safetyTitle": "تجربة تقنية فقط",
    "coach.safetyText":
      "لا يتم رفع فيديو أو صوت، ولا يتم الاحتفاظ بالإطارات، ولا تقدم هذه الصفحة إرشادا سريريا.",
    "coach.derivedTitle": "إشارات محلية مشتقة",
    "coach.samples": "العينات",
    "coach.brightness": "السطوع",
    "coach.visibility": "مؤشر الظهور",
    "coach.latency": "متوسط الزمن المنقضي",
    "coach.landmarksIdle":
      "يتم تحميل نموذج وضعية الجسم على الجهاز عند تشغيل الكاميرا.",
    "coach.landmarksLoading": "جارٍ تحميل نموذج وضعية الجسم على الجهاز...",
    "coach.landmarksError":
      "تعذر تشغيل نموذج وضعية الجسم على الجهاز. تحقق من الاتصال ودعم WebAssembly في المتصفح، ثم أعد تشغيل الكاميرا.",
    "coach.landmarksEnabled":
      "تتبع وضعية الجسم على الجهاز نشط: {count} معالم، متوسط الثقة {confidence}.",
    "coach.modelTitle": "جاهزية نموذج التعرف",
    "coach.modelAvailable": "النماذج المرشحة جاهزة",
    "coach.modelPending": "الأثر قيد الانتظار",
    "coach.modelDescription":
      "يمكن لنموذجي XGBoost وGRU الزمني المثبتين اقتراح تمرين. لا يبدآن المحلل ولا يستبدلان الاختيار اليدوي.",
    "coach.stepData": "تم تنفيذ عقد بيانات الوضعية ذي 40 ميزة ومسار الإعداد",
    "coach.stepRecognition":
      "تم تدريب مرشحي XGBoost وGRU الزمني مع مجموعات اختبار منفصلة حسب الفيديو",
    "coach.stepAnalyzers":
      "تم تنفيذ محللات محافظة للضغط وضغط الكتف وثني الذراع وتمرين المطرقة وثني الكتف مع قيود الوضعية المرئية",
    "coach.stepRealtime": "البث الموثق وأحداث التكرار والحفظ قيد الانتظار",
    "coach.complete": "التدريب في الوقت الفعلي جاهز",
    "coach.stepAnalyzersComplete":
      "تم تنفيذ المحللات المحافظة؛ دليل اتجاه اليد لتمرين المطرقة نشط",
    "coach.stepRealtimeComplete":
      "تم تنفيذ البث الموثق وأحداث التكرار وحفظ البيانات الوصفية فقط",
    "coach.exerciseMode": "التمرين المباشر",
    "coach.bicepCurl": "ثني العضلة ذات الرأسين",
    "coach.hammerCurl": "تمرين المطرقة",
    "coach.overlayLabel": "تراكب وضعية الجسم المباشر",
    "coach.overlayActive": "التراكب مباشر",
    "coach.overlayWaiting": "يبدأ التراكب مع الكاميرا",
    "coach.cameraView": "زاوية الكاميرا",
    "coach.setup": "وضع البداية",
    "coach.movement": "الحركة",
    "coach.note": "ملاحظة",
    "coach.liveAngle": "زاوية المفصل",
    "coach.exercise.bicep_curl": "ثني العضلة ذات الرأسين",
    "coach.exercise.bicep_curl.view":
      "من الأمام أو الجانب قليلا مع إظهار الكتفين والمرفقين والرسغين والوركين.",
    "coach.exercise.bicep_curl.setup":
      "قف منتصبا والمرفق العامل ممدودا وقريبا من جانبك.",
    "coach.exercise.bicep_curl.motion":
      "اثن المرفق ضمن نطاق مريح ثم اخفض الذراع بتحكم.",
    "coach.exercise.bicep_curl.note":
      "حافظ على ثبات أعلى الذراع. لا تستطيع الكاميرا تقييم أمان الحمل أو الألم.",
    "coach.exercise.hammer_curl": "تمرين المطرقة",
    "coach.exercise.hammer_curl.view":
      "من الأمام أو الجانب قليلا مع إظهار اليد والذراع العامل بالكامل.",
    "coach.exercise.hammer_curl.setup":
      "ابدأ والمرفق ممدود والإبهام متجها إلى أعلى.",
    "coach.exercise.hammer_curl.motion":
      "اثن المرفق مع إبقاء وضع اليد محايدا ثم عد ببطء.",
    "coach.exercise.hammer_curl.note":
      "اتجاه القبضة تقديري وقد لا يتوفر عند حجب اليد.",
    "coach.exercise.bodyweight_squat": "القرفصاء بوزن الجسم",
    "coach.exercise.bodyweight_squat.view":
      "من الجانب أو الأمام بزاوية مع إبقاء الكتفين والوركين والركبتين والكاحلين داخل الإطار.",
    "coach.exercise.bodyweight_squat.setup":
      "قف بوضع مريح مع مساحة خالية وآمنة حولك.",
    "coach.exercise.bodyweight_squat.motion":
      "انخفض بتحكم حتى تنثني الركبتان بوضوح ثم عد إلى الوقوف.",
    "coach.exercise.bodyweight_squat.note":
      "استخدم دعما ثابتا عند الحاجة وتوقف عند الألم أو الدوار أو الأعراض غير المعتادة.",
    "coach.exercise.shoulder_press": "ضغط الكتف",
    "coach.exercise.shoulder_press.view":
      "من الأمام أو بزاوية بسيطة مع إظهار اليدين فوق الرأس.",
    "coach.exercise.shoulder_press.setup":
      "ابدأ والمرفقان مثنيان واليدان قرب مستوى الكتفين.",
    "coach.exercise.shoulder_press.motion":
      "ادفع إلى أعلى حتى يمتد المرفقان ثم عد بتحكم.",
    "coach.exercise.shoulder_press.note":
      "تدرب دون وزن أو استخدم حملا معتمدا من المختص فقط.",
    "coach.exercise.shoulder_abduction": "رفع الذراعين جانبيا",
    "coach.exercise.shoulder_abduction.view":
      "من الأمام مع إظهار الذراعين والجذع من الوركين إلى اليدين.",
    "coach.exercise.shoulder_abduction.setup":
      "قف منتصبا والذراعان بجانب الجسم والمرفقان مسترخيان.",
    "coach.exercise.shoulder_abduction.motion":
      "ارفع الذراعين جانبيا نحو مستوى الكتفين ثم اخفضهما ببطء.",
    "coach.exercise.shoulder_abduction.note":
      "تحرك ضمن نطاق مريح وتجنب رفع الكتفين نحو الأذنين.",
    "coach.liveReps": "التكرارات المباشرة",
    "coach.livePhase": "المرحلة",
    "coach.liveGrip": "دليل القبضة",
    "coach.liveCue": "إرشاد التدريب المباشر",
    "coach.cue.idle": "شغّل الكاميرا لبدء تتبع التكرارات مباشرة.",
    "coach.cue.connecting": "جارٍ توصيل عداد التكرارات المباشر…",
    "coach.cue.tracking": "تتبع وضعية الجسم نشط.",
    "coach.cue.seekingStart": "قف منتصبًا وأبقِ المفاصل العاملة ظاهرة.",
    "coach.cue.ready": "جاهز — ابدأ التكرار التالي.",
    "coach.cue.working": "استمر ضمن نطاق حركة مريح.",
    "coach.cue.returning": "عُد إلى وضع البداية بتحكم.",
    "coach.cue.saved": "اكتملت الجلسة وتم حفظ الملخص المشتق.",
    "coach.lastRepAnalysis":
      "تم احتساب التكرار {rep} · {duration} ث · نطاق حركة {range}°",
    "coach.loginRequired":
      "سجل الدخول قبل بدء جلسة تدريب موثقة. تظل جودة الكاميرا وتتبع المعالم المحلي متاحين دون بث.",
    "coach.sessionSaved":
      "تم حفظ ملخص الجلسة المشتق. لم يتم الاحتفاظ بإطارات الكاميرا أو تسلسلات المعالم.",
    "coach.recognitionTitle": "تعرف على التمرين من الفيديو",
    "coach.recognitionDescription":
      "ارفع مقطعا قصيرا للحركة ليصنف النموذج الزمني التمارين المحتملة. راجع الاقتراح وأكده قبل فتح المحلل.",
    "coach.candidateReady": "المرشح الزمني جاهز",
    "coach.recognitionChoose": "اختر فيديو حركة",
    "coach.recognitionSelected": "تم اختيار {size} ميجابايت",
    "coach.recognitionFormats":
      "MP4 أو MOV أو AVI أو MKV أو WEBM · الحد الأقصى 100 ميجابايت",
    "coach.recognitionTemporary": "تتم معالجة الملف مؤقتا وحذفه بعد التعرف.",
    "coach.recognitionAction": "تعرف على التمرين",
    "coach.recognitionProcessing": "جار التعرف",
    "coach.recognitionErrorTitle": "تعذر إكمال التعرف",
    "coach.recognitionError":
      "تعذر التعرف على هذا الفيديو. تحقق من التسجيل وحاول مرة أخرى.",
    "coach.recognitionEmptyTitle": "ستظهر نتائج الاقتراح هنا",
    "coach.recognitionEmptyText":
      "يعرض النموذج أفضل التمارين المحتملة مع الثقة. الاقتراح لا يقيم الأداء أو السلامة.",
    "coach.recognitionSuggestion": "التمرين المقترح",
    "coach.recognitionConfidence": "ثقة النموذج {confidence}",
    "coach.uncertainBadge": "ثقة منخفضة",
    "coach.uncertainTitle": "اختر التمرين يدويا",
    "coach.uncertainText":
      "الثقة أقل من حد القبول المعاير {threshold}، لذلك لا يمكن تأكيد هذا الاقتراح.",
    "coach.confirmSuggestion": "أكد {exercise} وتابع",
    "coach.confirmingSuggestion": "جار تسجيل التأكيد",
    "coach.confirmationAuditTitle": "تعذر تسجيل التأكيد",
    "coach.confirmationAuditError":
      "حاول مرة أخرى. لم يتم فتح المحلل لأن تأكيد التعرف لم يتم حفظه.",
    "coach.noAnalyzerTitle": "المحلل غير متاح",
    "coach.noAnalyzerText":
      "يمكن التعرف على هذا التصنيف، لكن لا يوجد محلل تدريب نشط له في Movena.",
  },
};

export function interpolate(message, values = {}) {
  return Object.entries(values).reduce(
    (result, [key, value]) => result.replaceAll(`{${key}}`, String(value)),
    message,
  );
}

export function translate(locale, key, values) {
  const catalog = MESSAGES[locale] || MESSAGES[DEFAULT_LOCALE];
  const message = catalog[key] || MESSAGES[DEFAULT_LOCALE][key] || key;
  return interpolate(message, values);
}

export function getExerciseText(exerciseId, locale = DEFAULT_LOCALE) {
  const entry = exerciseText[exerciseId];
  if (entry) return entry[locale] || entry[DEFAULT_LOCALE];
  const label = String(exerciseId || "movement").replaceAll("_", " ");
  return {
    name: label.replace(/\b\w/g, (letter) => letter.toUpperCase()),
    short: label,
    bodyRegion: translate(locale, "status.planned"),
    family: translate(locale, "status.planned"),
    cameraView: translate(locale, "status.notAvailable"),
    landmarks: [],
    description:
      locale === "ar"
        ? "تغطية مخطط لها؛ لا يتوفر محلل عامل بعد."
        : "Planned exercise coverage; no working analyzer is available yet.",
    pattern:
      locale === "ar" ? "غير متاح للتحليل." : "Not available for analysis.",
    safety:
      locale === "ar"
        ? "لا تستخدم Movena لتحليل هذا التمرين بعد."
        : "Do not use Movena to analyze this exercise yet.",
  };
}

export function prettyLabel(value = "", locale = DEFAULT_LOCALE) {
  if (!value) return "";
  const normalized = String(value).toLowerCase();
  if (normalized === "success") return translate(locale, "common.success");
  if (normalized === "rejected") return translate(locale, "common.rejected");
  if (normalized === "unknown") return translate(locale, "common.unknown");
  if (normalized === "none") return translate(locale, "common.none");
  const exercise = getExerciseText(normalized, locale);
  if (exercise.name && normalized in exerciseText) return exercise.name;
  const words = String(value).replaceAll("_", " ");
  return locale === "ar"
    ? words
    : words.replace(/\b\w/g, (letter) => letter.toUpperCase());
}
