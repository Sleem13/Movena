import { BarChart3, TrendingUp } from "lucide-react";

const CHART_WIDTH = 640;
const CHART_HEIGHT = 220;
const CHART_PADDING = { top: 22, right: 22, bottom: 32, left: 42 };

function scorePoints(sessions) {
  const scored = sessions
    .filter((item) => item.movement_score != null && Number.isFinite(Number(item.movement_score)))
    .slice(0, 8)
    .reverse();
  const chartWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const chartHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;
  return scored.map((item, index) => ({
    ...item,
    score: Number(item.movement_score),
    x: CHART_PADDING.left + (scored.length === 1 ? chartWidth / 2 : index * chartWidth / (scored.length - 1)),
    y: CHART_PADDING.top + chartHeight * (1 - Number(item.movement_score) / 100),
  }));
}

export function SessionScoreChart({ emptyLabel, label, sessions }) {
  const points = scorePoints(sessions);
  if (!points.length) return <div className="grid min-h-52 place-items-center rounded-xl border border-dashed border-slate-200 bg-slate-50/60 px-6 text-center text-sm text-slate-500">{emptyLabel}</div>;
  const path = points.map((point, index) => `${index ? "L" : "M"}${point.x},${point.y}`).join(" ");
  const area = `${path} L${points.at(-1).x},${CHART_HEIGHT - CHART_PADDING.bottom} L${points[0].x},${CHART_HEIGHT - CHART_PADDING.bottom} Z`;
  return <div className="min-w-0" aria-label={label}>
    <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-label={label} className="h-auto w-full overflow-visible">
      <defs>
        <linearGradient id="score-area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2563eb" stopOpacity="0.2" /><stop offset="1" stopColor="#2563eb" stopOpacity="0" /></linearGradient>
      </defs>
      {[0, 50, 100].map((value) => {
        const y = CHART_PADDING.top + (CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom) * (1 - value / 100);
        return <g key={value}><line x1={CHART_PADDING.left} x2={CHART_WIDTH - CHART_PADDING.right} y1={y} y2={y} stroke="var(--chart-grid)" strokeDasharray="4 6" /><text x={CHART_PADDING.left - 10} y={y + 4} textAnchor="end" fill="var(--chart-label)" className="text-[11px]">{value}</text></g>;
      })}
      <path d={area} fill="url(#score-area)" />
      <path d={path} fill="none" stroke="#2563eb" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      {points.map((point) => <g key={point.session_id}>
        <circle cx={point.x} cy={point.y} r="7" fill="var(--chart-point)" stroke="var(--brand-teal)" strokeWidth="4"><title>{`${point.exercise_display_name || point.exercise_id}: ${point.score}`}</title></circle>
        <text x={point.x} y={point.y - 14} textAnchor="middle" className="fill-clinical-ink text-[11px] font-bold">{Math.round(point.score)}</text>
      </g>)}
    </svg>
  </div>;
}

export function DistributionBars({ emptyLabel, entries, label, labelForKey, tone = "blue" }) {
  const sorted = Object.entries(entries || {}).sort((a, b) => b[1] - a[1]).slice(0, 7);
  if (!sorted.length) return <div className="grid min-h-44 place-items-center rounded-xl border border-dashed border-slate-200 bg-slate-50/60 px-6 text-center text-sm text-slate-500">{emptyLabel}</div>;
  const max = Math.max(...sorted.map(([, count]) => count), 1);
  const fill = tone === "amber" ? "from-amber-300 to-amber-500" : "from-blue-500 to-teal-400";
  return <div role="img" aria-label={label} className="space-y-4">
    {sorted.map(([key, count]) => <div key={key}>
      <div className="mb-1.5 flex items-center justify-between gap-3 text-xs"><span className="truncate font-semibold text-slate-700">{labelForKey(key)}</span><span className="font-bold tabular-nums text-clinical-ink">{count}</span></div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100"><span className={`block h-full rounded-full bg-gradient-to-r ${fill}`} style={{ width: `${Math.max(8, count / max * 100)}%` }} /></div>
    </div>)}
  </div>;
}

export function VisualizationHeading({ description, icon = "trend", title }) {
  const Icon = icon === "bars" ? BarChart3 : TrendingUp;
  return <div className="mb-5 flex items-start justify-between gap-4"><div><h2 className="font-bold text-clinical-ink">{title}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{description}</p></div><span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-blue-50 text-clinical-blue"><Icon size={18} /></span></div>;
}
