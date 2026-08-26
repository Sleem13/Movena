import { ArrowLeftRight, GitCompareArrows, LoaderCircle, X } from "lucide-react";
import { Badge, Button, Card } from "../common/UI.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const METRICS = [
  { key: "movement_score", label: "history.compareScore", unit: "/100", summaryKey: "movement_score" },
  { key: "total_reps", label: "history.compareReps", unit: "", summaryKey: "total_reps" },
  { key: "average_knee_angle", label: "history.compareKnee", unit: "°" },
  { key: "average_hip_angle", label: "history.compareHip", unit: "°" },
  { key: "average_trunk_angle", label: "history.compareTrunk", unit: "°" },
  { key: "average_shoulder_angle", label: "history.compareShoulder", unit: "°" },
  { key: "average_elbow_angle", label: "history.compareElbow", unit: "°" },
];

function metricValue(session, definition) {
  if (!session) return null;
  if (definition.summaryKey && session[definition.summaryKey] != null) return Number(session[definition.summaryKey]);
  const metric = session.metrics?.find((item) => item.metric_name === definition.key);
  return metric?.metric_value_float == null ? null : Number(metric.metric_value_float);
}

export function buildComparisonRows(sessions) {
  if (sessions.length !== 2) return [];
  const chronological = [...sessions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  return METRICS.flatMap((definition) => {
    const previous = metricValue(chronological[0], definition);
    const current = metricValue(chronological[1], definition);
    if (previous == null && current == null) return [];
    if (!definition.summaryKey && previous === 0 && current === 0) return [];
    return [{ ...definition, previous, current, delta: previous == null || current == null ? null : current - previous }];
  });
}

function formatValue(value, unit) {
  if (value == null || Number.isNaN(value)) return "—";
  const rounded = Number.isInteger(value) ? value : Math.round(value * 10) / 10;
  return `${rounded}${unit}`;
}

export default function SessionComparison({ selected, details, loading, error, onClear }) {
  const { locale, t, exerciseText } = useLocale();
  const ordered = [...details].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  const rows = buildComparisonRows(ordered);
  const dateFormatter = new Intl.DateTimeFormat(locale === "ar" ? "ar-EG" : "en-GB", { dateStyle: "medium", timeStyle: "short" });
  const waitingForDetails = selected.length === 2 && details.length !== 2 && !error;

  if (selected.length === 0) return null;

  return (
    <Card className="mb-5 overflow-hidden" aria-label={t("history.compareTitle")}>
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-clinical-line bg-clinical-sky/60 px-5 py-4">
        <div className="flex min-w-0 items-start gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-100 text-blue-700 ring-1 ring-blue-200">
            <GitCompareArrows size={19} aria-hidden="true" />
          </span>
          <div>
            <h2 className="font-bold text-clinical-ink">{t("history.compareTitle")}</h2>
            <p className="mt-0.5 text-xs leading-5 text-slate-500">
              {selected.length === 1 ? t("history.compareSelectSecond") : t("history.compareDescription")}
            </p>
          </div>
        </div>
        <Button variant="ghost" onClick={onClear} className="min-h-9 px-3"><X size={15} />{t("history.compareClear")}</Button>
      </div>

      {loading || waitingForDetails ? (
        <div className="flex min-h-36 items-center justify-center gap-2 p-5 text-sm text-slate-600" role="status">
          <LoaderCircle className="animate-spin" size={18} aria-hidden="true" />{t("history.compareLoading")}
        </div>
      ) : error ? (
        <p className="p-5 text-sm text-red-700" role="alert">{error}</p>
      ) : selected.length === 1 ? (
        <div className="p-5">
          <Badge tone="blue" className="tabular-nums" dir="ltr">1 / 2</Badge>
          <p className="mt-3 text-sm font-semibold text-clinical-ink">{exerciseText(selected[0].exercise_id).name}</p>
          <p className="mt-1 text-xs text-slate-500">{dateFormatter.format(new Date(selected[0].created_at))}</p>
        </div>
      ) : (
        <div className="p-5">
          <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-3 rounded-xl bg-slate-50 p-4 text-center">
            <div><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("history.compareEarlier")}</p><p className="mt-1 text-sm font-bold text-clinical-ink">{dateFormatter.format(new Date(ordered[0].created_at))}</p></div>
            <ArrowLeftRight className="text-blue-500" size={18} aria-hidden="true" />
            <div><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("history.compareLater")}</p><p className="mt-1 text-sm font-bold text-clinical-ink">{dateFormatter.format(new Date(ordered[1].created_at))}</p></div>
          </div>

          <div className="mt-4 divide-y divide-clinical-line rounded-xl border border-clinical-line">
            {rows.map((row) => {
              const delta = row.delta == null ? null : Math.round(row.delta * 10) / 10;
              return (
                <div key={row.key} className="grid grid-cols-[minmax(4.5rem,1fr)_minmax(5.5rem,1.2fr)_minmax(4.5rem,1fr)] items-center gap-2 px-3 py-3 text-sm sm:px-4">
                  <p className="font-semibold text-clinical-ink">{formatValue(row.previous, row.unit)}</p>
                  <div className="text-center">
                    <p className="text-xs font-semibold text-slate-500">{t(row.label)}</p>
                    {delta != null && <Badge tone={delta === 0 ? "slate" : delta > 0 ? "teal" : "amber"} className="mt-1" dir="ltr">{delta > 0 ? "+" : ""}{delta}{row.unit}</Badge>}
                  </div>
                  <p className="text-end font-semibold text-clinical-ink">{formatValue(row.current, row.unit)}</p>
                </div>
              );
            })}
          </div>
          <p className="mt-4 text-xs leading-5 text-slate-500">{t("history.compareDisclaimer")}</p>
        </div>
      )}
    </Card>
  );
}
