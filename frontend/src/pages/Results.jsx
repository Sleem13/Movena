import { ArrowLeft } from "lucide-react";
import { Button, EmptyState } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ResultsDashboard, { ExportActions } from "../components/results/ResultsDashboard.jsx";

export default function Results({ report, originalVideoUrl, onAnalyzeAnother, onGoAnalyze }) {
  if (!report) {
    return <main className="mx-auto max-w-4xl px-6 py-20"><EmptyState title="No analysis results yet" description="Upload a squat video to create a movement dashboard." /><div className="mt-5 text-center"><Button onClick={onGoAnalyze}><ArrowLeft size={16} />Go to Analyze</Button></div></main>;
  }
  return <main className="mx-auto w-full max-w-7xl px-6 py-12"><PageHeader eyebrow="Analysis complete" title="Bodyweight squat report" description="Review movement metrics, visual evidence, feedback, and known limitations from this session." actions={<ExportActions report={report} />} /><ResultsDashboard report={report} originalVideoUrl={originalVideoUrl} onAnalyzeAnother={onAnalyzeAnother} /></main>;
}
