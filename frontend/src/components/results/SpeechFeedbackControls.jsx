import { useEffect, useMemo, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { useLocale } from "../../i18n/LocaleContext.jsx";
import { Button } from "../common/UI.jsx";

export function buildSpeechSummary(report, t) {
  const translatedExercise = t(`exercise.${report.exercise}`);
  const exercise = translatedExercise.startsWith("exercise.") ? "Movement" : translatedExercise;
  const parts = [t(report.status === "rejected" ? "speech.statusRejected" : "speech.statusComplete", { exercise })];
  if (report.summary) parts.push(report.summary);
  if (report.total_reps != null) parts.push(t("speech.reps", { count: report.total_reps }));
  if (report.movement_score != null) parts.push(t("speech.score", { score: report.movement_score }));
  if (report.analysis_confidence?.level) parts.push(t("speech.confidence", { level: report.analysis_confidence.level }));
  if (report.feedback?.length) parts.push(t("speech.feedbackIntro"), ...report.feedback.slice(0, 3));
  if (report.limitations?.length) parts.push(t("speech.limitationsIntro"), ...report.limitations.slice(0, 2));
  parts.push(t("speech.disclaimer"));
  return parts.filter(Boolean).join(" ");
}

export default function SpeechFeedbackControls({ report }) {
  const { locale, t } = useLocale();
  const [speaking, setSpeaking] = useState(false);
  const supported = typeof window !== "undefined" && "speechSynthesis" in window && typeof SpeechSynthesisUtterance !== "undefined";
  const synthesis = supported ? window.speechSynthesis : null;
  const summary = useMemo(() => buildSpeechSummary(report, t), [report, t]);

  useEffect(() => () => {
    synthesis?.cancel();
  }, [synthesis]);

  function toggleSpeech() {
    if (!supported) return;
    if (speaking) {
      synthesis.cancel();
      setSpeaking(false);
      return;
    }
    synthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(summary);
    utterance.lang = locale === "ar" ? "ar-EG" : "en-US";
    utterance.rate = 0.95;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    synthesis.speak(utterance);
  }

  return <div className="inline-flex flex-col items-start">
    <Button
      variant="secondary"
      type="button"
      onClick={toggleSpeech}
      disabled={!supported}
      title={supported ? undefined : t("speech.unavailable")}
    >
      {speaking ? <VolumeX size={16} aria-hidden="true" /> : <Volume2 size={16} aria-hidden="true" />}
      {speaking ? t("speech.stop") : t("speech.listen")}
    </Button>
    {!supported && <span className="mt-1 max-w-56 text-xs text-slate-500">{t("speech.unavailable")}</span>}
    <span className="sr-only" aria-live="polite">{speaking ? t("speech.stop") : ""}</span>
  </div>;
}
