import { Activity, ArrowRight, Clock3, ShieldCheck, Video } from "lucide-react";
import { Badge, Button, Card } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";

function ExerciseCard({ exercise, onAnalyze }) {
  const supported = exercise.supported_in_app;
  return <Card className={`group flex h-full flex-col overflow-hidden p-5 transition duration-200 ${supported ? "hover:-translate-y-1 hover:shadow-lift" : "bg-slate-50/70 opacity-90"}`}>
    <div className={`-mx-5 -mt-5 mb-5 h-1 ${supported ? "bg-gradient-to-r from-clinical-blue to-clinical-teal" : "bg-slate-200"}`} />
    <div className="flex items-start justify-between gap-3"><span className={`grid h-12 w-12 place-items-center rounded-2xl transition ${supported ? "bg-blue-50 text-clinical-blue group-hover:bg-clinical-blue group-hover:text-white" : "bg-slate-100 text-slate-400"}`}><Activity size={21} /></span><Badge tone={supported ? "teal" : "slate"}>{supported ? "Supported" : "Planned — not available yet"}</Badge></div>
    <h2 className="mt-4 text-lg font-bold text-clinical-ink">{exercise.display_name}</h2>
    <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-clinical-teal">{exercise.body_region} · {exercise.exercise_family}</p>
    <p className="mt-3 flex items-start gap-2 text-sm text-slate-600"><Video className="mt-0.5 shrink-0" size={16} />{exercise.recommended_camera_view}</p>
    <p className="mt-3 text-sm leading-6 text-slate-600">{exercise.movement_description}</p>
    <p className="mt-3 flex items-start gap-2 text-xs leading-5 text-slate-500"><ShieldCheck className="mt-0.5 shrink-0" size={15} />{exercise.safety_notes}</p>
    <div className="mt-auto pt-5">{supported ? <Button className="w-full" onClick={() => onAnalyze(exercise.exercise_id)}>Analyze this exercise <ArrowRight size={16} /></Button> : <Button className="w-full" variant="secondary" disabled><Clock3 size={16} />Not available</Button>}</div>
  </Card>;
}

export default function ExerciseLibrary({ exercises, onAnalyze }) {
  const supported = exercises.filter((item) => item.supported_in_app);
  const planned = exercises.filter((item) => !item.supported_in_app);
  return <main className="mx-auto w-full max-w-7xl px-6 py-12">
    <PageHeader eyebrow="Exercise library" title="Choose a supported movement" description="Five rule-based analyzers are available. Manual selection remains primary; planned exercises cannot be analyzed yet." />
    <section aria-labelledby="supported-exercises"><div className="flex items-center justify-between gap-4"><div><h2 id="supported-exercises" className="text-xl font-bold text-clinical-ink">Supported exercises</h2><p className="mt-1 text-sm text-slate-500">Available for rule-based video analysis now.</p></div><Badge tone="teal">{supported.length} available</Badge></div><div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{supported.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div></section>
    <section className="mt-14 border-t border-slate-200 pt-10" aria-labelledby="planned-exercises"><div className="flex items-center justify-between gap-4"><div><h2 id="planned-exercises" className="text-xl font-bold text-clinical-ink">Planned exercises</h2><p className="mt-1 text-sm text-slate-500">Roadmap coverage only; these analyzers are not active.</p></div><Badge tone="slate">{planned.length} planned</Badge></div><div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{planned.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div></section>
  </main>;
}
