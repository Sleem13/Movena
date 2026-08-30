import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  FlaskConical,
  Gauge,
  LoaderCircle,
  Play,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { PageHeader } from "../components/layout/AppShell.jsx";
import {
  createRehabRlAssessment,
  getRehabRlExercises,
  getRehabRlInspector,
  getRehabRlOverview,
  getRehabRlTrainingStatus,
  restoreRehabRlCheckpoint,
  simulateRehabRlTrajectory,
  startRehabRlTraining,
} from "../services/api.js";

const DEFAULT_INJURIES = [
  "ACL Tear",
  "Rotator Cuff Tear",
  "Lumbar Disc Herniation",
  "Ankle Sprain",
  "Tennis Elbow",
  "Patellofemoral Syndrome",
  "Hip Labral Tear",
  "Achilles Tendinopathy",
  "Shoulder Impingement",
  "Plantar Fasciitis",
  "Cervical Strain",
  "Hamstring Strain",
];
const STAGES = ["Acute", "Subacute", "Remodeling", "Functional", "Return"];

const initialAssessment = {
  injury_type: "ACL Tear",
  recovery_stage: 1,
  injury_severity: 0.7,
  pain_level: 0.5,
  rom: 0.6,
  strength: 0.55,
  movement_quality: 0.55,
  fatigue: 0.3,
  adherence: 0.85,
};

function requestMessage(error) {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    "The RehabRL service is unavailable."
  );
}

function Loading({ label }) {
  return (
    <div className="grid min-h-56 place-items-center rounded-2xl border border-slate-200 bg-white">
      <div className="flex items-center gap-3 text-sm font-semibold text-slate-600">
        <LoaderCircle className="animate-spin text-blue-600" size={20} />
        {label}
      </div>
    </div>
  );
}

function ErrorNotice({ message }) {
  return (
    <div role="alert" className="flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      <AlertTriangle className="mt-0.5 shrink-0" size={19} />
      <span>{message}</span>
    </div>
  );
}

function Metric({ label, value, detail }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-[#071b4a]">{value}</p>
      {detail ? <p className="mt-1 text-xs text-slate-500">{detail}</p> : null}
    </div>
  );
}

