import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Eye,
  FileText,
  LockKeyhole,
  Play,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from "lucide-react";
import { Badge, Button, Card } from "../components/common/UI.jsx";

const steps = [
  {
    icon: UploadCloud,
    number: "01",
    title: "Upload a clear video",
    description: "Choose a supported movement and follow the camera guide.",
  },
  {
    icon: Eye,
    number: "02",
    title: "Review movement signals",
    description: "Pose landmarks and explicit rules estimate reps, angles, and observations.",
  },
  {
    icon: FileText,
    number: "03",
    title: "Discuss the report",
    description: "Use the visual summary as educational support—not as a diagnosis.",
  },
];

export default function Home({ onStart }) {
  return (
    <main>
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_78%_24%,rgba(37,99,235,0.11),transparent_28%),radial-gradient(circle_at_12%_75%,rgba(15,143,131,0.09),transparent_24%)]" />
        <div className="relative mx-auto grid min-h-[680px] max-w-7xl items-center gap-14 px-6 py-16 lg:grid-cols-[1.04fr_.96fr] lg:py-20">
          <div>
            <Badge tone="teal">
              <ShieldCheck className="mr-1.5" size={14} aria-hidden="true" />
              Safety-first movement support
            </Badge>
            <h1 className="mt-7 max-w-3xl text-5xl font-extrabold leading-[1.04] tracking-[-0.045em] text-clinical-ink sm:text-6xl lg:text-7xl">
              Movement insight that is{" "}
              <span className="bg-gradient-to-r from-clinical-blue via-blue-500 to-clinical-teal bg-clip-text text-transparent">
                easier to understand.
              </span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Turn a short exercise video into a clear, rule-based movement
              report with visual review, angle trends, and practical recording
              guidance.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button type="button" aria-label="Analyze Squat Video" onClick={onStart} className="min-h-12 px-6">
                Start an analysis
                <ArrowRight size={18} aria-hidden="true" />
              </Button>
              <Button as="a" href="#how-it-works" variant="secondary" className="min-h-12 px-6">
                <Play size={17} aria-hidden="true" />
                See how it works
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-2"><CheckCircle2 size={15} className="text-clinical-teal" />Rule-based primary analysis</span>
              <span className="flex items-center gap-2"><CheckCircle2 size={15} className="text-clinical-teal" />No clinical claims</span>
              <span className="flex items-center gap-2"><LockKeyhole size={15} className="text-clinical-teal" />Temporary upload processing</span>
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-xl">
            <div className="absolute -inset-8 rounded-[2.5rem] bg-gradient-to-br from-blue-200/50 to-teal-100/60 blur-3xl" />
            <Card className="relative overflow-hidden p-3 shadow-lift">
              <div className="rounded-[1.3rem] bg-gradient-to-br from-clinical-navy via-[#164d72] to-[#0e746e] p-6 text-white sm:p-7">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-blue-200">Example session</p>
                    <p className="mt-2 text-2xl font-bold">Bodyweight squat</p>
                    <p className="mt-1 text-xs text-blue-100">Rule-based movement summary</p>
                  </div>
                  <Badge className="bg-white/15 text-white ring-white/20">Complete</Badge>
                </div>
                <div className="mt-8 grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                    <p className="text-xs text-blue-100">Movement score</p>
                    <p className="mt-2 text-4xl font-extrabold">88<span className="ml-1 text-sm font-medium text-blue-200">/100</span></p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                    <p className="text-xs text-blue-100">Completed reps</p>
                    <p className="mt-2 text-4xl font-extrabold">5</p>
                  </div>
                </div>
                <div className="mt-4 rounded-2xl border border-white/10 bg-white/10 p-4">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-blue-100">Knee angle trend</span>
                    <span className="text-teal-200">Live sample</span>
                  </div>
                  <div className="mt-5 flex h-28 items-end gap-2">
                    {[38, 58, 46, 82, 65, 91, 72, 88, 60, 78, 54, 84].map((height, index) => (
                      <span
                        key={index}
                        className="flex-1 rounded-t-md bg-gradient-to-t from-teal-300 to-blue-100 opacity-90"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="grid gap-2 p-3 sm:grid-cols-3">
                {[
                  [BarChart3, "Angle trends"],
                  [Sparkles, "Clear feedback"],
                  [FileText, "PDF export"],
                ].map(([Icon, label]) => (
                  <div key={label} className="flex items-center gap-2 rounded-xl bg-slate-50 p-3 text-xs font-semibold text-slate-700">
                    <Icon size={16} className="text-clinical-blue" />
                    {label}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-24 border-y border-slate-200/80 bg-white/70">
        <div className="mx-auto max-w-7xl px-6 py-16">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">How it works</p>
            <h2 className="mt-3 text-3xl font-extrabold tracking-tight text-clinical-ink">A clear path from recording to review</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">Designed to keep the workflow approachable for both patients and movement professionals.</p>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-3">
            {steps.map(({ icon: Icon, number, title, description }) => (
              <Card key={number} className="group relative overflow-hidden p-6 transition duration-200 hover:-translate-y-1 hover:shadow-lift">
                <span className="absolute right-5 top-4 text-5xl font-black text-slate-100">{number}</span>
                <span className="relative grid h-12 w-12 place-items-center rounded-2xl bg-blue-50 text-clinical-blue">
                  <Icon size={21} />
                </span>
                <h3 className="relative mt-5 text-lg font-bold text-clinical-ink">{title}</h3>
                <p className="relative mt-2 text-sm leading-6 text-slate-600">{description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="flex flex-col gap-6 rounded-[2rem] bg-clinical-ink p-7 text-white shadow-lift sm:flex-row sm:items-center sm:justify-between sm:p-9">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-teal-300">Important safety boundary</p>
            <h2 className="mt-3 text-2xl font-bold">Built to support a conversation—not replace clinical care.</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">Results are educational estimates and must not be used for diagnosis, treatment decisions, or emergency guidance.</p>
          </div>
          <Button type="button" onClick={onStart} className="shrink-0 bg-white text-clinical-ink hover:bg-blue-50">
            Analyze a video
            <ArrowRight size={17} />
          </Button>
        </div>
      </section>
    </main>
  );
}
