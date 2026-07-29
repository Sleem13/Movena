import { Activity, ArrowRight, Clock3, Search, ShieldCheck, SlidersHorizontal, Video, X } from "lucide-react";
import { Badge, Button, Card, EmptyState } from "../components/common/UI.jsx";
import { useMemo, useState } from "react";
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
  const [query, setQuery] = useState("");
  const [availability, setAvailability] = useState("all");
  const [bodyRegion, setBodyRegion] = useState("all");
  const bodyRegions = useMemo(() => Array.from(new Set(exercises.map((item) => item.body_region))).sort(), [exercises]);
  const filteredExercises = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return exercises.filter((item) => {
      const matchesQuery = !normalizedQuery || [
        item.display_name,
        item.body_region,
        item.exercise_family,
        item.movement_description,
        item.recommended_camera_view,
      ].some((value) => String(value).toLowerCase().includes(normalizedQuery));
      const matchesAvailability = availability === "all" || (availability === "supported" ? item.supported_in_app : !item.supported_in_app);
      const matchesBodyRegion = bodyRegion === "all" || item.body_region === bodyRegion;
      return matchesQuery && matchesAvailability && matchesBodyRegion;
    });
  }, [availability, bodyRegion, exercises, query]);
  const supported = filteredExercises.filter((item) => item.supported_in_app);
  const planned = filteredExercises.filter((item) => !item.supported_in_app);
  const hasActiveFilters = query || availability !== "all" || bodyRegion !== "all";
  function resetFilters() { setQuery(""); setAvailability("all"); setBodyRegion("all"); }
  return <main className="mx-auto w-full max-w-7xl px-6 py-12">
    <PageHeader eyebrow="Exercise library" title="Choose a supported movement" description="Five rule-based analyzers are available. Manual selection remains primary; planned exercises cannot be analyzed yet." />
    <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft" aria-label="Exercise filters">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px_220px_auto]">
        <label className="relative block">
          <span className="sr-only">Search exercises</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} aria-hidden="true" />
          <input value={query} onChange={(event) => setQuery(event.target.value)} className="h-11 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm text-clinical-ink placeholder:text-slate-400 focus:border-clinical-blue focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="Search by movement, region, or camera view" />
        </label>
        <label className="relative block">
          <span className="sr-only">Availability</span>
          <SlidersHorizontal className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} aria-hidden="true" />
          <select aria-label="Availability" value={availability} onChange={(event) => setAvailability(event.target.value)} className="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-8 text-sm font-semibold text-clinical-ink focus:border-clinical-blue focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100">
            <option value="all">All availability</option>
            <option value="supported">Supported only</option>
            <option value="planned">Planned only</option>
          </select>
        </label>
        <label className="block">
          <span className="sr-only">Body region</span>
          <select aria-label="Body region" value={bodyRegion} onChange={(event) => setBodyRegion(event.target.value)} className="h-11 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-semibold text-clinical-ink focus:border-clinical-blue focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100">
            <option value="all">All body regions</option>
            {bodyRegions.map((region) => <option key={region} value={region}>{region}</option>)}
          </select>
        </label>
        <Button type="button" variant="secondary" onClick={resetFilters} disabled={!hasActiveFilters} aria-label="Clear exercise filters"><X size={16} />Clear</Button>
      </div>
      <p className="mt-3 text-sm text-slate-500">{filteredExercises.length} {filteredExercises.length === 1 ? "exercise matches" : "exercises match"} your filters.</p>
    </section>
    {filteredExercises.length === 0 ? <EmptyState title="No exercises match" description="Clear filters or try a broader search term." /> : <>
      <section aria-labelledby="supported-exercises"><div className="flex items-center justify-between gap-4"><div><h2 id="supported-exercises" className="text-xl font-bold text-clinical-ink">Supported exercises</h2><p className="mt-1 text-sm text-slate-500">Available for rule-based video analysis now.</p></div><Badge tone="teal">{supported.length} available</Badge></div>{supported.length ? <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{supported.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div> : <EmptyState compact title="No supported exercises in this view" description="Adjust filters to include available analyzers." />}</section>
      <section className="mt-14 border-t border-slate-200 pt-10" aria-labelledby="planned-exercises"><div className="flex items-center justify-between gap-4"><div><h2 id="planned-exercises" className="text-xl font-bold text-clinical-ink">Planned exercises</h2><p className="mt-1 text-sm text-slate-500">Roadmap coverage only; these analyzers are not active.</p></div><Badge tone="slate">{planned.length} planned</Badge></div>{planned.length ? <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{planned.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onAnalyze={onAnalyze} />)}</div> : <EmptyState compact title="No planned exercises in this view" description="Adjust filters to include roadmap exercises." />}</section>
    </>}
  </main>;
}
