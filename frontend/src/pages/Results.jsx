import { ArrowLeft } from "lucide-react";
import { Badge, Button, Card, EmptyState } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ResultsDashboard, { ExportActions } from "../components/results/ResultsDashboard.jsx";
import SpeechFeedbackControls from "../components/results/SpeechFeedbackControls.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function Results({ report, originalVideoUrl, onAnalyzeAnother, onGoAnalyze, onViewHistory }) {
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
    {report.session_id && <Card className="mb-5 flex flex-wrap items-center justify-between gap-3 border-teal-200 p-4">
      <div>
        <Badge tone="teal">{t("results.savedSession")}</Badge>
        <p className="mt-2 text-xs text-slate-500">{t("results.sessionStored", { session: report.session_id.slice(0, 8) })}</p>
      </div>
      <Button variant="secondary" onClick={onViewHistory}>{t("results.viewHistory")}</Button>
    </Card>}
    <ResultsDashboard report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={onAnalyzeAnother} />
  </main>;
}
