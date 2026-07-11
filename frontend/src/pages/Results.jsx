import AnalysisSummary from "../components/AnalysisSummary.jsx";
import FeedbackList from "../components/FeedbackList.jsx";
import ScoreCard from "../components/ScoreCard.jsx";
import { Download, ShieldAlert, Video } from "lucide-react";
import { artifactUrl } from "../services/api.js";

export default function Results({ report, onAnalyzeAnother }) {
  if (!report) {
    return null;
  }
  const reportDownloadUrl = artifactUrl(report.report_download_url);
  const overlayVideoUrl = artifactUrl(report.overlay_download_url);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-10">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-clinical-teal">
            Analysis complete
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-clinical-ink">
            Bodyweight squat report
          </h1>
        </div>
        <div className="flex flex-wrap gap-3">
          {reportDownloadUrl && (
            <a href={reportDownloadUrl} className="inline-flex h-11 items-center gap-2 rounded-lg bg-clinical-teal px-4 text-sm font-semibold text-white" download>
              <Download size={17} aria-hidden="true" /> Download PDF report
            </a>
          )}
          <button type="button" onClick={onAnalyzeAnother} className="h-11 rounded-lg border border-clinical-line bg-white px-4 text-sm font-semibold text-clinical-ink transition hover:border-clinical-teal">
            Analyze another video
          </button>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <ScoreCard label="Movement score" value={report.movement_score} unit="/100" type="score" />
        <ScoreCard label="Total reps" value={report.total_reps} type="reps" />
        <ScoreCard label="Avg knee angle" value={report.average_knee_angle} unit="deg" type="angle" />
        <ScoreCard label="Avg hip angle" value={report.average_hip_angle} unit="deg" type="angle" />
        <ScoreCard label="Avg trunk lean" value={report.average_trunk_angle} unit="deg" type="angle" />
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <AnalysisSummary report={report} />
        <FeedbackList feedback={report.feedback} />
      </div>

      {overlayVideoUrl && (
        <section className="mt-6 rounded-lg border border-clinical-line bg-white p-5 shadow-panel">
          <div className="mb-4 flex items-center gap-2">
            <Video size={20} className="text-clinical-teal" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-clinical-ink">Annotated movement preview</h2>
          </div>
          <video className="w-full max-w-3xl rounded-lg bg-black" controls src={overlayVideoUrl}>
            Your browser does not support video playback.
          </video>
          <p className="mt-3 text-sm text-slate-600">Experimental 2D overlay; markers may shift with occlusion or camera angle.</p>
        </section>
      )}

      <section className="mt-6 flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
        <ShieldAlert className="mt-0.5 shrink-0" size={19} aria-hidden="true" />
        <div>
          <h2 className="font-semibold">Educational analysis only</h2>
          <p className="mt-1">Possible movement observations do not diagnose injury or pathology. Consider reviewing this report with a licensed physiotherapist.</p>
        </div>
      </section>
    </main>
  );
}
