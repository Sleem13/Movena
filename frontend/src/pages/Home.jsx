import {
  ArrowRight,
  Check,
  FileText,
  MessageSquareText,
  PauseCircle,
  PlayCircle,
  ShieldCheck,
  TrendingUp,
  UploadCloud,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "../components/common/UI.jsx";
import ExercisePoseGraph, { getPoseMetrics } from "../components/exercises/ExercisePoseGraph.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

const TREND_POINTS = [42, 72, 54, 78, 66, 90];
const DEMO_DURATION_MS = 5200;

function ProductPreview({ t, squatName }) {
  const [playing, setPlaying] = useState(true);
  const [progress, setProgress] = useState(0);
  const elapsedRef = useRef(0);

  useEffect(() => {
    if (!playing) return undefined;
    let frameId;
    let previousTime = performance.now();
    const advance = (time) => {
      elapsedRef.current = (elapsedRef.current + (time - previousTime)) % DEMO_DURATION_MS;
      previousTime = time;
      setProgress(elapsedRef.current / DEMO_DURATION_MS);
      frameId = requestAnimationFrame(advance);
    };
    frameId = requestAnimationFrame(advance);
    return () => cancelAnimationFrame(frameId);
  }, [playing]);

  const metrics = getPoseMetrics("bodyweight_squat", progress);
  const movement = 0.5 - (Math.cos(progress * Math.PI * 2) / 2);
  const scanOpacity = Math.min(1, progress * 9, (1 - progress) * 9);
  return (
    <div className="landing-preview relative mx-auto min-w-0 w-full max-w-[650px]" aria-label={t("home.exampleSummary")}>
      <div className="grid min-w-0 overflow-hidden rounded-[22px] border border-slate-200 bg-white shadow-[0_28px_80px_rgba(7,27,74,0.15)] sm:grid-cols-[1.16fr_.84fr]">
        <div className="border-b border-slate-200 bg-slate-50 p-4 sm:border-b-0 sm:border-r sm:p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-extrabold text-clinical-ink">{squatName}</p>
              <p className="mt-1 text-xs text-slate-500">{t("home.exampleSummary")}</p>
            </div>
            <span className="inline-flex items-center gap-1.5 rounded-lg bg-clinical-mint px-2.5 py-1 text-[11px] font-bold text-clinical-teal">
              <Check size={13} strokeWidth={2.5} /> {t("home.complete")}
            </span>
          </div>
          <div className="relative mt-4 aspect-[4/3] overflow-hidden rounded-2xl border border-slate-200 bg-white p-3">
            <ExercisePoseGraph animated animationProgress={progress} exerciseId="bodyweight_squat" label={`${squatName} movement preview`} paused={!playing} supported />
            <span data-testid="analysis-scanner" className="pointer-events-none absolute inset-x-3 h-px bg-gradient-to-r from-transparent via-teal-400 to-transparent shadow-[0_0_12px_#2dd4bf]" style={{ opacity: scanOpacity, top: `${15 + (movement * 67)}%` }} />
            <span className="absolute left-3 top-3 rounded-lg border border-blue-100 bg-white/90 px-2 py-1 text-[10px] font-bold text-blue-700 shadow-sm backdrop-blur">{t("home.poseTracking")}</span>
            <div className="absolute bottom-3 right-3 flex flex-wrap justify-end gap-1.5 pl-3 text-[9px] font-extrabold sm:text-[10px]" aria-label={t("home.liveMeasurements")}>
              <span className="rounded-lg border border-teal-100 bg-white/92 px-2 py-1 text-clinical-teal shadow-sm backdrop-blur">{t("home.kneeLabel")} {metrics.knee}°</span>
              <span className="rounded-lg border border-blue-100 bg-white/92 px-2 py-1 text-blue-700 shadow-sm backdrop-blur">{t("home.hipLabel")} {metrics.hip}°</span>
              <span className="rounded-lg border border-slate-200 bg-white/92 px-2 py-1 text-slate-600 shadow-sm backdrop-blur">{t("home.trunkLabel")} {metrics.trunk}°</span>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-3 rounded-xl bg-clinical-ink px-3 py-2.5 text-white">
            <button type="button" onClick={() => setPlaying((value) => !value)} className="grid h-7 w-7 shrink-0 place-items-center rounded-full text-teal-300 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-200" aria-label={t(playing ? "home.pauseDemo" : "home.playDemo")}>{playing ? <PauseCircle size={19} /> : <PlayCircle size={19} />}</button>
            <span className="h-1 flex-1 overflow-hidden rounded-full bg-white/20"><span className="block h-full rounded-full bg-teal-300" style={{ width: `${6 + (progress * 94)}%` }} /></span>
            <span className="text-[10px] font-semibold text-blue-100">{t("home.liveAnalysis")}</span>
          </div>
        </div>
        <div className="min-w-0 p-4 sm:p-5">
          <p className="text-sm font-extrabold text-clinical-ink">{t("home.clearFeedback")}</p>
          <div className="mt-4 space-y-3">
            {[t("home.featureRule"), t("home.featureClaims")].map((label) => (
              <div key={label} className="flex gap-2.5 border-b border-slate-100 pb-3 text-xs leading-5 text-slate-600 last:border-0">
                <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border border-teal-200 bg-teal-50 text-clinical-teal"><Check size={12} strokeWidth={2.5} /></span>
                {label}
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-3.5">
            <div className="flex items-center justify-between text-[11px] font-bold">
              <span className="text-clinical-ink">{t("home.kneeTrend")}</span>
              <TrendingUp size={15} className="text-clinical-teal" />
            </div>
            <div className="mt-5 flex h-24 items-end gap-2 border-b border-l border-slate-200 px-1">
              {TREND_POINTS.map((height, index) => (
                <span key={index} className="relative flex-1" style={{ height: `${height}%` }}>
                  <span className="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-clinical-teal ring-4 ring-teal-50" />
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home({ authenticated = false, onStart }) {
  const { t, exerciseText } = useLocale();
  const squat = exerciseText("bodyweight_squat");
  const steps = [
    [UploadCloud, t("home.stepUploadTitle"), t("home.stepUploadDescription")],
    [TrendingUp, t("home.stepReviewTitle"), t("home.stepReviewDescription")],
    [MessageSquareText, t("home.stepDiscussTitle"), t("home.stepDiscussDescription")],
  ];
  const benefits = [
    [TrendingUp, t("home.angleTrends"), t("home.benefitTrends")],
    [MessageSquareText, t("home.clearFeedback"), t("home.benefitFeedback")],
    [FileText, t("home.pdfExport"), t("home.benefitReports")],
  ];

  return (
    <main className="overflow-hidden bg-white">
      <section className="relative border-b border-slate-100">
        <div className="hero-grid pointer-events-none absolute inset-0 opacity-70" />
        <div className="relative mx-auto grid min-h-[700px] max-w-[1400px] items-center gap-12 px-5 py-14 sm:px-8 lg:grid-cols-[.86fr_1.14fr] lg:px-12 lg:py-20">
          <div className="max-w-[610px]">
            <h1 className="text-balance text-[3.25rem] font-extrabold leading-[.98] tracking-[-0.055em] text-clinical-ink sm:text-[4.4rem] lg:text-[5rem]">
              {t("home.titlePrefix")} <span className="text-clinical-blue">{t("home.titleHighlight")}</span>
            </h1>
            <p className="mt-7 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">{t("home.description")}</p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button type="button" onClick={onStart} className="min-h-[52px] px-6 text-[15px]">
                {t(authenticated ? "home.openAnalyzer" : "home.getStarted")} <ArrowRight size={18} aria-hidden="true" />
              </Button>
              <Button as="a" href="#how-it-works" variant="secondary" className="min-h-[52px] px-6 text-[15px]">
                <PlayCircle size={18} aria-hidden="true" /> {t("home.how")}
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-xs font-semibold text-slate-500">
              {[t("home.featureRule"), t("home.featureClaims"), t("home.featureUploads")].map((label) => (
                <span key={label} className="flex items-center gap-2"><Check size={15} className="text-clinical-teal" />{label}</span>
              ))}
            </div>
          </div>
          <ProductPreview t={t} squatName={squat.name} />
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-24 bg-white">
        <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-balance text-3xl font-extrabold tracking-[-0.035em] text-clinical-ink sm:text-4xl">{t("home.howTitle")}</h2>
            <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">{t("home.howDescription")}</p>
          </div>
          <div className="relative mt-14 grid gap-10 md:grid-cols-3 md:gap-12">
            <div className="pointer-events-none absolute left-[16%] right-[16%] top-9 hidden border-t border-dashed border-teal-300 md:block" />
            {steps.map(([Icon, title, description], index) => (
              <article key={title} className="relative text-center md:text-left">
                <span className="relative mx-auto grid h-[74px] w-[74px] place-items-center rounded-[22px] border border-blue-100 bg-clinical-sky text-clinical-teal shadow-soft md:mx-0"><Icon size={28} strokeWidth={1.8} /></span>
                <p className="mt-7 text-xs font-extrabold tracking-[0.12em] text-clinical-teal">0{index + 1}</p>
                <h3 className="mt-2 text-lg font-extrabold text-clinical-ink">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="benefits" className="scroll-mt-24 bg-clinical-panel">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[.8fr_1.2fr] lg:py-24">
          <div>
            <h2 className="max-w-md text-balance text-3xl font-extrabold tracking-[-0.035em] text-clinical-ink sm:text-4xl">{t("home.benefitsTitle")}</h2>
            <div className="mt-9 space-y-7">
              {benefits.map(([Icon, title, description]) => (
                <div key={title} className="flex gap-4">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-teal-100 bg-white text-clinical-teal shadow-soft"><Icon size={20} /></span>
                  <div><h3 className="text-sm font-extrabold text-clinical-ink">{title}</h3><p className="mt-1.5 text-sm leading-6 text-slate-600">{description}</p></div>
                </div>
              ))}
            </div>
          </div>
          <div className="relative rounded-[24px] border border-blue-100 bg-[#eaf3ff] p-5 sm:p-8">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_18px_50px_rgba(7,27,74,0.1)] sm:p-7">
              <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-[11px] bg-gradient-to-br from-blue-600 to-teal-400 text-white"><TrendingUp size={18} /></span><div><p className="text-sm font-extrabold text-clinical-ink">{t("home.exampleSummary")}</p><p className="text-xs text-slate-500">{squat.name}</p></div></div>
              <div className="mt-7 grid gap-4 sm:grid-cols-[1fr_150px]"><div className="space-y-3"><span className="block h-3 w-4/5 rounded bg-slate-100" /><span className="block h-3 w-full rounded bg-slate-100" /><span className="block h-3 w-2/3 rounded bg-slate-100" /></div><div className="rounded-xl bg-clinical-sky p-4"><ShieldCheck className="text-clinical-teal" size={24} /><span className="mt-3 block h-2.5 w-full rounded bg-blue-100" /><span className="mt-2 block h-2.5 w-3/4 rounded bg-blue-100" /></div></div>
              <div className="mt-7 flex h-32 items-end gap-3 border-b border-l border-slate-200 px-3">{TREND_POINTS.map((height, index) => <span key={index} className="flex-1 rounded-t-sm bg-gradient-to-t from-blue-100 to-teal-400" style={{ height: `${height}%` }} />)}</div>
            </div>
          </div>
        </div>
      </section>

      <section id="safety" className="scroll-mt-24 bg-clinical-ink">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-12 text-white sm:px-8 md:grid-cols-[auto_1.15fr_.85fr] md:items-center lg:py-16">
          <span className="grid h-16 w-16 place-items-center rounded-2xl border border-teal-300/30 bg-teal-300/10 text-teal-300"><ShieldCheck size={31} strokeWidth={1.7} /></span>
          <h2 className="max-w-xl text-balance text-2xl font-extrabold tracking-[-0.025em] sm:text-3xl">{t("home.safetyTitle")}</h2>
          <p className="text-sm leading-7 text-blue-100">{t("home.safetyDescription")}</p>
        </div>
      </section>
    </main>
  );
}
