import { AlertTriangle, ClipboardList } from "lucide-react";

function EmptyState({ label }) {
  return <p className="text-sm text-slate-500">{label}</p>;
}

export default function AnalysisSummary({ report }) {
  return (
    <section className="rounded-lg border border-clinical-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-2">
        <ClipboardList size={20} className="text-clinical-teal" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-clinical-ink">Analysis summary</h2>
      </div>

      <p className="text-sm leading-6 text-slate-700">{report.summary}</p>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <AlertTriangle size={17} className="text-amber-600" aria-hidden="true" />
            <h3 className="text-sm font-semibold text-slate-800">Detected issues</h3>
          </div>
          {report.detected_issues?.length ? (
            <ul className="space-y-2">
              {report.detected_issues.map((issue) => (
                <li key={issue} className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  {issue.replaceAll("_", " ")}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState label="No major movement issues detected." />
          )}
        </div>

        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-800">Known limitations</h3>
          {report.limitations?.length ? (
            <ul className="space-y-2">
              {report.limitations.map((limitation) => (
                <li key={limitation} className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  {limitation}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState label="No limitations returned." />
          )}
        </div>
      </div>
    </section>
  );
}
