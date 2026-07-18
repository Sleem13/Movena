import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Plus,
  Stethoscope,
  Users,
} from "lucide-react";
import {
  createPatientProfile,
  getPatientProfile,
  getPatientProgress,
  getTherapistDashboard,
  listPatientProfiles,
  listPatientSessions,
} from "../services/api.js";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";

const WARNING =
  "Therapist dashboard is a protected development prototype. Do not use real patient data without production identity controls, consent, and privacy review.";
const pretty = (value = "") =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
const exerciseName = (value = "") => ({ bodyweight_squat: "Bodyweight Squat", sit_to_stand: "Sit-to-Stand", knee_extension: "Knee Extension", shoulder_abduction: "Shoulder Abduction", hip_abduction: "Hip Abduction" }[value] || pretty(value));

export default function TherapistDashboard() {
  const [view, setView] = useState(
    window.location.pathname === "/therapist/patients"
      ? "patients"
      : "dashboard",
  );
  const [dashboard, setDashboard] = useState(null);
  const [patients, setPatients] = useState([]);
  const [detail, setDetail] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [progress, setProgress] = useState(null);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [summary, profiles] = await Promise.all([
        getTherapistDashboard(),
        listPatientProfiles(),
      ]);
      setDashboard(summary);
      setPatients(profiles);
    } catch (requestError) {
      setError(
        requestError.response?.status === 403
          ? "You do not have permission to view this page."
          : requestError.response?.status === 401
            ? "Please log in to continue."
            : "Therapist dashboard data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
    const match = window.location.pathname.match(
      /^\/therapist\/patients\/([^/]+)$/,
    );
    if (match) openPatient(match[1]);
  }, []);

  async function createProfile(event) {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      await createPatientProfile({ display_name: name.trim() });
      setName("");
      await load();
      setView("patients");
    } catch {
      setError("Development profile could not be created.");
    }
  }

  async function openPatient(patientId) {
    setLoading(true);
    try {
      const [profile, patientSessions, patientProgress] = await Promise.all([
        getPatientProfile(patientId),
        listPatientSessions(patientId),
        getPatientProgress(patientId),
      ]);
      setDetail(profile);
      setSessions(patientSessions);
      setProgress(patientProgress);
      setView("detail");
      window.history.pushState({}, "", `/therapist/patients/${patientId}`);
    } catch {
      setError("Development profile details could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  const cards = dashboard
    ? [
        ["Total patients", dashboard.total_patients, Users],
        ["Total sessions", dashboard.total_sessions, Activity],
        [
          "Low-confidence sessions",
          dashboard.low_confidence_sessions,
          AlertTriangle,
        ],
        [
          "Most common issue",
          dashboard.common_detected_issues?.[0]
            ? pretty(dashboard.common_detected_issues[0].issue_code)
            : "None",
          Stethoscope,
        ],
      ]
    : [];
  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader
        eyebrow="Development prototype"
        title="Therapist dashboard"
        description="Review locally saved movement-analysis metadata and placeholder profiles."
      />
      <Alert
        tone="warning"
        title="Prototype dashboard for development use only"
      >
        {WARNING} Do not enter real patient-identifiable information. AI
        feedback supports exercise monitoring and does not replace licensed
        physiotherapist assessment.
      </Alert>
      <div className="my-5 flex flex-wrap gap-2">
        <Button
          variant={view === "dashboard" ? "primary" : "secondary"}
          onClick={() => setView("dashboard")}
        >
          Dashboard
        </Button>
        <Button
          variant={view === "patients" ? "primary" : "secondary"}
          onClick={() => setView("patients")}
        >
          Patient profiles
        </Button>
      </div>
      {error && <Alert title="Dashboard error">{error}</Alert>}
      {loading ? (
        <Card className="grid min-h-52 place-items-center">
          <LoadingSpinner label="Loading dashboard" />
        </Card>
      ) : view === "dashboard" ? (
        <div className="space-y-5">
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {cards.map(([label, value, Icon]) => (
              <Card key={label} className="p-5">
                <Icon size={19} className="text-clinical-blue" />
                <p className="mt-4 text-xs font-semibold uppercase text-slate-500">
                  {label}
                </p>
                <p className="mt-2 text-2xl font-bold text-clinical-ink">
                  {value}
                </p>
              </Card>
            ))}
          </section>
          <div className="grid gap-5 lg:grid-cols-2">
            <Card className="p-5">
              <h2 className="font-bold">Recent sessions</h2>
              {dashboard?.recent_sessions?.length ? (
                <ul className="mt-4 space-y-3">
                  {dashboard.recent_sessions.map((item) => (
                    <li
                      key={item.session_id}
                      className="rounded-xl bg-slate-50 p-3 text-sm"
                    >
                      <span className="font-semibold">
                        {item.exercise_display_name}
                      </span>{" "}
                      · {item.total_reps ?? "—"} reps · score{" "}
                      {item.movement_score ?? "—"}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-sm text-slate-500">
                  No saved sessions yet.
                </p>
              )}
            </Card>
            <Card className="p-5">
              <h2 className="font-bold">Common detected issues</h2>
              {dashboard?.common_detected_issues?.length ? (
                <ul className="mt-4 space-y-2">
                  {dashboard.common_detected_issues.map((item) => (
                    <li
                      key={item.issue_code}
                      className="flex justify-between text-sm"
                    >
                      <span>{pretty(item.issue_code)}</span>
                      <Badge tone="amber">{item.count}</Badge>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-sm text-slate-500">
                  No detected issue history.
                </p>
              )}
              <h3 className="mt-6 font-bold">Sessions by exercise</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {Object.entries(dashboard?.sessions_by_exercise || {}).map(
                  ([key, value]) => (
                    <li key={key}>
                      {exerciseName(key)}: {value}
                    </li>
                  ),
                )}
              </ul>
              <h3 className="mt-6 font-bold">Low-confidence sessions by exercise</h3>
              {Object.keys(dashboard?.low_confidence_sessions_by_exercise || {}).length ? <ul className="mt-3 space-y-2 text-sm">{Object.entries(dashboard.low_confidence_sessions_by_exercise).map(([key, value]) => <li key={key}>{exerciseName(key)}: {value}</li>)}</ul> : <p className="mt-3 text-sm text-slate-500">No low-confidence sessions.</p>}
            </Card>
          </div>
        </div>
      ) : view === "patients" ? (
        <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
          <Card className="p-5">
            <h2 className="font-bold">Create development profile</h2>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Use placeholders only. Do not enter names or identifying
              information.
            </p>
            <form className="mt-4 space-y-3" onSubmit={createProfile}>
              <input
                aria-label="Development profile display name"
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Example: Demo Profile A"
              />
              <Button type="submit" disabled={!name.trim()}>
                <Plus size={16} />
                Create profile
              </Button>
            </form>
          </Card>
          <div>
            {patients.length ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {patients.map((patient) => (
                  <Card key={patient.patient_id} className="p-5">
                    <h2 className="font-bold">{patient.display_name}</h2>
                    <p className="mt-2 text-xs text-slate-500">
                      {pretty(patient.age_group || "unknown")} ·{" "}
                      {pretty(patient.clinical_group || "unknown")}
                    </p>
                    <p className="mt-3 text-sm">
                      {patient.session_count} saved session
                      {patient.session_count === 1 ? "" : "s"}
                    </p>
                    <Button
                      className="mt-4"
                      variant="secondary"
                      onClick={() => openPatient(patient.patient_id)}
                    >
                      View profile
                    </Button>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No development patient profiles yet"
                description="Create a placeholder profile without using real patient-identifiable information."
                icon={Users}
              />
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          <Button variant="ghost" onClick={() => setView("patients")}>
            <ArrowLeft size={16} />
            Back to profiles
          </Button>
          <Card className="p-5">
            <Badge tone="blue">Development profile</Badge>
            <h2 className="mt-3 text-2xl font-bold">{detail?.display_name}</h2>
            <p className="mt-2 text-sm text-slate-500">
              {detail?.patient_id?.slice(0, 8)} ·{" "}
              {pretty(detail?.age_group || "unknown")} ·{" "}
              {pretty(detail?.clinical_group || "unknown")}
            </p>
          </Card>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-4">
              <p className="text-xs text-slate-500">Total sessions</p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.total_sessions || 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Average score</p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.average_movement_score ?? "—"}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Average confidence</p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.average_analysis_confidence == null
                  ? "—"
                  : `${Math.round(progress.average_analysis_confidence * 100)}%`}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Low-confidence sessions</p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.low_confidence_session_count || 0}
              </p>
            </Card>
          </section>
          <Card className="p-5">
            <h2 className="font-bold">Exercise session history</h2>
            {Object.keys(progress?.sessions_by_exercise || {}).length > 0 && <div className="mt-4 flex flex-wrap gap-2">{Object.entries(progress.sessions_by_exercise).map(([key, value]) => <Badge key={key} tone="blue">{exerciseName(key)}: {value}</Badge>)}</div>}
            {sessions.length ? (
              <ul className="mt-4 space-y-3">
                {sessions.map((item) => (
                  <li
                    key={item.session_id}
                    className="rounded-xl border border-slate-100 p-3 text-sm"
                  >
                    {item.exercise_display_name} · {item.total_reps ?? "—"} reps
                    · score {item.movement_score ?? "—"}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                No sessions assigned to this profile.
              </p>
            )}
            <h3 className="mt-6 font-bold">Detected issue counts</h3>
            <ul className="mt-3 space-y-2 text-sm">
              {progress?.detected_issue_counts?.map((item) => (
                <li key={item.issue_code}>
                  {pretty(item.issue_code)}: {item.count}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      )}
      <p className="mt-8 text-xs leading-5 text-slate-500">
        Production use requires authentication, roles and permissions, consent,
        secure storage, encryption, audit logs, and formal privacy review.
      </p>
    </main>
  );
}
