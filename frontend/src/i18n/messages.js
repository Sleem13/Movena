export const DEFAULT_LOCALE = "en";
export const LOCALE_STORAGE_KEY = "physiovision_locale";

export const SUPPORTED_LOCALES = [
  { code: "en", label: "English", direction: "ltr" },
  { code: "ar", label: "العربية", direction: "rtl" },
];

export const MESSAGES = {
  en: {
    "language.label": "Language",
    "nav.home": "Home",
    "nav.exercises": "Exercises",
    "nav.analyze": "Analyze",
    "nav.results": "Results",
    "nav.history": "History",
    "nav.therapist": "Therapist",
    "nav.about": "About",
    "nav.profile": "Profile",
    "nav.login": "Log in",
    "brand.tagline": "Movement intelligence",
    "exercise.bodyweight_squat": "Bodyweight squat",
    "exercise.sit_to_stand": "Sit-to-Stand",
    "exercise.knee_extension": "Knee Extension",
    "exercise.shoulder_abduction": "Shoulder Abduction",
    "exercise.hip_abduction": "Hip Abduction",
    "footer.product": "PhysioVision AI · Educational movement support",
    "footer.disclaimer": "This analysis does not replace assessment, diagnosis, or treatment by a licensed professional.",
    "results.emptyTitle": "No analysis results yet",
    "results.emptyDescription": "Upload a supported exercise video to create a movement dashboard.",
    "results.goAnalyze": "Go to Analyze",
    "results.rejectedEyebrow": "Recording rejected",
    "results.completeEyebrow": "Analysis complete",
    "results.rejectedTitle": "{exercise} recording could not be scored",
    "results.reportTitle": "{exercise} report",
    "results.rejectedDescription": "Review the recording guidance and try again with a complete {movement} sequence.",
    "results.completeDescription": "Review movement metrics, visual evidence, feedback, and known limitations from this session.",
    "results.savedSession": "Saved session",
    "results.sessionStored": "Session {session} · stored in the local development database",
    "results.viewHistory": "View Session History",
    "speech.listen": "Listen to feedback",
    "speech.stop": "Stop audio",
    "speech.unavailable": "Spoken feedback is not supported by this browser.",
    "speech.statusComplete": "{exercise} analysis complete.",
    "speech.statusRejected": "The {exercise} recording was rejected and could not be scored.",
    "speech.reps": "Completed repetitions: {count}.",
    "speech.score": "Movement score: {score} out of 100.",
    "speech.confidence": "Analysis confidence: {level}.",
    "speech.feedbackIntro": "Feedback:",
    "speech.limitationsIntro": "Important limitations:",
    "speech.disclaimer": "This educational analysis does not provide diagnosis or treatment and does not replace a licensed professional.",
  },
  ar: {
    "language.label": "اللغة",
    "nav.home": "الرئيسية",
    "nav.exercises": "التمارين",
    "nav.analyze": "التحليل",
    "nav.results": "النتائج",
    "nav.history": "السجل",
    "nav.therapist": "المعالج",
    "nav.about": "حول",
    "nav.profile": "الملف الشخصي",
    "nav.login": "تسجيل الدخول",
    "brand.tagline": "تحليل الحركة",
    "exercise.bodyweight_squat": "القرفصاء بوزن الجسم",
    "exercise.sit_to_stand": "الجلوس إلى الوقوف",
    "exercise.knee_extension": "مد الركبة",
    "exercise.shoulder_abduction": "إبعاد الكتف",
    "exercise.hip_abduction": "إبعاد الورك",
    "footer.product": "PhysioVision AI · دعم تعليمي للحركة",
    "footer.disclaimer": "لا يحل هذا التحليل محل التقييم أو التشخيص أو العلاج بواسطة مختص مرخص.",
    "results.emptyTitle": "لا توجد نتائج تحليل بعد",
    "results.emptyDescription": "ارفع فيديو لتمرين مدعوم لإنشاء لوحة تحليل الحركة.",
    "results.goAnalyze": "الانتقال إلى التحليل",
    "results.rejectedEyebrow": "تم رفض التسجيل",
    "results.completeEyebrow": "اكتمل التحليل",
    "results.rejectedTitle": "تعذر تقييم تسجيل {exercise}",
    "results.reportTitle": "تقرير {exercise}",
    "results.rejectedDescription": "راجع إرشادات التسجيل وحاول مرة أخرى بتسلسل كامل لحركة {movement}.",
    "results.completeDescription": "راجع مؤشرات الحركة والأدلة المرئية والملاحظات والقيود المعروفة لهذه الجلسة.",
    "results.savedSession": "جلسة محفوظة",
    "results.sessionStored": "الجلسة {session} · محفوظة في قاعدة بيانات التطوير المحلية",
    "results.viewHistory": "عرض سجل الجلسات",
    "speech.listen": "استمع إلى الملاحظات",
    "speech.stop": "إيقاف الصوت",
    "speech.unavailable": "الملاحظات الصوتية غير مدعومة في هذا المتصفح.",
    "speech.statusComplete": "اكتمل تحليل {exercise}.",
    "speech.statusRejected": "تم رفض تسجيل {exercise} وتعذر تقييمه.",
    "speech.reps": "عدد التكرارات المكتملة: {count}.",
    "speech.score": "نتيجة الحركة: {score} من 100.",
    "speech.confidence": "مستوى الثقة في التحليل: {level}.",
    "speech.feedbackIntro": "الملاحظات:",
    "speech.limitationsIntro": "قيود مهمة:",
    "speech.disclaimer": "هذا التحليل تعليمي ولا يقدم تشخيصاً أو علاجاً ولا يحل محل المختص المرخص.",
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
