import { Activity, BadgeCheck, Gauge } from "lucide-react";

const iconMap = {
  score: Gauge,
  reps: Activity,
  angle: BadgeCheck,
};

export default function ScoreCard({ label, value, unit, type = "score" }) {
  const Icon = iconMap[type] || Gauge;

  return (
    <div className="rounded-lg border border-clinical-line bg-white p-5 shadow-panel">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-slate-600">{label}</span>
        <Icon size={18} className="text-clinical-teal" aria-hidden="true" />
      </div>
      <div className="mt-3 flex items-end gap-1">
        <span className="text-3xl font-semibold text-clinical-ink">{value}</span>
        {unit && <span className="pb-1 text-sm text-slate-500">{unit}</span>}
      </div>
    </div>
  );
}
