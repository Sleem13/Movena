import { useEffect, useState } from "react";
import { Activity, AlertTriangle, ArrowLeft, Plus, Stethoscope, Users } from "lucide-react";
import {
  createPatientProfile,
  getPatientProfile,
  getPatientProgress,
  getTherapistDashboard,
  listPatientExercisePlans,
  listPatientProfiles,
  listPatientSessions,
} from "../services/api.js";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../components/common/UI.jsx";
import { DistributionBars, SessionScoreChart, VisualizationHeading } from "../components/dashboard/TherapistVisualizations.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ExercisePlanManager from "../components/therapist/ExercisePlanManager.jsx";
import BaselineComparison from "../components/therapist/BaselineComparison.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function TherapistDashboard() {
  const { t, exerciseText, pretty } = useLocale();
  const [view, setView] = useState(window.location.pathname === "/therapist/patients" ? "patients" : "dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [patients, setPatients] = useState([]);
  const [detail, setDetail] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [progress, setProgress] = useState(null);
  const [plans, setPlans] = useState([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const sessionExerciseName = (item) => {
    const id = item.exercise_id || item.exercise;
    return id ? exerciseText(id).name : item.exercise_display_name;
  };
  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
    } catch {
      return "—";
    }
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
      const [profile, patientSessions, patientProgress, patientPlans] = await Promise.all([
        getPatientProfile(patientId),
        listPatientSessions(patientId),
        getPatientProgress(patientId),
        listPatientExercisePlans(patientId),
      ]);
      setDetail(profile);
      setSessions(patientSessions);
      setProgress(patientProgress);
      setPlans(patientPlans);
      setView("detail");
      const patientPath = `/therapist/patients/${patientId}`;
      if (window.location.pathname !== patientPath) window.history.pushState({}, "", patientPath);
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
  const issueCounts = Object.fromEntries((dashboard?.common_detected_issues || []).map((item) => [item.issue_code, item.count]));

  return (
    <main>
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
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,.75fr)]">
            <Card className="min-w-0 p-5 sm:p-6">
              <VisualizationHeading title={t("therapist.scoreTrend")} description={t("therapist.scoreTrendDescription")} />
              <SessionScoreChart sessions={dashboard?.recent_sessions || []} label={t("therapist.scoreTrend")} emptyLabel={t("therapist.noScoredSessions")} />
              {dashboard?.recent_sessions?.length ? <div className="mt-5 border-t border-slate-100 pt-4"><h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">{t("therapist.recentSessions")}</h3><ul className="mt-3 grid gap-2 sm:grid-cols-2">{dashboard.recent_sessions.slice(0, 4).map((item) => <li key={item.session_id} className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 px-3 py-2.5 text-xs"><span className="truncate font-semibold text-slate-700">{sessionExerciseName(item)}</span><span className="shrink-0 font-bold text-clinical-blue">{item.movement_score ?? "—"}</span></li>)}</ul></div> : null}
            </Card>
            <Card className="p-5 sm:p-6">
              <VisualizationHeading icon="bars" title={t("therapist.sessionsByExercise")} description={t("therapist.exerciseDistributionDescription")} />
              <DistributionBars entries={dashboard?.sessions_by_exercise} label={t("therapist.sessionsByExercise")} labelForKey={(key) => exerciseText(key).name} emptyLabel={t("therapist.noSavedSessions")} />
              <div className="mt-7 border-t border-slate-100 pt-5"><h3 className="mb-4 text-sm font-bold text-clinical-ink">{t("therapist.lowConfidenceByExercise")}</h3><DistributionBars entries={dashboard?.low_confidence_sessions_by_exercise} label={t("therapist.lowConfidenceByExercise")} labelForKey={(key) => exerciseText(key).name} emptyLabel={t("therapist.noLowConfidence")} tone="amber" /></div>
            </Card>
          </div>
          <Card className="p-5 sm:p-6">
            <VisualizationHeading icon="bars" title={t("therapist.commonIssues")} description={t("therapist.issueFrequencyDescription")} />
            <DistributionBars entries={issueCounts} label={t("therapist.commonIssues")} labelForKey={pretty} emptyLabel={t("therapist.noIssueHistory")} tone="amber" />
          </Card>
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
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.averageScore")}</p><p className="mt-2 text-2xl font-bold">{progress?.average_movement_score ?? "—"}</p><p className="mt-1 text-[11px] text-slate-500">{t("therapist.observationCount", { count: progress?.movement_score_observation_count || 0 })}</p></Card>
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.averageConfidence")}</p><p className="mt-2 text-2xl font-bold">{progress?.average_analysis_confidence == null ? "—" : `${Math.round(progress.average_analysis_confidence * 100)}%`}</p><p className="mt-1 text-[11px] text-slate-500">{t("therapist.observationCount", { count: progress?.analysis_confidence_observation_count || 0 })}</p></Card>
            <Card className="p-4"><p className="text-xs text-slate-500">{t("therapist.lowConfidenceSessions")}</p><p className="mt-2 text-2xl font-bold">{progress?.low_confidence_session_count || 0}</p></Card>
          </section>
          <ExercisePlanManager patientId={detail.patient_id} plans={plans} onPlansChange={setPlans} />
          <BaselineComparison comparisons={progress?.exercise_comparisons || []} />
          <Alert tone="info" title={t("therapist.provenanceTitle")}>
            <p>{t("therapist.provenanceSummary", { date: formatDate(progress?.latest_session_date) })}</p>
            {progress?.metric_provenance?.length ? (
              <ul className="mt-2 list-disc space-y-1 ps-5">
                {progress.metric_provenance.map((item) => <li key={item}>{item}</li>)}
              </ul>
            ) : (
              <p className="mt-2">{t("therapist.noProvenance")}</p>
            )}
          </Alert>
          <Card className="p-5">
            <h2 className="font-bold">{t("therapist.exerciseHistory")}</h2>
            {Object.keys(progress?.sessions_by_exercise || {}).length > 0 && <div className="mt-4 flex flex-wrap gap-2">{Object.entries(progress.sessions_by_exercise).map(([key, value]) => <Badge key={key} tone="blue">{exerciseText(key).name}: {value}</Badge>)}</div>}
            {sessions.length ? (
              <ul className="mt-4 space-y-3">
                {sessions.map((item) => <li key={item.session_id} className="rounded-xl border border-slate-100 p-3 text-sm">{sessionExerciseName(item)} · {t("therapist.rowReps", { value: item.total_reps ?? "—" })} · {t("therapist.rowScore", { value: item.movement_score ?? item.score ?? "—" })} · {t("therapist.rowConfidence", { value: item.analysis_confidence_level || "—" })} · {formatDate(item.created_at)}</li>)}
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