function RangeField({ label, value, onChange }) {
  return (
    <label className="block rounded-xl border border-slate-200 bg-slate-50/60 p-3.5">
      <span className="mb-2 flex items-center justify-between text-sm font-semibold text-slate-700">
        {label}
        <strong className="text-blue-700">{Math.round(value * 100)}%</strong>
      </span>
      <input
        className="w-full accent-blue-600"
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function TrajectoryChart({ rows }) {
  const paths = useMemo(() => {
    if (!rows?.length) return {};
    const width = 720;
    const height = 250;
    const point = (row, index, key) => {
      const x = 38 + (index / Math.max(1, rows.length - 1)) * (width - 58);
      const y = 18 + (1 - Number(row[key]) / 100) * (height - 50);
      return `${index ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`;
    };
    return Object.fromEntries(
      ["rom", "strength", "pain"].map((key) => [
        key,
        rows.map((row, index) => point(row, index, key)).join(" "),
      ]),
    );
  }, [rows]);
  if (!rows?.length) return null;
  return (
    <div className="max-w-full overflow-x-auto">
      <div className="mb-3 flex gap-5 text-xs font-semibold text-slate-600">
        {[["#2563eb", "Range of motion"], ["#0f766e", "Strength"], ["#e11d48", "Pain"]].map(([color, label]) => (
          <span key={label} className="flex items-center gap-2"><i className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />{label}</span>
        ))}
      </div>
      <svg viewBox="0 0 720 250" className="block min-w-[620px] max-w-none" role="img" aria-label="Simulated recovery trajectory">
        {[0, 25, 50, 75, 100].map((tick) => {
          const y = 18 + (1 - tick / 100) * 200;
          return <g key={tick}><line x1="38" x2="700" y1={y} y2={y} stroke="#e2e8f0" /><text x="30" y={y + 4} textAnchor="end" fontSize="11" fill="#64748b">{tick}</text></g>;
        })}
        <path d={paths.rom} fill="none" stroke="#2563eb" strokeWidth="3" />
        <path d={paths.strength} fill="none" stroke="#0f766e" strokeWidth="3" />
        <path d={paths.pain} fill="none" stroke="#e11d48" strokeWidth="3" />
      </svg>
    </div>
  );
}

function OverviewTab({ data, loading, error, onSelectTab }) {
  if (loading) return <Loading label="Loading policy overview" />;
  if (error) return <ErrorNotice message={error} />;
  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Policy" value={data.metrics.algorithm} detail="Reinforcement learning architecture" />
        <Metric label="State features" value={data.metrics.state_features} detail="Patient and recovery signals" />
        <Metric label="Clinical actions" value={data.metrics.clinical_actions} detail="Stage-aware prescription templates" />
        <Metric label="Policy source" value={data.signals.policy_source || "Clinical heuristic"} detail={`${data.signals.backend || "CPU"} · ${data.signals.device || "local runtime"}`} />
      </div>
      <section className="grid min-w-0 gap-5 xl:grid-cols-[1.4fr_.8fr]">
        <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div><h2 className="font-bold text-[#071b4a]">Recovery trajectory signal</h2><p className="mt-1 text-sm text-slate-500">Reference policy behavior from recent training history.</p></div>
            <Activity className="text-teal-700" size={21} />
          </div>
          <TrajectoryChart rows={data.trajectory} />
        </div>
        <div className="rounded-2xl bg-[#071b4a] p-6 text-white shadow-sm">
          <Sparkles className="text-cyan-300" size={24} />
          <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-blue-200">Decision-support workflow</p>
          <h2 className="mt-2 text-xl font-bold">Generate a stage-aware recommendation</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">Combine pain, mobility, strength, fatigue, adherence, and recovery stage into a reviewable prescription candidate.</p>
          <button onClick={() => onSelectTab("assessment")} className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-xl bg-white px-4 text-sm font-bold text-[#071b4a] hover:bg-blue-50"><Play size={17} />Start assessment</button>
        </div>
      </section>
    </div>
  );
}

function AssessmentTab({ injuries }) {
  const [form, setForm] = useState(initialAssessment);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault();
    setLoading(true); setError(""); setResult(null);
    try { setResult(await createRehabRlAssessment(form)); }
    catch (requestError) { setError(requestMessage(requestError)); }
    finally { setLoading(false); }
  }
  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
      <form onSubmit={submit} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="text-lg font-bold text-[#071b4a]">Patient state</h2>
        <p className="mt-1 text-sm text-slate-500">Enter clinician-reviewed normalized measures.</p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-semibold text-slate-700">Injury type<select value={form.injury_type} onChange={(event) => update("injury_type", event.target.value)} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal">{injuries.map((item) => <option key={item}>{item}</option>)}</select></label>
          <label className="text-sm font-semibold text-slate-700">Recovery stage<select value={form.recovery_stage} onChange={(event) => update("recovery_stage", Number(event.target.value))} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal">{STAGES.map((item, index) => <option key={item} value={index}>{item}</option>)}</select></label>
          {[["injury_severity", "Injury severity"], ["pain_level", "Pain level"], ["rom", "Range of motion"], ["strength", "Strength"], ["movement_quality", "Movement quality"], ["fatigue", "Fatigue"], ["adherence", "Adherence"]].map(([key, label]) => <RangeField key={key} label={label} value={form[key]} onChange={(value) => update(key, value)} />)}
        </div>
        {error ? <div className="mt-4"><ErrorNotice message={error} /></div> : null}
        <button disabled={loading} className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60">{loading ? <LoaderCircle className="animate-spin" size={18} /> : <BrainCircuit size={18} />}{loading ? "Evaluating policy" : "Generate recommendation"}</button>
      </form>
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        {!result ? <div className="grid min-h-[28rem] place-items-center text-center"><div><Gauge className="mx-auto text-slate-300" size={44} /><h2 className="mt-4 font-bold text-[#071b4a]">Recommendation preview</h2><p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">A prescription candidate, risk level, rationale, and exercise set will appear here for clinical review.</p></div></div> : <div className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-teal-700">{result.source}</p><h2 className="mt-1 text-xl font-bold text-[#071b4a]">{result.prescription.name}</h2></div><span className={`rounded-full px-3 py-1.5 text-xs font-bold ${result.risk === "High" ? "bg-red-100 text-red-700" : result.risk === "Moderate" ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-700"}`}>{result.risk} risk</span></div>
          <div className="grid grid-cols-2 gap-3"><Metric label="Confidence" value={`${result.confidence}%`} /><Metric label="Stage" value={result.prescription.stage} /></div>
          <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-bold uppercase tracking-wide text-slate-500">Rationale</p><p className="mt-2 text-sm leading-6 text-slate-700">{result.prescription.rationale}</p></div>
          <dl className="grid grid-cols-2 gap-3 text-sm">{[["Intensity", result.prescription.intensity], ["Frequency", result.prescription.frequency], ["Duration", result.prescription.duration], ["Rest", result.prescription.rest]].map(([label, value]) => <div key={label} className="rounded-xl border border-slate-200 p-3"><dt className="text-xs font-semibold text-slate-500">{label}</dt><dd className="mt-1 font-bold text-slate-800">{value}</dd></div>)}</dl>
          <div><h3 className="font-bold text-[#071b4a]">Suggested exercises</h3><div className="mt-3 space-y-2">{result.prescription.exercises.map((exercise) => <div key={exercise.name} className="flex items-start gap-3 rounded-xl border border-slate-200 p-3"><CheckCircle2 className="mt-0.5 shrink-0 text-teal-600" size={18} /><div><p className="text-sm font-bold text-slate-800">{exercise.name}</p><p className="mt-1 text-xs leading-5 text-slate-500">{exercise.sets} sets · {exercise.reps} · {exercise.cue}</p></div></div>)}</div></div>
        </div>}
      </section>
    </div>
  );
}

