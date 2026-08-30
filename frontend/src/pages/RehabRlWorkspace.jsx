import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  Activity,
  AlertTriangle,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  ClipboardList,
  ExternalLink,
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
import ConditionCombobox from "../components/rehab/ConditionCombobox.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import {
  REHAB_CONDITION_AR,
  localizeRehabConditions,
  rehabText,
} from "../i18n/rehabRlMessages.js";
import {
  createRehabRlAssessment,
  getRehabRlExercises,
  getRehabRlInspector,
  getRehabRlGovernance,
  getRehabRlOverview,
  getRehabRlModelManifest,
  getRehabRlProtocols,
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
const RehabLocaleContext = createContext({
  locale: "en",
  tr: (value) => value,
});
function useRehabCopy() {
  return useContext(RehabLocaleContext);
}
function T({ children }) {
  const { tr } = useRehabCopy();
  const source = String(children).replace(/\s+/g, " ").trim();
  const translated = tr(source);
  if (/^[.,:%…·—]+$/.test(source) || /^[.,]/.test(source)) return translated;
  if (source.endsWith(":")) return <>{translated} </>;
  return <> {translated} </>;
}
const initialAssessment = {
  condition_id: "acl_tear",
  injury_type: "ACL Tear",
  recovery_stage: 1,
  injury_severity: 0.7,
  pain_level: 0.5,
  rom: 0.6,
  strength: 0.55,
  movement_quality: 0.55,
  fatigue: 0.3,
  adherence: 0.85,
  safety_screen: {
    red_flags_reviewed: false,
    red_flags_present: false,
    precautions_reviewed: false,
    postoperative: false,
    procedure_orders_confirmed: false,
    clinician_attestation: false,
  },
};
function requestMessage(error, tr = (value) => value) {
  return tr(
    error?.response?.data?.message ||
      error?.response?.data?.detail ||
      error?.message ||
      "The RehabRL service is unavailable.",
  );
}
function Loading({ label }) {
  const { tr } = useRehabCopy();
  return (
    <div className="grid min-h-56 place-items-center rounded-2xl border border-slate-200 bg-white">
      <div className="flex items-center gap-3 text-sm font-semibold text-slate-600">
        <LoaderCircle className="animate-spin text-blue-600" size={20} />
        {tr(label)}
      </div>
    </div>
  );
}
function ErrorNotice({ message }) {
  return (
    <div
      role="alert"
      className="flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
    >
      <AlertTriangle className="mt-0.5 shrink-0" size={19} />
      <span>{message}</span>
    </div>
  );
}
function Metric({ label, value, detail }) {
  const { tr } = useRehabCopy();
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">
        {tr(label)}
      </p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-[#071b4a]">
        {typeof value === "string" ? tr(value) : value}
      </p>
      {detail ? (
        <p className="mt-1 text-xs text-slate-500">{tr(detail)}</p>
      ) : null}
    </div>
  );
}
function RangeField({ label, value, onChange }) {
  const { tr } = useRehabCopy();
  return (
    <label className="block rounded-xl border border-slate-200 bg-slate-50/60 p-3.5">
      <span className="mb-2 flex items-center justify-between text-sm font-semibold text-slate-700">
        {tr(label)}
        <strong className="text-blue-700">
          {Math.round(value * 100)}
          <T>{"%"}</T>
        </strong>
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
  const { tr } = useRehabCopy();
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
        {[
          ["#2563eb", tr("Range of motion")],
          ["#0f766e", tr("Strength")],
          ["#e11d48", tr("Pain")],
        ].map(([color, label]) => (
          <span key={label} className="flex items-center gap-2">
            <i
              className="h-2.5 w-2.5 rounded-full"
              style={{
                background: color,
              }}
            />
            {label}
          </span>
        ))}
      </div>
      <svg
        viewBox="0 0 720 250"
        className="block min-w-[620px] max-w-none"
        role="img"
        aria-label={tr("Simulated recovery trajectory")}
      >
        {[0, 25, 50, 75, 100].map((tick) => {
          const y = 18 + (1 - tick / 100) * 200;
          return (
            <g key={tick}>
              <line x1="38" x2="700" y1={y} y2={y} stroke="#e2e8f0" />
              <text
                x="30"
                y={y + 4}
                textAnchor="end"
                fontSize="11"
                fill="#64748b"
              >
                {tick}
              </text>
            </g>
          );
        })}
        <path d={paths.rom} fill="none" stroke="#2563eb" strokeWidth="3" />
        <path d={paths.strength} fill="none" stroke="#0f766e" strokeWidth="3" />
        <path d={paths.pain} fill="none" stroke="#e11d48" strokeWidth="3" />
      </svg>
    </div>
  );
}
function MLOpsMonitoring({ governance }) {
  const { locale, tr } = useRehabCopy();
  if (!governance?.monitoring) return null;
  const monitoring = governance.monitoring;
  const topConditions = Object.entries(governance.conditions || {}).slice(0, 5);
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.12em] text-purple-700">
            <T>{"MLOps monitoring"}</T>
          </p>
          <h2 className="mt-1 font-bold text-[#071b4a]">
            <T>{"Coverage, abstention, and release controls"}</T>
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            <T>
              {
                "Observed decision-support usage is separated from performance claims that require labeled outcomes."
              }
            </T>
          </p>
        </div>
        <span className="rounded-full bg-purple-50 px-3 py-1.5 text-xs font-bold text-purple-700">
          <T>{"Automatic promotion disabled"}</T>
        </span>
      </div>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="text-xs text-slate-500">
            <T>{"Policy decisions"}</T>
          </dt>
          <dd className="mt-1 text-xl font-bold text-slate-800">
            {governance.policy_decisions}
          </dd>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="text-xs text-slate-500">
            <T>{"Abstentions / protocol-only"}</T>
          </dt>
          <dd className="mt-1 text-xl font-bold text-slate-800">
            {governance.abstentions}
          </dd>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="text-xs text-slate-500">
            <T>{"Abstention rate"}</T>
          </dt>
          <dd className="mt-1 text-xl font-bold text-slate-800">
            {Math.round(governance.abstention_rate * 100)}
            <T>{"%"}</T>
          </dd>
        </div>
      </dl>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 p-4">
          <h3 className="text-sm font-bold text-slate-800">
            <T>{"Decision coverage by condition"}</T>
          </h3>
          {topConditions.length ? (
            <ul className="mt-3 space-y-2 text-xs text-slate-600">
              {topConditions.map(([condition, count]) => (
                <li key={condition} className="flex justify-between gap-3">
                  <span>
                    {locale === "ar"
                      ? REHAB_CONDITION_AR[condition] ||
                        tr(condition.replaceAll("_", " "))
                      : condition.replaceAll("_", " ")}
                  </span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-xs text-slate-500">
              <T>{"No decisions in this window."}</T>
            </p>
          )}
        </div>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
          <h3 className="text-sm font-bold text-amber-900">
            <T>{"Evidence limits"}</T>
          </h3>
          <ul className="mt-3 list-disc space-y-2 ps-5 text-xs leading-5 text-amber-950">
            <li>
              <T>{"Drift:"}</T>
              {tr(monitoring.drift_status.replaceAll("_", " "))}
              <T>{"."}</T>
            </li>
            <li>
              <T>{"Subgroups:"}</T>{" "}
              {tr(monitoring.subgroup_monitoring_status.replaceAll("_", " "))}
              <T>{"."}</T>
            </li>
            <li>
              <T>{"Performance:"}</T>{" "}
              {tr(monitoring.performance_breakdown_status.replaceAll("_", " "))}
              <T>{"."}</T>
            </li>
          </ul>
        </div>
      </div>
      <p className="mt-4 text-xs font-semibold text-slate-600">
        <T>{"Rollback:"}</T>
        {tr(monitoring.rollback_control)}
        <T>{". Clinical approval required before release."}</T>
      </p>
    </section>
  );
}
function OverviewTab({
  data,
  manifest,
  governance,
  loading,
  error,
  onSelectTab,
}) {
  const { tr } = useRehabCopy();
  if (loading) return <Loading label="Loading policy overview" />;
  if (error) return <ErrorNotice message={error} />;
  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="Policy"
          value={data.metrics.algorithm}
          detail="Reinforcement learning architecture"
        />
        <Metric
          label="State features"
          value={data.metrics.state_features}
          detail="Patient and recovery signals"
        />
        <Metric
          label="Clinical actions"
          value={data.metrics.clinical_actions}
          detail="Stage-aware prescription templates"
        />
        <Metric
          label="Policy source"
          value={data.signals.policy_source || "Clinical heuristic"}
          detail={`${data.signals.backend || "CPU"} · ${data.signals.device || "local runtime"}`}
        />
      </div>
      <section className="grid min-w-0 gap-5 xl:grid-cols-[1.4fr_.8fr]">
        <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2 className="font-bold text-[#071b4a]">
                <T>{"Recovery trajectory signal"}</T>
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                <T>
                  {"Reference policy behavior from recent training history."}
                </T>
              </p>
            </div>
            <Activity className="text-teal-700" size={21} />
          </div>
          <TrajectoryChart rows={data.trajectory} />
        </div>
        <div className="rounded-2xl bg-[#071b4a] p-6 text-white shadow-sm">
          <Sparkles className="text-cyan-300" size={24} />
          <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-blue-200">
            <T>{"Decision-support workflow"}</T>
          </p>
          <h2 className="mt-2 text-xl font-bold">
            <T>{"Generate a stage-aware recommendation"}</T>
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            <T>
              {
                "Combine pain, mobility, strength, fatigue, adherence, and recovery stage into a reviewable prescription candidate."
              }
            </T>
          </p>
          <button
            onClick={() => onSelectTab("assessment")}
            className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-xl bg-white px-4 text-sm font-bold text-[#071b4a] hover:bg-blue-50"
          >
            <Play size={17} />
            <T>{"Start assessment"}</T>
          </button>
        </div>
      </section>
      {manifest ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-blue-700">
                <T>{"Model governance"}</T>
              </p>
              <h2 className="mt-1 font-bold text-[#071b4a]">
                <T>{"Immutable inference contract"}</T>
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                <T>
                  {
                    "Only the checkpoint's versioned 12-label state space can reach policy inference."
                  }
                </T>
              </p>
            </div>
            <span
              className={`rounded-full px-3 py-1.5 text-xs font-bold ${manifest.checkpoint.compatible ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}
            >
              {tr(
                manifest.checkpoint.compatible
                  ? "Contract compatible"
                  : "Inference disabled",
              )}
            </span>
          </div>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Contract"}</T>
              </dt>
              <dd className="mt-1 font-bold text-slate-800">
                {manifest.contract.version}
              </dd>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Dimensions"}</T>
              </dt>
              <dd className="mt-1 font-bold text-slate-800">
                {manifest.contract.state_dim}
                <T>{"states \xB7"}</T> {manifest.contract.action_dim}
                <T>{"actions"}</T>
              </dd>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Fingerprint"}</T>
              </dt>
              <dd
                className="mt-1 truncate font-mono text-xs font-bold text-slate-800"
                title={manifest.contract.sha256}
              >
                {manifest.contract.sha256.slice(0, 16)}
                <T>{"\u2026"}</T>
              </dd>
            </div>
          </dl>
        </section>
      ) : null}
      {governance ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-teal-700">
                <T>{"Clinical governance"}</T>
              </p>
              <h2 className="mt-1 font-bold text-[#071b4a]">
                <T>{"Traceable decision support"}</T>
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                <T>
                  {
                    "Privacy-minimized decision events support safety review and lifecycle monitoring."
                  }
                </T>
              </p>
            </div>
            <span className="rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700">
              <T>{"Audit logging active"}</T>
            </span>
          </div>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Decisions \xB7"}</T>
                {governance.window_days}
                <T>{"days"}</T>
              </dt>
              <dd className="mt-1 text-xl font-bold text-slate-800">
                {governance.decisions}
              </dd>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Safety holds"}</T>
              </dt>
              <dd className="mt-1 text-xl font-bold text-slate-800">
                {governance.safety_holds}
              </dd>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <dt className="text-xs text-slate-500">
                <T>{"Referral holds"}</T>
              </dt>
              <dd className="mt-1 text-xl font-bold text-slate-800">
                {governance.referrals}
              </dd>
            </div>
          </dl>
          <div
            className={`mt-4 rounded-xl border p-4 ${governance.escalation.configured ? "border-emerald-100 bg-emerald-50" : "border-amber-100 bg-amber-50"}`}
          >
            <p
              className={`text-xs font-bold uppercase tracking-wide ${governance.escalation.configured ? "text-emerald-800" : "text-amber-900"}`}
            >
              {tr(
                governance.escalation.configured
                  ? "Escalation contact configured"
                  : "Escalation contact requires configuration",
              )}
            </p>
            <p className="mt-1 text-sm leading-6 text-slate-700">
              {tr(governance.escalation.instruction)}
            </p>
            {governance.escalation.contact ? (
              <p className="mt-1 text-sm font-bold text-slate-800">
                {governance.escalation.organization}
                <T>{":"}</T> {governance.escalation.contact}
              </p>
            ) : null}
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">
            {tr(governance.audit.privacy_profile)}
            <T>{"."}</T>
          </p>
        </section>
      ) : null}
      <MLOpsMonitoring governance={governance} />
    </div>
  );
}
function AssessmentTab({ conditions, onDecisionLogged }) {
  const { tr } = useRehabCopy();
  const [form, setForm] = useState(initialAssessment);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = (key, value) =>
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  const updateSafety = (key, value) =>
    setForm((current) => ({
      ...current,
      safety_screen: {
        ...current.safety_screen,
        [key]: value,
      },
    }));
  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const nextResult = await createRehabRlAssessment(form);
      setResult(nextResult);
      onDecisionLogged?.();
    } catch (requestError) {
      setError(requestMessage(requestError, tr));
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
      <form
        onSubmit={submit}
        className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
      >
        <h2 className="text-lg font-bold text-[#071b4a]">
          <T>{"Patient state"}</T>
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          <T>{"Enter clinician-reviewed normalized measures."}</T>
        </p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <ConditionCombobox
            conditions={conditions}
            label={tr("Condition or diagnosis")}
            placeholder={tr("Search condition or diagnosis")}
            emptyMessage={tr("No matching condition")}
            value={form.condition_id}
            onChange={(condition) => {
              setForm((current) => ({
                ...current,
                condition_id: condition.id,
                injury_type: condition.rl_injury_type || current.injury_type,
                safety_screen: {
                  ...initialAssessment.safety_screen,
                },
              }));
              setResult(null);
              setError("");
            }}
          />
          <label className="text-sm font-semibold text-slate-700">
            <T>{"Recovery stage"}</T>
            <select
              value={form.recovery_stage}
              onChange={(event) =>
                update("recovery_stage", Number(event.target.value))
              }
              className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 bg-white px-3 font-normal"
            >
              {STAGES.map((item, index) => (
                <option key={item} value={index}>
                  {tr(item)}
                </option>
              ))}
            </select>
          </label>
          {[
            ["injury_severity", "Injury severity"],
            ["pain_level", "Pain level"],
            ["rom", "Range of motion"],
            ["strength", "Strength"],
            ["movement_quality", "Movement quality"],
            ["fatigue", "Fatigue"],
            ["adherence", "Adherence"],
          ].map(([key, label]) => (
            <RangeField
              key={key}
              label={label}
              value={form[key]}
              onChange={(value) => update(key, value)}
            />
          ))}
        </div>
        <fieldset className="mt-5 rounded-2xl border border-blue-100 bg-blue-50/50 p-4">
          <legend className="px-2 text-sm font-bold text-[#071b4a]">
            <T>{"Mandatory clinical safety gate"}</T>
          </legend>
          <p className="mb-3 text-xs leading-5 text-slate-600">
            <T>
              {
                "Attest only after examination and review of the selected pathway's red flags and precautions."
              }
            </T>
          </p>
          <div className="space-y-2">
            {[
              [
                "red_flags_reviewed",
                "I reviewed the condition-specific red flags",
              ],
              [
                "precautions_reviewed",
                "I reviewed contraindications and precautions",
              ],
              ["postoperative", "This is a postoperative case"],
              ...(form.safety_screen.postoperative
                ? [
                    [
                      "procedure_orders_confirmed",
                      "I confirmed surgeon-specific loading, ROM, brace, and weight-bearing orders",
                    ],
                  ]
                : []),
              [
                "clinician_attestation",
                "I attest that a qualified clinician examined the patient and this pathway is appropriate",
              ],
            ].map(([key, label]) => (
              <label
                key={key}
                className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-3 text-sm font-medium text-slate-700"
              >
                <input
                  type="checkbox"
                  className="mt-0.5 h-4 w-4 accent-blue-600"
                  checked={form.safety_screen[key]}
                  onChange={(event) => updateSafety(key, event.target.checked)}
                />
                {tr(label)}
              </label>
            ))}
            <label className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-bold text-red-800">
              <input
                type="checkbox"
                className="mt-0.5 h-4 w-4 accent-red-600"
                checked={form.safety_screen.red_flags_present}
                onChange={(event) =>
                  updateSafety("red_flags_present", event.target.checked)
                }
              />
              <T>
                {
                  "A red flag is present \u2014 withhold treatment guidance and show referral action"
                }
              </T>
            </label>
          </div>
        </fieldset>
        {error ? (
          <div className="mt-4">
            <ErrorNotice message={error} />
          </div>
        ) : null}
        <button
          disabled={loading}
          className={`mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl px-4 text-sm font-bold text-white disabled:opacity-60 ${form.safety_screen.red_flags_present ? "bg-red-700 hover:bg-red-800" : "bg-blue-600 hover:bg-blue-700"}`}
        >
          {loading ? (
            <LoaderCircle className="animate-spin" size={18} />
          ) : (
            <BrainCircuit size={18} />
          )}
          {tr(
            loading
              ? "Evaluating safety and policy"
              : form.safety_screen.red_flags_present
                ? "Generate hold and referral guidance"
                : "Generate clinician-reviewed guidance",
          )}
        </button>
      </form>
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        {!result ? (
          <div className="grid min-h-[28rem] place-items-center text-center">
            <div>
              <Gauge className="mx-auto text-slate-300" size={44} />
              <h2 className="mt-4 font-bold text-[#071b4a]">
                <T>{"Recommendation preview"}</T>
              </h2>
              <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                <T>
                  {
                    "A prescription candidate, risk level, rationale, and exercise set will appear here for clinical review."
                  }
                </T>
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.12em] text-teal-700">
                  {result.source}
                </p>
                <h2 className="mt-1 text-xl font-bold text-[#071b4a]">
                  {result.prescription.name}
                </h2>
              </div>
              <span
                className={`rounded-full px-3 py-1.5 text-xs font-bold ${result.load_caution === "High" ? "bg-red-100 text-red-700" : result.load_caution === "Moderate" ? "bg-amber-100 text-amber-800" : result.load_caution === "Low" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-700"}`}
              >
                {result.load_caution || result.risk}
                <T>{"load caution"}</T>
              </span>
            </div>
            {result.mode === "safety_hold" ? (
              <div
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 p-4"
              >
                <p className="font-bold text-red-800">
                  <T>{"Treatment guidance is locked"}</T>
                </p>
                <p className="mt-1 text-sm leading-6 text-red-900">
                  {result.clinical_safety.message}
                </p>
              </div>
            ) : null}
            {result.decision_audit_id ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                  <T>{"Decision audit ID"}</T>
                </p>
                <p className="mt-1 break-all font-mono text-xs font-semibold text-slate-700">
                  {result.decision_audit_id}
                </p>
              </div>
            ) : null}
            <div className="grid grid-cols-2 gap-3">
              <Metric
                label={
                  result.mode === "rehabrl_policy"
                    ? "Policy confidence"
                    : "Decision mode"
                }
                value={
                  result.mode === "safety_hold"
                    ? "Safety hold"
                    : result.confidence == null
                      ? "Clinical reference"
                      : `${result.confidence}%`
                }
              />
              <Metric label="Stage" value={result.prescription.stage} />
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                <T>{"Rationale"}</T>
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {result.prescription.rationale}
              </p>
            </div>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Intensity", result.prescription.intensity],
                ["Frequency", result.prescription.frequency],
                ["Duration", result.prescription.duration],
                ["Rest", result.prescription.rest],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-xl border border-slate-200 p-3"
                >
                  <dt className="text-xs font-semibold text-slate-500">
                    {tr(label)}
                  </dt>
                  <dd className="mt-1 font-bold text-slate-800">{value}</dd>
                </div>
              ))}
            </dl>
            <div className="rounded-xl border border-teal-100 bg-teal-50/60 p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-teal-700">
                <T>{"Current phase goals"}</T>
              </p>
              <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
                {result.phase_plan.goals.map((item) => (
                  <li key={item} className="flex gap-2">
                    <CheckCircle2
                      className="mt-0.5 shrink-0 text-teal-600"
                      size={16}
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            {result.phase_plan.interventions.length ? (
              <div>
                <h3 className="font-bold text-[#071b4a]">
                  <T>{"Treatment options for clinician selection"}</T>
                </h3>
                <div className="mt-3 space-y-2">
                  {result.phase_plan.interventions.map((item) => (
                    <div
                      key={item}
                      className="flex items-start gap-3 rounded-xl border border-slate-200 p-3"
                    >
                      <CheckCircle2
                        className="mt-0.5 shrink-0 text-teal-600"
                        size={18}
                      />
                      <p className="text-sm leading-5 text-slate-700">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
            {result.prescription.exercises.length ? (
              <div>
                <h3 className="font-bold text-[#071b4a]">
                  <T>{"RehabRL exercise candidates"}</T>
                </h3>
                <div className="mt-3 space-y-2">
                  {result.prescription.exercises.map((exercise) => (
                    <div
                      key={exercise.name}
                      className="flex items-start gap-3 rounded-xl border border-slate-200 p-3"
                    >
                      <CheckCircle2
                        className="mt-0.5 shrink-0 text-teal-600"
                        size={18}
                      />
                      <div>
                        <p className="text-sm font-bold text-slate-800">
                          {exercise.name}
                        </p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          {exercise.sets}
                          <T>{"sets \xB7"}</T>
                          {exercise.reps}
                          <T>{"\xB7"}</T> {exercise.cue}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
            <div>
              <h3 className="font-bold text-[#071b4a]">
                <T>{"Progress only when"}</T>
              </h3>
              <ul className="mt-3 space-y-2">
                {result.phase_plan.progression_criteria.map((item) => (
                  <li
                    key={item}
                    className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div
              className={`rounded-xl border p-4 ${result.clinical_safety.red_flags_present ? "border-red-200 bg-red-50" : "border-amber-100 bg-amber-50"}`}
            >
              <p
                className={`text-xs font-bold uppercase tracking-wide ${result.clinical_safety.red_flags_present ? "text-red-700" : "text-amber-800"}`}
              >
                {tr(
                  result.clinical_safety.red_flags_present
                    ? "Positive red flag — hold and refer"
                    : result.clinical_safety.treatment_readiness ===
                        "procedure_orders_required"
                      ? "Procedure orders incomplete"
                      : result.clinical_safety.treatment_readiness ===
                          "clinician_attestation_required"
                        ? "Clinician attestation incomplete"
                        : result.clinical_safety.red_flags_screened
                          ? "Safety screen recorded"
                          : "Safety screen incomplete",
                )}
              </p>
              <p className="mt-1 text-xs leading-5 text-slate-800">
                {result.clinical_safety.message}
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-5 text-slate-800">
                {[
                  ...result.protocol.red_flags.slice(0, 3),
                  ...result.protocol.precautions,
                ].map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
function SimulationTab({ conditions }) {
  const { tr } = useRehabCopy();
  const [form, setForm] = useState({
    injury_type: "ACL Tear",
    injury_severity: 0.7,
    recovery_stage: 0,
    sessions: 40,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setResult(await simulateRehabRlTrajectory(form));
    } catch (requestError) {
      setError(requestMessage(requestError, tr));
    } finally {
      setLoading(false);
    }
  }
  const selected =
    conditions.find(
      (condition) => condition.rl_injury_type === form.injury_type,
    ) || conditions[0];
  return (
    <div className="space-y-5">
      <form
        onSubmit={submit}
        className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-4 md:items-end"
      >
        <ConditionCombobox
          conditions={conditions}
          label={tr("RL-supported condition")}
          placeholder={tr("Search condition or diagnosis")}
          emptyMessage={tr("No matching condition")}
          value={selected?.id}
          onChange={(condition) =>
            setForm({
              ...form,
              injury_type: condition.rl_injury_type,
            })
          }
        />
        <label className="text-sm font-semibold text-slate-700">
          <T>{"Starting stage"}</T>
          <select
            value={form.recovery_stage}
            onChange={(event) =>
              setForm({
                ...form,
                recovery_stage: Number(event.target.value),
              })
            }
            className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          >
            {STAGES.map((item, index) => (
              <option key={item} value={index}>
                {tr(item)}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-semibold text-slate-700">
          <T>{"Sessions"}</T>
          <input
            type="number"
            min="5"
            max="100"
            value={form.sessions}
            onChange={(event) =>
              setForm({
                ...form,
                sessions: Number(event.target.value),
              })
            }
            className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
          />
        </label>
        <button
          disabled={loading}
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? (
            <LoaderCircle className="animate-spin" size={18} />
          ) : (
            <FlaskConical size={18} />
          )}
          <T>{"Run simulation"}</T>
        </button>
      </form>
      {error ? <ErrorNotice message={error} /> : null}
      {result ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 grid gap-3 sm:grid-cols-3">
            <Metric label="Sessions simulated" value={result.sessions} />
            <Metric label="Total reward" value={result.total_reward} />
            <Metric
              label="Return stage reached"
              value={result.recovered ? "Yes" : "No"}
            />
          </div>
          <TrajectoryChart rows={result.trajectory} />
          <p className="mt-4 text-xs leading-5 text-slate-500">
            <T>
              {
                "Synthetic projection for model evaluation only. It is not a forecast of an individual patient\u2019s outcome."
              }
            </T>
          </p>
        </section>
      ) : (
        <div className="grid min-h-64 place-items-center rounded-2xl border border-dashed border-slate-300 bg-white text-center">
          <div>
            <FlaskConical className="mx-auto text-slate-300" size={40} />
            <p className="mt-3 font-bold text-slate-700">
              <T>{"Configure and run a synthetic recovery trajectory"}</T>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
function ProtocolsTab({ data, loading, error }) {
  const { locale, tr } = useRehabCopy();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [selectedId, setSelectedId] = useState(null);
  const categories = useMemo(
    () => ["All", ...new Set((data?.items || []).map((item) => item.category))],
    [data],
  );
  const filtered = useMemo(
    () =>
      (data?.items || []).filter(
        (item) =>
          (category === "All" || item.category === category) &&
          item.search_text.toLowerCase().includes(query.toLowerCase()),
      ),
    [data, query, category],
  );
  const selected =
    (data?.items || []).find((item) => item.id === selectedId) ||
    filtered[0] ||
    data?.items?.[0];
  if (loading) return <Loading label="Loading clinical protocol catalog" />;
  if (error) return <ErrorNotice message={error} />;
  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row">
        <label className="flex min-h-11 flex-1 items-center gap-2 rounded-xl border border-slate-300 px-3">
          <Search size={18} className="text-slate-400" />
          <input
            aria-label={tr("Search clinical protocols")}
            className="w-full outline-none"
            placeholder={tr(
              "Search condition, alias, body region, or category",
            )}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <select
          aria-label={tr("Protocol category")}
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="min-h-11 rounded-xl border border-slate-300 bg-white px-3"
        >
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>
      <div className="grid gap-5 xl:grid-cols-[.72fr_1.28fr]">
        <div className="grid content-start gap-2 sm:grid-cols-2 xl:grid-cols-1">
          {filtered.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className={`rounded-xl border p-4 text-left ${selected?.id === item.id ? "border-blue-300 bg-blue-50 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-blue-200"}`}
            >
              <div className="flex items-start justify-between gap-2">
                <p className="font-bold text-[#071b4a]">
                  {locale === "ar"
                    ? REHAB_CONDITION_AR[item.id] || item.name
                    : item.name}
                </p>
                {item.rl_supported ? (
                  <span className="rounded-full bg-cyan-50 px-2 py-1 text-[10px] font-bold text-cyan-700">
                    <T>{"RL supported"}</T>
                  </span>
                ) : null}
              </div>
              <p className="mt-1 text-xs font-semibold text-teal-700">
                {tr(item.category)}
                <T>{"\xB7"}</T>
                {tr(item.body_region)}
              </p>
              <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                {item.summary}
              </p>
            </button>
          ))}
        </div>
        {selected ? (
          <article className="h-fit rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-teal-700">
                  <T>{"Clinical protocol reference"}</T>
                </p>
                <h2 className="mt-1 text-2xl font-bold text-[#071b4a]">
                  {locale === "ar"
                    ? REHAB_CONDITION_AR[selected.id] || selected.name
                    : selected.name}
                </h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  {selected.summary}
                </p>
                <p className="mt-2 text-xs font-medium text-slate-500">
                  <T>{"Evidence reviewed"}</T>
                  {selected.evidence_reviewed_on}
                  <T>{"\xB7 Next review due"}</T>
                  {selected.next_review_due}
                </p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700">
                {selected.phases.length}
                <T>{"phases"}</T>
              </span>
            </div>
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div className="rounded-xl border border-red-100 bg-red-50 p-4">
                <h3 className="text-sm font-bold text-red-800">
                  <T>{"Red flags and referral screen"}</T>
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-5 text-red-900">
                  {selected.red_flags.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl border border-amber-100 bg-amber-50 p-4">
                <h3 className="text-sm font-bold text-amber-900">
                  <T>{"Precautions"}</T>
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-5 text-amber-950">
                  {selected.precautions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <h3 className="mt-6 font-bold text-[#071b4a]">
              <T>{"Criteria-based plan"}</T>
            </h3>
            <div className="mt-3 space-y-3">
              {selected.phases.map((phase) => (
                <details
                  key={phase.stage}
                  className="rounded-xl border border-slate-200 p-4"
                  open={phase.stage === 0}
                >
                  <summary className="cursor-pointer list-none font-bold text-slate-800">
                    <span className="mr-2 inline-grid h-7 w-7 place-items-center rounded-lg bg-blue-50 text-xs text-blue-700">
                      {phase.stage + 1}
                    </span>
                    {phase.name}
                    <span className="ml-2 text-xs font-normal text-slate-500">
                      {phase.typical_timing}
                    </span>
                  </summary>
                  <div className="mt-4 grid gap-4 md:grid-cols-3">
                    {[
                      ["Goals", phase.goals],
                      ["Interventions", phase.interventions],
                      ["Progression criteria", phase.progression_criteria],
                    ].map(([heading, items]) => (
                      <div key={heading}>
                        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                          {tr(heading)}
                        </p>
                        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-5 text-slate-700">
                          {items.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </details>
              ))}
            </div>
            <div className="mt-6">
              <h3 className="font-bold text-[#071b4a]">
                <T>{"Recommended outcome tracking"}</T>
              </h3>
              <div className="mt-2 flex flex-wrap gap-2">
                {selected.outcome_measures.map((item) => (
                  <span
                    key={item}
                    className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-6 border-t border-slate-200 pt-4">
              <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                <T>{"Evidence sources"}</T>
              </p>
              <div className="mt-2 flex flex-wrap gap-3">
                {selected.sources.map((source) => (
                  <a
                    key={source.url}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:underline"
                  >
                    {source.title}
                    <ExternalLink size={12} />
                  </a>
                ))}
              </div>
            </div>
          </article>
        ) : null}
      </div>
    </div>
  );
}
function LibraryTab({ data, loading, error }) {
  const { tr } = useRehabCopy();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    if (data?.items?.length) setSelected((current) => current || data.items[0]);
  }, [data]);
  const filtered = useMemo(
    () =>
      data?.items?.filter(
        (item) =>
          (category === "All" || item.category === category) &&
          `${item.name} ${item.description}`
            .toLowerCase()
            .includes(query.toLowerCase()),
      ) || [],
    [data, query, category],
  );
  if (loading) return <Loading label="Loading prescription exercise library" />;
  if (error) return <ErrorNotice message={error} />;
  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row">
        <label className="flex min-h-11 flex-1 items-center gap-2 rounded-xl border border-slate-300 px-3">
          <Search size={18} className="text-slate-400" />
          <input
            aria-label={tr("Search RehabRL exercises")}
            className="w-full outline-none"
            placeholder={tr("Search exercises")}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <select
          aria-label={tr("Exercise category")}
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="min-h-11 rounded-xl border border-slate-300 bg-white px-3"
        >
          {["All", ...data.categories].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>
      <div className="grid gap-5 xl:grid-cols-[1fr_.8fr]">
        <div className="grid content-start gap-2 sm:grid-cols-2">
          {filtered.map((exercise) => (
            <button
              key={exercise.name}
              onClick={() => setSelected(exercise)}
              className={`rounded-xl border p-4 text-left transition ${selected?.name === exercise.name ? "border-blue-300 bg-blue-50 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-blue-200"}`}
            >
              <p className="font-bold text-[#071b4a]">{exercise.name}</p>
              <p className="mt-1 text-xs font-semibold text-teal-700">
                {exercise.category}
                <T>{"\xB7"}</T>
                {exercise.intensity}
              </p>
              <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                {exercise.description}
              </p>
            </button>
          ))}
        </div>
        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:sticky xl:top-24">
          {selected ? (
            <>
              <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">
                {selected.category}
              </span>
              <h2 className="mt-4 text-xl font-bold text-[#071b4a]">
                {selected.name}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {selected.description}
              </p>
              <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
                {[
                  ["Prescription", `${selected.sets} sets · ${selected.reps}`],
                  ["Intensity", selected.intensity],
                  ["Pain ceiling", `${selected.pain_limit} / 10`],
                  [
                    "Stages",
                    `${selected.stage_min + 1}–${selected.stage_max + 1}`,
                  ],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-xl bg-slate-50 p-3">
                    <dt className="text-xs text-slate-500">{label}</dt>
                    <dd className="mt-1 font-bold text-slate-800">{value}</dd>
                  </div>
                ))}
              </dl>
              <div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4">
                <p className="text-xs font-bold uppercase tracking-wide text-blue-700">
                  <T>{"Clinical cue"}</T>
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  {selected.cue}
                </p>
              </div>
            </>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
function OperationsTab() {
  const [inspector, setInspector] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const [episodes, setEpisodes] = useState(100);
  const [busy, setBusy] = useState(false);
  async function refresh() {
    try {
      const [nextInspector, nextStatus] = await Promise.all([
        getRehabRlInspector(),
        getRehabRlTrainingStatus(),
      ]);
      setInspector(nextInspector);
      setStatus(nextStatus);
      setError("");
    } catch (requestError) {
      setError(requestMessage(requestError));
    }
  }
  useEffect(() => {
    refresh();
  }, []);
  useEffect(() => {
    if (!status || !["starting", "running"].includes(status.state))
      return undefined;
    const timer = setInterval(
      () =>
        getRehabRlTrainingStatus()
          .then(setStatus)
          .catch((requestError) => setError(requestMessage(requestError))),
      1500,
    );
    return () => clearInterval(timer);
  }, [status?.state]);
  async function restore() {
    setBusy(true);
    setError("");
    try {
      await restoreRehabRlCheckpoint();
      await refresh();
    } catch (requestError) {
      setError(requestMessage(requestError));
    } finally {
      setBusy(false);
    }
  }
  async function train() {
    setBusy(true);
    setError("");
    try {
      setStatus(
        await startRehabRlTraining({
          episodes,
          max_steps: 50,
          learning_rate: 0.0003,
          gamma: 0.96,
          batch_size: 128,
          use_mhealth: false,
        }),
      );
    } catch (requestError) {
      setError(requestMessage(requestError));
    } finally {
      setBusy(false);
    }
  }
  if (!inspector && !error) return <Loading label="Inspecting RehabRL model" />;
  return (
    <div className="space-y-5">
      {error ? <ErrorNotice message={error} /> : null}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Backend" value={inspector?.stats?.backend || "—"} />
        <Metric label="Device" value={inspector?.stats?.device || "—"} />
        <Metric label="Episodes" value={inspector?.stats?.episodes ?? "—"} />
        <Metric
          label="Parameters"
          value={Number(inspector?.stats?.n_params || 0).toLocaleString()}
        />
      </div>
      <section className="grid gap-5 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="font-bold text-[#071b4a]">
                <T>{"Model lifecycle"}</T>
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                <T>{"Super-admin controls for the embedded policy."}</T>
              </p>
            </div>
            <ShieldCheck className="text-blue-600" />
          </div>
          <div className="mt-5 rounded-xl bg-slate-50 p-4">
            <div className="flex justify-between text-sm">
              <span className="font-semibold text-slate-600">
                <T>{"Training state"}</T>
              </span>
              <strong className="capitalize text-[#071b4a]">
                {status?.state || "idle"}
              </strong>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full bg-blue-600 transition-all"
                style={{
                  width: `${Math.round((status?.progress || 0) * 100)}%`,
                }}
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">{status?.message}</p>
          </div>
          <label className="mt-5 block text-sm font-semibold text-slate-700">
            <T>{"Training episodes"}</T>
            <input
              type="number"
              min="1"
              max="1000"
              value={episodes}
              onChange={(event) => setEpisodes(Number(event.target.value))}
              className="mt-2 min-h-11 w-full rounded-xl border border-slate-300 px-3 font-normal"
            />
          </label>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <button
              onClick={restore}
              disabled={busy || ["starting", "running"].includes(status?.state)}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-300 px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              <RefreshCw size={17} />
              <T>{"Restore checkpoint"}</T>
            </button>
            <button
              onClick={train}
              disabled={busy || ["starting", "running"].includes(status?.state)}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <Play size={17} />
              <T>{"Start training"}</T>
            </button>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="font-bold text-[#071b4a]">
            <T>{"Network architecture"}</T>
          </h2>
          <div className="mt-5 space-y-3">
            {inspector?.architecture?.map((layer, index) => (
              <div
                key={layer.name}
                className="flex items-center gap-3 rounded-xl border border-slate-200 p-3"
              >
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-sm font-bold text-blue-700">
                  {index + 1}
                </span>
                <div>
                  <p className="text-sm font-bold text-slate-800">
                    {layer.name}
                  </p>
                  <p className="text-xs text-slate-500">{layer.shape}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
export default function RehabRlWorkspace({ user }) {
  const { locale, direction } = useLocale();
  const tr = useCallback((value) => rehabText(locale, value), [locale]);
  const localeContext = useMemo(
    () => ({
      locale,
      tr,
    }),
    [locale, tr],
  );
  const [tab, setTab] = useState("overview");
  const [overview, setOverview] = useState(null);
  const [library, setLibrary] = useState(null);
  const [protocols, setProtocols] = useState(null);
  const [manifest, setManifest] = useState(null);
  const [governance, setGovernance] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    Promise.all([
      getRehabRlOverview(),
      getRehabRlExercises(),
      getRehabRlProtocols(),
      getRehabRlModelManifest(),
      getRehabRlGovernance(),
    ])
      .then(
        ([
          nextOverview,
          nextLibrary,
          nextProtocols,
          nextManifest,
          nextGovernance,
        ]) => {
          if (active) {
            setOverview(nextOverview);
            setLibrary(nextLibrary);
            setProtocols(nextProtocols);
            setManifest(nextManifest);
            setGovernance(nextGovernance);
          }
        },
      )
      .catch((requestError) => {
        if (active) setError(requestMessage(requestError, tr));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [tr]);
  const refreshGovernance = () =>
    getRehabRlGovernance()
      .then(setGovernance)
      .catch(() => {});
  const tabs = [
    {
      id: "overview",
      label: tr("Overview"),
      icon: Activity,
    },
    {
      id: "assessment",
      label: tr("Assessment"),
      icon: BrainCircuit,
    },
    {
      id: "protocols",
      label: tr("Clinical protocols"),
      icon: ClipboardList,
    },
    {
      id: "simulation",
      label: tr("Simulation"),
      icon: FlaskConical,
    },
    {
      id: "library",
      label: tr("Policy exercises"),
      icon: BookOpen,
    },
    ...(user?.role === "super_admin"
      ? [
          {
            id: "operations",
            label: tr("Model operations"),
            icon: ShieldCheck,
          },
        ]
      : []),
  ];
  const conditions = useMemo(
    () => localizeRehabConditions(library?.conditions || [], locale),
    [library?.conditions, locale],
  );
  const rlConditions = conditions.filter((condition) => condition.rl_supported);
  return (
    <RehabLocaleContext.Provider value={localeContext}>
      <main
        dir={direction}
        className="mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8"
      >
        <PageHeader
          eyebrow={tr("Clinical decision support")}
          title={tr("Rehabilitation planning workspace")}
          description={tr(
            "Review criteria-based physical therapy protocols and trained-policy suggestions inside PhysioVision AI.",
          )}
        />
        <div className="mb-5 flex gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
          <AlertTriangle className="mt-0.5 shrink-0" size={19} />
          <p>
            <strong>{tr("Clinician review required.")}</strong>{" "}
            {tr(
              "Protocols are references, not diagnoses or autonomous prescriptions. Examine the patient, screen red flags, apply procedure-specific orders, and use shared decision-making before treatment.",
            )}
          </p>
        </div>
        <div className="mb-6 overflow-x-auto">
          <div className="inline-flex min-w-full gap-1 rounded-xl border border-slate-200 bg-white p-1 shadow-sm sm:min-w-0">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                aria-current={tab === id ? "page" : undefined}
                className={`inline-flex min-h-11 flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-lg px-4 text-sm font-bold transition ${tab === id ? "bg-[#071b4a] text-white" : "text-slate-600 hover:bg-slate-50"}`}
              >
                <Icon size={17} />
                {label}
              </button>
            ))}
          </div>
        </div>
        {tab === "overview" ? (
          <OverviewTab
            data={overview}
            manifest={manifest}
            governance={governance}
            loading={loading}
            error={error}
            onSelectTab={setTab}
          />
        ) : null}
        {tab === "assessment" ? (
          <AssessmentTab
            conditions={conditions}
            onDecisionLogged={refreshGovernance}
          />
        ) : null}
        {tab === "protocols" ? (
          <ProtocolsTab data={protocols} loading={loading} error={error} />
        ) : null}
        {tab === "simulation" ? (
          <SimulationTab conditions={rlConditions} />
        ) : null}
        {tab === "library" ? (
          <LibraryTab data={library} loading={loading} error={error} />
        ) : null}
        {tab === "operations" && user?.role === "super_admin" ? (
          <OperationsTab />
        ) : null}
      </main>
    </RehabLocaleContext.Provider>
  );
}
