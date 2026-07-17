import { ArrowLeft } from "lucide-react";
import { Badge, Button, Card, EmptyState } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ResultsDashboard, { ExportActions } from "../components/results/ResultsDashboard.jsx";

export default function Results({ report, originalVideoUrl, onAnalyzeAnother, onGoAnalyze, onViewHistory }) {
  if (!report) {
    return <main className="mx-auto max-w-4xl px-6 py-20"><EmptyState title="No analysis results yet" description="Upload a squat video to create a movement dashboard." /><div className="mt-5 text-center"><Button onClick={onGoAnalyze}><ArrowLeft size={16} />Go to Analyze</Button></div></main>;
  }
  const rejected = report.status === "rejected";
  const sitToStand = report.exercise === "sit_to_stand";
  const displayName = sitToStand ? "Sit-to-Stand" : "Bodyweight squat";
  return <main className="mx-auto w-full max-w-7xl px-6 py-12"><PageHeader eyebrow={rejected ? "Recording rejected" : "Analysis complete"} title={rejected ? `${displayName} recording could not be scored` : `${displayName} report`} description={rejected ? `Review the recording guidance and try again with a complete ${sitToStand ? "sit-to-stand" : "squat"} sequence.` : "Review movement metrics, visual evidence, feedback, and known limitations from this session."} actions={rejected ? null : <ExportActions report={report} />} />{report.session_id && <Card className="mb-5 flex flex-wrap items-center justify-between gap-3 border-teal-200 p-4"><div><Badge tone="teal">Saved session</Badge><p className="mt-2 text-xs text-slate-500">Session {report.session_id.slice(0, 8)} · stored in the local development database</p></div><Button variant="secondary" onClick={onViewHistory}>View Session History</Button></Card>}<ResultsDashboard report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={onAnalyzeAnother} /></main>;
}