function SimulationTab({ injuries }) {
  const [form, setForm] = useState({ injury_type: "ACL Tear", injury_severity: 0.7, recovery_stage: 0, sessions: 40 });
  const [result, setResult] = useState(null); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event) { event.preventDefault(); setLoading(true); setError(""); try { setResult(await simulateRehabRlTrajectory(form)); } catch (requestError) { setError(requestMessage(requestError)); } finally { setLoading(false); } }
  return <div className="space-y-5"><form onSubmit={submit} className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-4 md:items-end"><label className="text-sm font-semibold text-slate-700">Injury<select value={form.injury_type} onChange={(event) => setForm({ ...form, injury_type: event.target.value })} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal">{injuries.map((item) => <option key={item}>{item}</option>)}</select></label><label className="text-sm font-semibold text-slate-700">Starting stage<select value={form.recovery_stage} onChange={(event) => setForm({ ...form, recovery_stage: Number(event.target.value) })} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal">{STAGES.map((item, index) => <option key={item} value={index}>{item}</option>)}</select></label><label className="text-sm font-semibold text-slate-700">Sessions<input type="number" min="5" max="100" value={form.sessions} onChange={(event) => setForm({ ...form, sessions: Number(event.target.value) })} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal" /></label><button disabled={loading} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60">{loading ? <LoaderCircle className="animate-spin" size={18} /> : <FlaskConical size={18} />}Run simulation</button></form>{error ? <ErrorNotice message={error} /> : null}{result ? <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div className="mb-5 grid gap-3 sm:grid-cols-3"><Metric label="Sessions simulated" value={result.sessions} /><Metric label="Total reward" value={result.total_reward} /><Metric label="Return stage reached" value={result.recovered ? "Yes" : "No"} /></div><TrajectoryChart rows={result.trajectory} /><p className="mt-4 text-xs leading-5 text-slate-500">Synthetic projection for model evaluation only. It is not a forecast of an individual patient’s outcome.</p></section> : <div className="grid min-h-64 place-items-center rounded-2xl border border-dashed border-slate-300 bg-white text-center"><div><FlaskConical className="mx-auto text-slate-300" size={40} /><p className="mt-3 font-bold text-slate-700">Configure and run a synthetic recovery trajectory</p></div></div>}</div>;
}

