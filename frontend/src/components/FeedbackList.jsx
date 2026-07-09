import { CheckCircle2, ShieldAlert } from "lucide-react";

export default function FeedbackList({ feedback = [] }) {
  return (
    <section className="rounded-lg border border-clinical-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-2">
        <CheckCircle2 size={20} className="text-clinical-teal" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-clinical-ink">Corrective feedback</h2>
      </div>
      <div className="space-y-3">
        {feedback.map((item, index) => {
          const isDisclaimer = item.toLowerCase().includes("licensed physiotherapist");
          return (
            <div
              key={`${item}-${index}`}
              className={`flex gap-3 rounded-lg border px-4 py-3 text-sm ${
                isDisclaimer
                  ? "border-amber-200 bg-amber-50 text-amber-900"
                  : "border-emerald-100 bg-emerald-50 text-emerald-900"
              }`}
            >
              {isDisclaimer ? (
                <ShieldAlert className="mt-0.5 shrink-0" size={17} aria-hidden="true" />
              ) : (
                <CheckCircle2 className="mt-0.5 shrink-0" size={17} aria-hidden="true" />
              )}
              <p>{item}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
