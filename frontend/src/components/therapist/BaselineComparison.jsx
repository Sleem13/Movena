import { ArrowDownRight, ArrowRight, ArrowUpRight, GitCompareArrows } from "lucide-react";
import { useLocale } from "../../i18n/LocaleContext.jsx";
import { Badge, Card, EmptyState } from "../common/UI.jsx";

function scorePosition(value) {
  return `${Math.max(0, Math.min(100, Number(value) || 0))}%`;
}

function DeltaIcon({ delta }) {
  if (delta > 0) return <ArrowUpRight size={17} aria-hidden="true" />;
  if (delta < 0) return <ArrowDownRight size={17} aria-hidden="true" />;
  return <ArrowRight size={17} aria-hidden="true" />;
}

export default function BaselineComparison({ comparisons = [] }) {
  const { t, exerciseText, locale } = useLocale();
  const formatDate = (value) => value
    ? new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(new Date(value))
    : "—";

  return <Card className="p-5 sm:p-6">
    <div className="flex items-start gap-3">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-teal-50 text-clinical-teal ring-1 ring-teal-100"><GitCompareArrows size={19} /></span>
      <div><h2 className="font-bold text-clinical-ink">{t("therapist.baselineComparison")}</h2><p className="mt-1 max-w-3xl text-xs leading-5 text-slate-500">{t("therapist.baselineHelp")}</p></div>
    </div>
    {comparisons.length ? <div className="mt-5 divide-y divide-clinical-line border-y border-clinical-line">
      {comparisons.map((item) => {
        const delta = item.score_delta;
        return <article key={item.exercise_id} className="py-5 first:pt-4 last:pb-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-bold text-clinical-ink">{exerciseText(item.exercise_id).name}</h3>
            <Badge tone="blue">{t(item.scored_session_count === 1 ? "therapist.scoredSession" : "therapist.scoredSessions", { count: item.scored_session_count })}</Badge>
          </div>
          {item.has_comparison ? <>
            <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
              <div className="rounded-xl bg-slate-50 px-4 py-3"><p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">{t("therapist.baseline")}</p><div className="mt-1 flex items-end justify-between gap-3"><strong className="text-2xl text-clinical-ink">{item.baseline_movement_score}</strong><span className="text-xs text-slate-500">{formatDate(item.baseline_date)}</span></div></div>
              <div className="rounded-xl bg-blue-50 px-4 py-3"><p className="text-[11px] font-bold uppercase tracking-wider text-blue-600">{t("therapist.latest")}</p><div className="mt-1 flex items-end justify-between gap-3"><strong className="text-2xl text-clinical-ink">{item.latest_movement_score}</strong><span className="text-xs text-slate-500">{formatDate(item.latest_date)}</span></div></div>
              <div className="flex min-w-28 items-center justify-center gap-2 rounded-xl border border-clinical-line px-4 py-3 text-clinical-blue"><DeltaIcon delta={delta} /><div><p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{t("therapist.observedChange")}</p><strong className="text-lg">{delta > 0 ? "+" : ""}{delta}</strong></div></div>
            </div>
            <div role="img" aria-label={t("therapist.comparisonAria", { exercise: exerciseText(item.exercise_id).name, baseline: item.baseline_movement_score, latest: item.latest_movement_score })} className="relative mx-2 mt-5 h-7">
              <div className="absolute inset-x-0 top-3 h-1 rounded-full bg-slate-100" />
              <div className="absolute top-3 h-1 rounded-full bg-gradient-to-r from-clinical-teal to-clinical-blue" style={{ left: scorePosition(Math.min(item.baseline_movement_score, item.latest_movement_score)), right: scorePosition(100 - Math.max(item.baseline_movement_score, item.latest_movement_score)) }} />
              <span className="absolute top-1.5 h-4 w-4 -translate-x-1/2 rounded-full border-2 border-white bg-clinical-teal shadow" style={{ left: scorePosition(item.baseline_movement_score) }} />
              <span className="absolute top-1 h-5 w-5 -translate-x-1/2 rounded-full border-[3px] border-white bg-clinical-blue shadow" style={{ left: scorePosition(item.latest_movement_score) }} />
            </div>
            {item.reps_delta != null ? <p className="mt-2 text-xs text-slate-500">{t("therapist.repsComparison", { baseline: item.baseline_total_reps, latest: item.latest_total_reps, delta: item.reps_delta > 0 ? `+${item.reps_delta}` : item.reps_delta })}</p> : null}
          </> : <div className="mt-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-4"><p className="text-sm font-semibold text-clinical-ink">{item.scored_session_count ? t("therapist.needAnotherSession") : t("therapist.noScoredExerciseSessions")}</p><p className="mt-1 text-xs text-slate-500">{item.scored_session_count ? t("therapist.currentBaseline", { score: item.baseline_movement_score, date: formatDate(item.baseline_date) }) : t("therapist.scoreRequired")}</p></div>}
        </article>;
      })}
    </div> : <div className="mt-5"><EmptyState compact icon={GitCompareArrows} title={t("therapist.noBaselineData")} description={t("therapist.noBaselineHelp")} /></div>}
    <p className="mt-4 text-[11px] leading-5 text-slate-500">{t("therapist.baselineDisclaimer")}</p>
  </Card>;
}
