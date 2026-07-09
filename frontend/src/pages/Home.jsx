import { ArrowRight, BrainCircuit } from "lucide-react";

export default function Home({ onStart }) {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-80px)] w-full max-w-6xl items-center px-6 py-10">
      <section className="grid w-full gap-8 lg:grid-cols-[1fr_360px] lg:items-center">
        <div>
          <div className="mb-5 inline-flex items-center gap-2 rounded-lg border border-clinical-line bg-white px-3 py-2 text-sm font-medium text-clinical-teal">
            <BrainCircuit size={17} aria-hidden="true" />
            Sprint 1 Squat Analyzer MVP
          </div>
          <h1 className="max-w-3xl text-4xl font-semibold leading-tight text-clinical-ink md:text-5xl">
            PhysioVision AI
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
            Upload a bodyweight squat video and receive a rule-based computer vision report with rep count, joint angle estimates, movement flags, and patient-friendly feedback.
          </p>
          <button
            type="button"
            onClick={onStart}
            className="mt-7 inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-clinical-teal px-5 text-sm font-semibold text-white transition hover:bg-teal-800"
          >
            Analyze Squat Video
            <ArrowRight size={18} aria-hidden="true" />
          </button>
        </div>

        <aside className="rounded-lg border border-clinical-line bg-white p-6 shadow-panel">
          <h2 className="text-base font-semibold text-clinical-ink">MVP report includes</h2>
          <dl className="mt-5 space-y-4">
            <div>
              <dt className="text-sm font-medium text-slate-800">Pose-based metrics</dt>
              <dd className="mt-1 text-sm text-slate-600">Knee, hip, and trunk angle estimates.</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-slate-800">Movement quality</dt>
              <dd className="mt-1 text-sm text-slate-600">Depth, trunk lean, knee alignment, and consistency flags.</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-slate-800">Safety-first feedback</dt>
              <dd className="mt-1 text-sm text-slate-600">Educational guidance with a clinical disclaimer.</dd>
            </div>
          </dl>
        </aside>
      </section>
    </main>
  );
}