function LibraryTab({ data, loading, error }) {
  const [query, setQuery] = useState(""); const [category, setCategory] = useState("All"); const [selected, setSelected] = useState(null);
  useEffect(() => { if (data?.items?.length) setSelected((current) => current || data.items[0]); }, [data]);
  const filtered = useMemo(() => data?.items?.filter((item) => (category === "All" || item.category === category) && `${item.name} ${item.description}`.toLowerCase().includes(query.toLowerCase())) || [], [data, query, category]);
  if (loading) return <Loading label="Loading prescription exercise library" />; if (error) return <ErrorNotice message={error} />;
  return <div className="space-y-4"><div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row"><label className="flex min-h-11 flex-1 items-center gap-2 rounded-xl border border-slate-300 px-3"><Search size={18} className="text-slate-400" /><input aria-label="Search RehabRL exercises" className="w-full outline-none" placeholder="Search exercises" value={query} onChange={(event) => setQuery(event.target.value)} /></label><select aria-label="Exercise category" value={category} onChange={(event) => setCategory(event.target.value)} className="min-h-11 rounded-xl border border-slate-300 bg-white px-3">{["All", ...data.categories].map((item) => <option key={item}>{item}</option>)}</select></div><div className="grid gap-5 xl:grid-cols-[1fr_.8fr]"><div className="grid content-start gap-2 sm:grid-cols-2">{filtered.map((exercise) => <button key={exercise.name} onClick={() => setSelected(exercise)} className={`rounded-xl border p-4 text-left transition ${selected?.name === exercise.name ? "border-blue-300 bg-blue-50 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-blue-200"}`}><p className="font-bold text-[#071b4a]">{exercise.name}</p><p className="mt-1 text-xs font-semibold text-teal-700">{exercise.category} · {exercise.intensity}</p><p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">{exercise.description}</p></button>)}</div><aside className="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:sticky xl:top-24">{selected ? <><span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">{selected.category}</span><h2 className="mt-4 text-xl font-bold text-[#071b4a]">{selected.name}</h2><p className="mt-2 text-sm leading-6 text-slate-600">{selected.description}</p><dl className="mt-5 grid grid-cols-2 gap-3 text-sm">{[["Prescription", `${selected.sets} sets · ${selected.reps}`], ["Intensity", selected.intensity], ["Pain ceiling", `${selected.pain_limit} / 10`], ["Stages", `${selected.stage_min + 1}–${selected.stage_max + 1}`]].map(([label, value]) => <div key={label} className="rounded-xl bg-slate-50 p-3"><dt className="text-xs text-slate-500">{label}</dt><dd className="mt-1 font-bold text-slate-800">{value}</dd></div>)}</dl><div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4"><p className="text-xs font-bold uppercase tracking-wide text-blue-700">Clinical cue</p><p className="mt-2 text-sm leading-6 text-slate-700">{selected.cue}</p></div></> : null}</aside></div></div>;
}

function OperationsTab() {
  const [inspector, setInspector] = useState(null); const [status, setStatus] = useState(null); const [error, setError] = useState(""); const [episodes, setEpisodes] = useState(100); const [busy, setBusy] = useState(false);
  async function refresh() { try { const [nextInspector, nextStatus] = await Promise.all([getRehabRlInspector(), getRehabRlTrainingStatus()]); setInspector(nextInspector); setStatus(nextStatus); setError(""); } catch (requestError) { setError(requestMessage(requestError)); } }
  useEffect(() => { refresh(); }, []);
  useEffect(() => { if (!status || !["starting", "running"].includes(status.state)) return undefined; const timer = setInterval(() => getRehabRlTrainingStatus().then(setStatus).catch((requestError) => setError(requestMessage(requestError))), 1500); return () => clearInterval(timer); }, [status?.state]);
  async function restore() { setBusy(true); setError(""); try { await restoreRehabRlCheckpoint(); await refresh(); } catch (requestError) { setError(requestMessage(requestError)); } finally { setBusy(false); } }
  async function train() { setBusy(true); setError(""); try { setStatus(await startRehabRlTraining({ episodes, max_steps: 50, learning_rate: 0.0003, gamma: 0.96, batch_size: 128, use_mhealth: false })); } catch (requestError) { setError(requestMessage(requestError)); } finally { setBusy(false); } }
  if (!inspector && !error) return <Loading label="Inspecting RehabRL model" />;
  return <div className="space-y-5">{error ? <ErrorNotice message={error} /> : null}<div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Backend" value={inspector?.stats?.backend || "—"} /><Metric label="Device" value={inspector?.stats?.device || "—"} /><Metric label="Episodes" value={inspector?.stats?.episodes ?? "—"} /><Metric label="Parameters" value={Number(inspector?.stats?.n_params || 0).toLocaleString()} /></div><section className="grid gap-5 xl:grid-cols-2"><div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><div className="flex items-start justify-between"><div><h2 className="font-bold text-[#071b4a]">Model lifecycle</h2><p className="mt-1 text-sm text-slate-500">Super-admin controls for the embedded policy.</p></div><ShieldCheck className="text-blue-600" /></div><div className="mt-5 rounded-xl bg-slate-50 p-4"><div className="flex justify-between text-sm"><span className="font-semibold text-slate-600">Training state</span><strong className="capitalize text-[#071b4a]">{status?.state || "idle"}</strong></div><div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200"><div className="h-full bg-blue-600 transition-all" style={{ width: `${Math.round((status?.progress || 0) * 100)}%` }} /></div><p className="mt-2 text-xs text-slate-500">{status?.message}</p></div><label className="mt-5 block text-sm font-semibold text-slate-700">Training episodes<input type="number" min="1" max="1000" value={episodes} onChange={(event) => setEpisodes(Number(event.target.value))} className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal" /></label><div className="mt-4 grid gap-3 sm:grid-cols-2"><button onClick={restore} disabled={busy || ["starting", "running"].includes(status?.state)} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-300 px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"><RefreshCw size={17} />Restore checkpoint</button><button onClick={train} disabled={busy || ["starting", "running"].includes(status?.state)} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"><Play size={17} />Start training</button></div></div><div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h2 className="font-bold text-[#071b4a]">Network architecture</h2><div className="mt-5 space-y-3">{inspector?.architecture?.map((layer, index) => <div key={layer.name} className="flex items-center gap-3 rounded-xl border border-slate-200 p-3"><span className="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-sm font-bold text-blue-700">{index + 1}</span><div><p className="text-sm font-bold text-slate-800">{layer.name}</p><p className="text-xs text-slate-500">{layer.shape}</p></div></div>)}</div></div></section></div>;
}

export default function RehabRlWorkspace({ user }) {
  const [tab, setTab] = useState("overview");
  const [overview, setOverview] = useState(null); const [library, setLibrary] = useState(null); const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  useEffect(() => { let active = true; Promise.all([getRehabRlOverview(), getRehabRlExercises()]).then(([nextOverview, nextLibrary]) => { if (active) { setOverview(nextOverview); setLibrary(nextLibrary); } }).catch((requestError) => { if (active) setError(requestMessage(requestError)); }).finally(() => { if (active) setLoading(false); }); return () => { active = false; }; }, []);
  const tabs = [{ id: "overview", label: "Overview", icon: Activity }, { id: "assessment", label: "Assessment", icon: BrainCircuit }, { id: "simulation", label: "Simulation", icon: FlaskConical }, { id: "library", label: "Policy exercises", icon: BookOpen }, ...(user?.role === "super_admin" ? [{ id: "operations", label: "Model operations", icon: ShieldCheck }] : [])];
  const injuries = library?.injuries || DEFAULT_INJURIES;
  return <main className="mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8"><PageHeader eyebrow="Clinical decision support" title="RehabRL policy workspace" description="Review stage-aware rehabilitation recommendations and synthetic recovery trajectories inside PhysioVision AI." /><div className="mb-5 flex gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900"><AlertTriangle className="mt-0.5 shrink-0" size={19} /><p><strong>Clinician review required.</strong> RehabRL outputs are experimental decision support, not autonomous prescriptions, diagnoses, or patient-specific outcome forecasts.</p></div><div className="mb-6 overflow-x-auto"><div className="inline-flex min-w-full gap-1 rounded-xl border border-slate-200 bg-white p-1 shadow-sm sm:min-w-0">{tabs.map(({ id, label, icon: Icon }) => <button key={id} onClick={() => setTab(id)} aria-current={tab === id ? "page" : undefined} className={`inline-flex min-h-11 flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-lg px-4 text-sm font-bold transition ${tab === id ? "bg-[#071b4a] text-white" : "text-slate-600 hover:bg-slate-50"}`}><Icon size={17} />{label}</button>)}</div></div>{tab === "overview" ? <OverviewTab data={overview} loading={loading} error={error} onSelectTab={setTab} /> : null}{tab === "assessment" ? <AssessmentTab injuries={injuries} /> : null}{tab === "simulation" ? <SimulationTab injuries={injuries} /> : null}{tab === "library" ? <LibraryTab data={library} loading={loading} error={error} /> : null}{tab === "operations" && user?.role === "super_admin" ? <OperationsTab /> : null}</main>;
}
