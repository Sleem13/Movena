import { useEffect, useState } from "react";
import { Activity, AlertTriangle, ArrowLeft, Plus, Stethoscope, Users } from "lucide-react";
import {
  createPatientProfile,
  getPatientProfile,
  getPatientProgress,
  getTherapistDashboard,
  listPatientProfiles,
  listPatientSessions,
} from "../services/api.js";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function TherapistDashboard() {
  const { t, exerciseText, pretty } = useLocale();
  const [view, setView] = useState(window.location.pathname === "/therapist/patients" ? "patients" : "dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [patients, setPatients] = useState([]);
  const [detail, setDetail] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [progress, setProgress] = useState(null);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const sessionExerciseName = (item) => {
    const id = item.exercise_id || item.exercise;
    return id ? exerciseText(id).name : item.exercise_display_name;
  };

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [summary, profiles] = await Promise.all([getTherapistDashboard(), listPatientProfiles()]);
      setDashboard(summary);
      setPatients(profiles);
    } catch (requestError) {
      setError(
        requestError.response?.status === 403
          ? t("therapist.noPermission")
          : requestError.response?.status === 401
            ? t("therapist.login")
            : t("therapist.loadError"),
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const match = window.location.pathname.match(/^\/therapist\/patients\/([^/]+)$/);
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
      setError(t("therapist.profileCreateError"));
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
      setError(t("therapist.detailError"));
    } finally {
      setLoading(false);
    }
  }

  const cards = dashboard
    ? [
        [t("therapist.totalPatients"), dashboard.total_patients, Users],
        [t("therapist.totalSessions"), dashboard.total_sessions, Activity],
        [t("therapist.lowConfidenceSessions"), dashboard.low_confidence_sessions, AlertTriangle],
        [t("therapist.commonIssue"), dashboard.common_detected_issues?.[0] ? pretty(dashboard.common_detected_issues[0].issue_code) : t("common.none"), Stethoscope],
      ]
    : [];

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader eyebrow={t("therapist.eyebrow")} title={t("therapist.title")} description={t("therapist.description")} />
      <Alert tone="warning" title={t("therapist.warningTitle")}>{t("therapist.warning")}</Alert>
      <div className="my-5 flex flex-wrap gap-2">
        <Button variant={view === "dashboard" ? "primary" : "secondary"} onClick={() => setView("dashboard")}>{t("therapist.dashboard")}</Button>
        <Button variant={view === "patients" ? "primary" : "secondary"} onClick={() => setView("patients")}>{t("therapist.patients")}</Button>
      </div>
      {error && <Alert title={t("therapist.errorTitle")}>{error}</Alert>}
      {loading ? (
        <Card className="grid min-h-52 place-items-center"><LoadingSpinner label={t("therapist.loading")} /></Card>
      ) : view === "dashboard" ? (
        <div className="space-y-5">
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {cards.map(([label, value, Icon]) => (
              <Card key={label} className="p-5">
                <Icon size={19} className="text-clinical-blue" />
                <p className="mt-4 text-xs font-semibold uppercase text-slate-500">{label}</p>
                <p className="mt-2 text-2xl font-bold text-clinical-ink">{value}</p>
              </Card>
            ))}
          </section>
          <div className="grid gap-5 lg:grid-cols-2">
            <Card className="p-5">
              <h2 className="font-bold">{t("therapist.recentSessions")}</h2>
              {dashboard?.recent_sessions?.length ? (
                <ul className="mt-4 space-y-3">
                  {dashboard.recent_sessions.map((item) => (
                    <li key={item.session_id} className="rounded-xl bg-slate-50 p-3 text-sm">
                      <span className="font-semibold">{sessionExerciseName(item)}</span>{" "}
                      · {item.total_reps ?? "—"} reps · score {item.movement_score ?? "—"}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-sm text-slate-500">{t("therapist.noSavedSessions")}</p>
              )}
            </Card>
            <Card className="p-5">
              <h2 className="font-bold">{t("therapist.commonIssues")}</h2>
              {dashboard?.common_detected_issues?.length ? (
                <ul className="mt-4 space-y-2">
                  {dashboard.common_detected_issues.map((item) => (
                    <li key={item.issue_code} className="flex justify-between text-sm"><span>{pretty(item.issue_code)}</span><Badge tone="amber">{item.count}</Badge></li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-sm text-slate-500">{t("therapist.noIssueHistory")}</p>
              )}
              <h3 className="mt-6 font-bold">{t("therapist.sessionsByExercise")}</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {Object.entries(dashboard?.sessions_by_exercise || {}).map(([key, value]) => <li key={key}>{exerciseText(key).name}: {value}</li>)}
              </ul>
              <h3 className="mt-6 font-bold">{t("therapist.lowConfidenceByExercise")}</h3>
              {Object.keys(dashboard?.low_confidence_sessions_by_exercise || {}).length ? <ul className="mt-3 space-y-2 text-sm">{Object.entries(dashboard.low_confidence_sessions_by_exercise).map(([key, value]) => <li key={key}>{exerciseText(key).name}: {value}</li>)}</ul> : <p className="mt-3 text-sm text-slate-500">{t("therapist.noLowConfidence")}</p>}
            </Card>
          </div>
        </div>
      ) : view === "patients" ? (
        <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
          <Card className="p-5">
            <h2 className="font-bold">{t("therapist.createProfile")}</h2>
            <p className="mt-2 text-xs leading-5 text-slate-500">{t("therapist.profileHelp")}</p>
            <form className="mt-4 space-y-3" onSubmit={createProfile}>
              <input aria-label={t("therapist.profileName")} className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm" value={name} onChange={(event) => setName(event.target.value)} placeholder={t("therapist.profilePlaceholder")} />
              <Button type="submit" disabled={!name.trim()}><Plus size={16} />{t("therapist.createProfileButton")}</Button>
            </form>
          </Card>
          <div>
            {patients.length ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {patients.map((patient) => {
                  const sessionLabel = patient.session_count === 1 ? t("therapist.sessionSingular") : t("therapist.sessionPlural");
                  return (
                    <Card key={patient.patient_id} className="p-5">
                      <h2 className="font-bold">{patient.display_name}</h2>
                      <p className="mt-2 text-xs text-slate-500">{pretty(patient.age_group || "unknown")} · {pretty(patient.clinical_group || "unknown")}</p>
                      <p className="mt-3 text-sm">{t("therapist.savedSessionCount", { count: patient.session_count, label: sessionLabel })}</p>
                      <Button className="mt-4" variant="secondary" onClick={() => openPatient(patient.patient_id)}>{t("therapist.viewProfile")}</Button>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <EmptyState title={t("therapist.emptyProfiles")} description={t("therapist.emptyProfilesDescription")} icon={Users} />
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          <Button variant="ghost" onClick={() => setView("patients")}><ArrowLeft size={16} />{t("therapist.backToProfiles")}</Button>
          <Card className="p-5">
            <Badge tone="blue">{t("therapist.developmentProfile")}</Badge>
            <h2 className="mt-3 text-2xl font-bold">{detail?.display_name}</h2>
            <p className="mt-2 text-sm text-slate-500">{detail?.patient_id?.slice(0, 8)} · {pretty(detail?.age_group || "unknown")} · {pretty(detail?.clinical_group || "unknown")}</p>
          </Card>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.totalSessions")}</p><p className="mt-2 text-2xl font-bold">{progress?.total_sessions || 0}</p></Card>
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.averageScore")}</p><p className="mt-2 text-2xl font-bold">{progress?.average_movement_score ?? "—"}</p></Card>
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.averageConfidence")}</p><p className="mt-2 text-2xl font-bold">{progress?.average_analysis_confidence == null ? "—" : `${Math.round(progress.average_analysis_confidence * 100)}%`}</p></Card>
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.lowConfidenceSessions")}</p><p className="mt-2 text-2xl font-bold">{progress?.low_confidence_session_count || 0}</p></Card>
          </section>
          <Card className="p-5">
            <h2 className="font-bold">{t("therapist.exerciseHistory")}</h2>
            {Object.keys(progress?.sessions_by_exercise || {}).length > 0 && <div className="mt-4 flex flex-wrap gap-2">{Object.entries(progress.sessions_by_exercise).map(([key, value]) => <Badge key={key} tone="blue">{exerciseText(key).name}: {value}</Badge>)}</div>}
            {sessions.length ? (
              <ul className="mt-4 space-y-3">
                {sessions.map((item) => <li key={item.session_id} className="rounded-xl border border-slate-100 p-3 text-sm">{sessionExerciseName(item)} · {item.total_reps ?? "—"} reps · score {item.movement_score ?? item.score ?? "—"}</li>)}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-slate-500">{t("therapist.noAssignedSessions")}</p>
            )}
            <h3 className="mt-6 font-bold">{t("therapist.detectedIssueCounts")}</h3>
            <ul className="mt-3 space-y-2 text-sm">{progress?.detected_issue_counts?.map((item) => <li key={item.issue_code}>{pretty(item.issue_code)}: {item.count}</li>)}</ul>
          </Card>
        </div>
      )}
      <p className="mt-8 text-xs leading-5 text-slate-500">{t("therapist.productionNotice")}</p>
    </main>
  );
}
