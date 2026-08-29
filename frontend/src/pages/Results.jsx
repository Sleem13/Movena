import { ArrowLeft } from "lucide-react";
import { Alert, Badge, Button, Card, EmptyState } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ResultsDashboard, { ExportActions } from "../components/results/ResultsDashboard.jsx";
import SpeechFeedbackControls from "../components/results/SpeechFeedbackControls.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function Results({ report, originalVideoUrl, onAnalyzeAnother, onGoAnalyze, onViewHistory, onContinueCare }) {
  const { t, exerciseText } = useLocale();
  if (!report) {
    return <main className="mx-auto max-w-4xl px-6 py-20">
      <EmptyState title={t("results.emptyTitle")} description={t("results.emptyDescription")} />
      <div className="mt-5 text-center">
        <Button onClick={onGoAnalyze}><ArrowLeft size={16} />{t("results.goAnalyze")}</Button>
      </div>
    </main>;
  }

  const rejected = report.status === "rejected";
  const displayName = exerciseText(report.exercise).name;
  const recognitionNotice = report.auto_routed
    ? t("upload.autoRerouteNotice", {
      selected: exerciseText(report.selected_exercise_id).name,
      suggested: displayName,
      confidence: `${Math.round((report.recognition_confidence || 0) * 100)}%`,
    })
    : report.recognition_message;
  const actions = <div className="flex flex-wrap items-start gap-2">
    <SpeechFeedbackControls report={report} />
    {!rejected && <ExportActions report={report} />}
  </div>;

  return <main className="mx-auto w-full max-w-7xl px-6 py-12">
    <PageHeader
      eyebrow={t(rejected ? "results.rejectedEyebrow" : "results.completeEyebrow")}
      title={t(rejected ? "results.rejectedTitle" : "results.reportTitle", { exercise: displayName })}
      description={rejected
        ? t("results.rejectedDescription", { movement: displayName })
        : t("results.completeDescription")}
      actions={actions}
    />
    {recognitionNotice && <Alert
      className="mb-5"
      tone={report.auto_routed ? "success" : "warning"}
      title={t(report.auto_routed ? "results.autoRoutedTitle" : "results.recognitionReviewTitle")}
    >{recognitionNotice}</Alert>}
    {report.session_id && <Card className="mb-5 flex flex-wrap items-center justify-between gap-3 border-teal-200 p-4">
      <div>
        <Badge tone="teal">{t("results.savedSession")}</Badge>
        <p className="mt-2 text-xs text-slate-500">{t("results.sessionStored", { session: report.session_id.slice(0, 8) })}</p>
      </div>
      <div className="flex flex-wrap gap-2"><Button variant="secondary" onClick={onViewHistory}>{t("results.viewHistory")}</Button>{onContinueCare ? <Button onClick={onContinueCare}>{t("results.continueCheckIn")}</Button> : null}</div>
    </Card>}
    <ResultsDashboard report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={onAnalyzeAnother} />
  </main>;
}
