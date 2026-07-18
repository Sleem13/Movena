import { Activity, ArrowRight, Clock3, ShieldCheck, Video } from "lucide-react";
import { Badge, Button, Card } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";

function ExerciseCard({ exercise, onAnalyze }) {
  const supported = exercise.supported_in_app;
  return <Card className={`flex h-full flex-col p-5 ${supported ? "" : "bg-slate-50/70"}`}>
    <div className="flex items-start justify-between gap-3"><span className={`grid h-11 w-11 place-items-center rounded-xl ${supported ? "bg-blue-50 text-clinical-blue" : "bg-slate-100 text-slate-400"}`}><Activity size={21} /></span><Badge tone={supported ? "teal" : "slate"}>{supported ? "Supported" : "Planned — not available yet"}</Badge></div>
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
    <section aria-labelledby="supported-exercises"><h2 id="supported-exercises" className="text-xl font-bold">Supported exercises</h2><div className="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{supported.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div></section>
    <section className="mt-12" aria-labelledby="planned-exercises"><h2 id="planned-exercises" className="text-xl font-bold">Planned exercises</h2><p className="mt-2 text-sm text-slate-500">These cards describe roadmap coverage only and do not represent working analyzers.</p><div className="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{planned.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div></section>
  </main>;
}
