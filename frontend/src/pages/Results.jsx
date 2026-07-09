import AnalysisSummary from "../components/AnalysisSummary.jsx";
import FeedbackList from "../components/FeedbackList.jsx";
import ScoreCard from "../components/ScoreCard.jsx";

export default function Results({ report, onAnalyzeAnother }) {
  if (!report) {
    return null;
  }

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
        <button
          type="button"
          onClick={onAnalyzeAnother}
          className="h-11 rounded-lg border border-clinical-line bg-white px-4 text-sm font-semibold text-clinical-ink transition hover:border-clinical-teal"
        >
          Analyze another video
        </button>
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
    </main>
  );
}
