import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  ChevronRight,
  ClipboardList,
  Plus,
  Search,
  Users,
} from "lucide-react";
import {
  acknowledgeExerciseResponse,
  createPatientProfile,
  getPatientProfile,
  getPatientProgress,
  getTherapistDashboard,
  listPatientExercisePlans,
  listPatientAdherence,
  listPatientProfiles,
  listPatientSessions,
  listTherapistAdherenceAlerts,
  listTherapistAppointments,
} from "../services/api.js";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import {
  DistributionBars,
  SessionScoreChart,
  VisualizationHeading,
} from "../components/dashboard/TherapistVisualizations.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import ExercisePlanManager from "../components/therapist/ExercisePlanManager.jsx";
import BaselineComparison from "../components/therapist/BaselineComparison.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";

function CareOperationsDashboard({
  dashboard,
  patients,
  careAlerts,
  appointments,
  onOpenPatient,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const todayKey = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Africa/Cairo",
  }).format(new Date());
  const todayAppointments = appointments.filter(
    (item) =>
      ["scheduled", "confirmed"].includes(item.status) &&
      new Intl.DateTimeFormat("en-CA", { timeZone: "Africa/Cairo" }).format(
        new Date(item.starts_at),
      ) === todayKey,
  );
  const upcomingAppointments = appointments
    .filter((item) => ["scheduled", "confirmed"].includes(item.status))
    .sort((a, b) => new Date(a.starts_at) - new Date(b.starts_at));
  const adherence = dashboard?.program_adherence_percent;
  const selectedPatient = patients[0];
  const normalizedQuery = searchQuery.trim().toLocaleLowerCase();
  const visiblePatients = normalizedQuery
    ? patients.filter((patient) =>
        [patient.display_name, patient.clinical_group].some((value) =>
          value?.toLocaleLowerCase().includes(normalizedQuery),
        ),
      )
    : patients;
  const patientName = (patientId) =>
    patients.find((patient) => patient.patient_id === patientId)
      ?.display_name || "Patient";
  const cairoTime = (value) =>
    new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Africa/Cairo",
    }).format(new Date(value));

  return (
    <div className="space-y-5">
      <section
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Care operations summary"
      >
        <Card className="p-5">
          <span className="sr-only">Total patients</span>
          <div className="flex items-start justify-between">
            <Users className="text-blue-700" size={21} />
            <span className="text-xs font-bold text-teal-700">Active</span>
          </div>
          <p className="mt-5 text-xs font-bold uppercase tracking-[.12em] text-slate-500">
            Assigned patients
          </p>
          <p className="mt-1 text-3xl font-extrabold text-[#071b4a]">
            {patients.length || dashboard?.total_patients || 0}
          </p>
        </Card>
        <Card className="p-5">
          <div className="flex items-start justify-between">
            <Activity className="text-teal-700" size={21} />
            <span className="text-xs font-bold text-slate-500">
              Last 7 days
            </span>
          </div>
          <p className="mt-5 text-xs font-bold uppercase tracking-[.12em] text-slate-500">
            Program adherence
          </p>
          <p className="mt-1 text-3xl font-extrabold text-[#071b4a]">
            {adherence == null ? "—" : `${Math.round(adherence)}%`}
          </p>
        </Card>
        <Card className="border-amber-200 p-5">
          <div className="flex items-start justify-between">
            <AlertTriangle className="text-amber-600" size={21} />
            <span className="text-xs font-bold text-amber-700">
              Review queue
            </span>
          </div>
          <p className="mt-5 text-xs font-bold uppercase tracking-[.12em] text-slate-500">
            Pain & adherence alerts
          </p>
          <p className="mt-1 text-3xl font-extrabold text-[#071b4a]">
            {careAlerts.length}
          </p>
        </Card>
        <Card className="p-5">
          <div className="flex items-start justify-between">
            <CalendarDays className="text-blue-700" size={21} />
            <span className="text-xs font-bold text-blue-700">Cairo time</span>
          </div>
          <p className="mt-5 text-xs font-bold uppercase tracking-[.12em] text-slate-500">
            Today&apos;s appointments
          </p>
          <p className="mt-1 text-3xl font-extrabold text-[#071b4a]">
            {todayAppointments.length}
          </p>
        </Card>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(330px,.75fr)]">
        <Card className="overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-extrabold text-[#071b4a]">
                Assigned patients
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Only patients explicitly assigned to your account are shown.
              </p>
            </div>
            <label className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                size={16}
              />
              <input
                aria-label="Search assigned patients"
                placeholder="Search patients…"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="w-full min-w-0 pl-9 text-sm sm:w-72"
              />
            </label>
          </div>
          <div className="max-w-full overflow-x-auto">
            <table className="w-full min-w-[660px] text-left text-sm">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-5 py-3">Patient</th>
                  <th className="px-4 py-3">Clinical group</th>
                  <th className="px-4 py-3">Sessions</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">
                    <span className="sr-only">Open</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {visiblePatients.length ? (
                  visiblePatients.slice(0, 8).map((patient) => (
                    <tr
                      key={patient.patient_id}
                      className="transition hover:bg-blue-50/50"
                    >
                      <td className="px-5 py-3.5">
                        <button
                          onClick={() => onOpenPatient(patient.patient_id)}
                          className="flex items-center gap-3 font-bold text-[#071b4a]"
                        >
                          <span className="grid h-9 w-9 place-items-center rounded-full bg-blue-50 text-xs text-blue-700">
                            {patient.display_name
                              .split(/\s+/)
                              .map((part) => part[0])
                              .join("")
                              .slice(0, 2)
                              .toUpperCase()}
                          </span>
                          {patient.display_name}
                        </button>
                      </td>
                      <td className="px-4 py-3.5 text-slate-600">
                        {patient.clinical_group || "Not specified"}
                      </td>
                      <td className="px-4 py-3.5 font-semibold">
                        {patient.session_count || 0}
                      </td>
                      <td className="px-4 py-3.5">
                        <Badge tone="teal">Active</Badge>
                      </td>
                      <td className="px-4 py-3.5">
                        <button
                          aria-label={`Open ${patient.display_name}`}
                          onClick={() => onOpenPatient(patient.patient_id)}
                          className="rounded-lg p-2 text-slate-400 hover:bg-white hover:text-blue-700"
                        >
                          <ChevronRight size={17} />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="5"
                      className="px-5 py-10 text-center text-sm text-slate-500"
                    >
                      {normalizedQuery
                        ? "No patients match your search."
                        : "No assigned patients yet."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <h2 className="flex items-center gap-2 font-extrabold text-[#071b4a]">
              <AlertTriangle size={18} className="text-amber-600" />
              Clinical alert queue
            </h2>
            <Badge tone={careAlerts.length ? "amber" : "teal"}>
              {careAlerts.length}
            </Badge>
          </div>
          <div className="divide-y divide-slate-100">
            {careAlerts.length ? (
              careAlerts.slice(0, 6).map((item) => (
                <div key={item.notification_id} className="px-5 py-4">
                  <p className="text-sm font-bold text-[#071b4a]">
                    {item.title}
                  </p>
                  <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-600">
                    {item.body}
                  </p>
                </div>
              ))
            ) : (
              <div className="p-5">
                <EmptyState
                  compact
                  title="No active pain or adherence alerts"
                />
              </div>
            )}
          </div>
        </Card>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <Card className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <h2 className="flex items-center gap-2 font-extrabold text-[#071b4a]">
              <CalendarDays size={18} className="text-blue-700" />
              Upcoming appointments
            </h2>
            <Badge tone="blue">{upcomingAppointments.length}</Badge>
          </div>
          <div className="divide-y divide-slate-100">
            {upcomingAppointments.length ? (
              upcomingAppointments.slice(0, 5).map((item) => (
                <div
                  key={item.appointment_id}
                  className="flex items-center justify-between gap-4 px-5 py-3.5"
                >
                  <div>
                    <p className="font-bold text-[#071b4a]">
                      {cairoTime(item.starts_at)} ·{" "}
                      {patientName(item.patient_id)}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {item.delivery_mode === "video"
                        ? "Private video session"
                        : "In-person session"}{" "}
                      · {item.status}
                    </p>
                  </div>
                  <Badge tone={item.can_join ? "teal" : "slate"}>
                    {item.can_join ? "Ready to join" : "Scheduled"}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="p-5">
                <EmptyState compact title="No upcoming appointments" />
              </div>
            )}
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-extrabold text-[#071b4a]">
              <ClipboardList size={18} className="text-teal-700" />
              Patient summary
            </h2>
            {selectedPatient ? (
              <Button
                variant="secondary"
                onClick={() => onOpenPatient(selectedPatient.patient_id)}
              >
                Open patient
              </Button>
            ) : null}
          </div>
          {selectedPatient ? (
            <div className="mt-5 flex items-center gap-4">
              <span className="grid h-14 w-14 place-items-center rounded-full bg-blue-50 font-extrabold text-blue-700">
                {selectedPatient.display_name
                  .split(/\s+/)
                  .map((part) => part[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase()}
              </span>
              <div>
                <p className="text-lg font-extrabold text-[#071b4a]">
                  {selectedPatient.display_name}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {selectedPatient.clinical_group ||
                    "Clinical group not specified"}{" "}
                  · {selectedPatient.session_count || 0} saved sessions
                </p>
              </div>
            </div>
          ) : (
            <div className="mt-4">
              <EmptyState
                compact
                title="Select a patient to review their plan and reports"
              />
            </div>
          )}
        </Card>
      </section>
    </div>
  );
}

export function ExerciseResponseReview({ patientId, entry, onReviewed }) {
  const [open, setOpen] = useState(false);
  const [disposition, setDisposition] = useState("contacted_patient");
  const [note, setNote] = useState("");
  const [attested, setAttested] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  if (entry.response_state !== "clinical_follow_up") {
    return <Badge tone="teal">Within reported tolerance</Badge>;
  }
  if (!entry.clinician_review_required || entry.reviewed_at) {
    return (
      <div>
        <Badge tone="teal">Reviewed</Badge>
        {entry.reviewed_by_name && <p className="mt-1 text-xs text-slate-500">{entry.reviewed_by_name}</p>}
        {entry.review_disposition ? (
          <p className="mt-1 text-[11px] text-slate-500">
            {entry.review_disposition.replaceAll("_", " ")}
          </p>
        ) : null}
      </div>
    );
  }

  async function submitReview(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const reviewed = await acknowledgeExerciseResponse(
        patientId,
        entry.adherence_id,
        { disposition, note: note.trim() || null, clinician_attestation: attested },
      );
      onReviewed(reviewed);
      setOpen(false);
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || "The review could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-w-56">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="amber">Review needed</Badge>
        <Button type="button" variant="ghost" className="min-h-8 px-2 text-xs" onClick={() => setOpen((value) => !value)}>
          {open ? "Close" : "Review"}
        </Button>
      </div>
      {open ? (
        <form className="mt-3 space-y-2 rounded-xl border border-amber-200 bg-amber-50 p-3" onSubmit={submitReview}>
          <label className="block text-xs font-semibold text-slate-700">
            Disposition
            <select className="mt-1 w-full rounded-lg border border-slate-200 bg-white p-2" value={disposition} onChange={(event) => setDisposition(event.target.value)}>
              <option value="contacted_patient">Contacted patient</option>
              <option value="plan_modified">Plan modified</option>
              <option value="appointment_scheduled">Appointment scheduled</option>
              <option value="referred_for_medical_review">Referred for medical review</option>
              <option value="reviewed_no_change">Reviewed—no change</option>
            </select>
          </label>
          <label className="block text-xs font-semibold text-slate-700">
            Clinical note
            <textarea className="mt-1 min-h-20 w-full rounded-lg border border-slate-200 bg-white p-2" value={note} onChange={(event) => setNote(event.target.value)} required={disposition === "reviewed_no_change"} maxLength={2000} />
          </label>
          <label className="flex items-start gap-2 text-xs font-semibold text-amber-950">
            <input className="mt-0.5" type="checkbox" checked={attested} onChange={(event) => setAttested(event.target.checked)} required />
            <span>I attest that I reviewed the patient-reported response and used clinical judgment.</span>
          </label>
          {error ? <Alert>{error}</Alert> : null}
          <Button type="submit" className="w-full" disabled={saving || !attested}>
            {saving ? "Saving…" : "Acknowledge review"}
          </Button>
        </form>
      ) : null}
    </div>
  );
}

export default function TherapistDashboard({ onNavigate }) {
  const { t, exerciseText, pretty } = useLocale();
  const { user } = useAuth();
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
  const [plans, setPlans] = useState([]);
  const [adherence, setAdherence] = useState([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [careAlerts, setCareAlerts] = useState([]);
  const [appointments, setAppointments] = useState([]);

  const sessionExerciseName = (item) => {
    const id = item.exercise_id || item.exercise;
    return id ? exerciseText(id).name : item.exercise_display_name;
  };
  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
        new Date(value),
      );
    } catch {
      return "—";
    }
  };

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [summary, profiles, alerts, appointmentRows] = await Promise.all([
        getTherapistDashboard(),
        listPatientProfiles(),
        Promise.resolve(
          typeof listTherapistAdherenceAlerts === "function"
            ? listTherapistAdherenceAlerts()
            : [],
        )
          .then((rows) => rows || [])
          .catch(() => []),
        Promise.resolve(
          typeof listTherapistAppointments === "function"
            ? listTherapistAppointments()
            : [],
        )
          .then((rows) => rows || [])
          .catch(() => []),
      ]);
      setDashboard(summary);
      setPatients(profiles);
      setCareAlerts(alerts);
      setAppointments(appointmentRows);
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
    const match = window.location.pathname.match(
      /^\/therapist\/patients\/([^/]+)$/,
    );
    if (match) openPatient(match[1]);
  }, []);

  function changePrimaryView(nextView) {
    setView(nextView);
    if (onNavigate) {
      onNavigate(nextView === "patients" ? "therapistPatients" : "therapist");
    }
  }

  async function createProfile(event) {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      await createPatientProfile({ display_name: name.trim() });
      setName("");
      await load();
      changePrimaryView("patients");
    } catch {
      setError(t("therapist.profileCreateError"));
    }
  }

  async function openPatient(patientId) {
    setLoading(true);
    try {
      const [
        profile,
        patientSessions,
        patientProgress,
        patientPlans,
        patientAdherence,
      ] = await Promise.all([
        getPatientProfile(patientId),
        listPatientSessions(patientId),
        getPatientProgress(patientId),
        listPatientExercisePlans(patientId),
        listPatientAdherence(patientId),
      ]);
      setDetail(profile);
      setSessions(patientSessions);
      setProgress(patientProgress);
      setPlans(patientPlans);
      setAdherence(patientAdherence);
      setView("detail");
      const patientPath = `/therapist/patients/${patientId}`;
      if (window.location.pathname !== patientPath)
        window.history.pushState({}, "", patientPath);
    } catch {
      setError(t("therapist.detailError"));
    } finally {
      setLoading(false);
    }
  }

  const issueCounts = Object.fromEntries(
    (dashboard?.common_detected_issues || []).map((item) => [
      item.issue_code,
      item.count,
    ]),
  );
  const therapistName = (
    user?.full_name ||
    user?.email?.split("@")[0] ||
    t("profile.developmentUser")
  ).split(/\s+/)[0];

  return (
    <main>
      <PageHeader
        eyebrow={t("therapist.eyebrow")}
        title={
          view === "dashboard"
            ? t("therapist.welcome", { name: therapistName })
            : t("therapist.title")
        }
        description={t("therapist.description")}
        actions={
          view === "dashboard" ? (
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => changePrimaryView("patients")}>
                <Users size={16} />
                {t("therapist.reviewPatients")}
              </Button>
              <Button
                variant="secondary"
                onClick={() => onNavigate?.("analyze")}
              >
                <Activity size={16} />
                {t("therapist.analyzeMovement")}
              </Button>
              <Button variant="ghost" onClick={() => onNavigate?.("history")}>
                <ClipboardList size={16} />
                {t("therapist.viewSessions")}
              </Button>
            </div>
          ) : null
        }
      />
      <Alert tone="warning" title={t("therapist.warningTitle")}>
        {t("therapist.warning")}
      </Alert>
      <div className="my-5 flex flex-wrap gap-2">
        <Button
          variant={view === "dashboard" ? "primary" : "secondary"}
          onClick={() => changePrimaryView("dashboard")}
        >
          {t("therapist.dashboard")}
        </Button>
        <Button
          variant={view === "patients" ? "primary" : "secondary"}
          onClick={() => changePrimaryView("patients")}
        >
          {t("therapist.patients")}
        </Button>
      </div>
      {error && <Alert title={t("therapist.errorTitle")}>{error}</Alert>}
      {loading ? (
        <Card className="grid min-h-52 place-items-center">
          <LoadingSpinner label={t("therapist.loading")} />
        </Card>
      ) : view === "dashboard" ? (
        <div className="space-y-5">
          <CareOperationsDashboard
            dashboard={dashboard}
            patients={patients}
            careAlerts={careAlerts}
            appointments={appointments}
            onOpenPatient={openPatient}
          />
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,.75fr)]">
            <Card className="min-w-0 p-5 sm:p-6">
              <VisualizationHeading
                title={t("therapist.scoreTrend")}
                description={t("therapist.scoreTrendDescription")}
              />
              <SessionScoreChart
                sessions={dashboard?.recent_sessions || []}
                label={t("therapist.scoreTrend")}
                emptyLabel={t("therapist.noScoredSessions")}
              />
              {dashboard?.recent_sessions?.length ? (
                <div className="mt-5 border-t border-slate-100 pt-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    {t("therapist.recentSessions")}
                  </h3>
                  <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                    {dashboard.recent_sessions.slice(0, 4).map((item) => (
                      <li
                        key={item.session_id}
                        className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 px-3 py-2.5 text-xs"
                      >
                        <span className="truncate font-semibold text-slate-700">
                          {sessionExerciseName(item)}
                        </span>
                        <span className="shrink-0 font-bold text-clinical-blue">
                          {item.movement_score ?? "—"}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </Card>
            <Card className="p-5 sm:p-6">
              <VisualizationHeading
                icon="bars"
                title={t("therapist.sessionsByExercise")}
                description={t("therapist.exerciseDistributionDescription")}
              />
              <DistributionBars
                entries={dashboard?.sessions_by_exercise}
                label={t("therapist.sessionsByExercise")}
                labelForKey={(key) => exerciseText(key).name}
                emptyLabel={t("therapist.noSavedSessions")}
              />
              <div className="mt-7 border-t border-slate-100 pt-5">
                <h3 className="mb-4 text-sm font-bold text-clinical-ink">
                  {t("therapist.lowConfidenceByExercise")}
                </h3>
                <DistributionBars
                  entries={dashboard?.low_confidence_sessions_by_exercise}
                  label={t("therapist.lowConfidenceByExercise")}
                  labelForKey={(key) => exerciseText(key).name}
                  emptyLabel={t("therapist.noLowConfidence")}
                  tone="amber"
                />
              </div>
            </Card>
          </div>
          <Card className="p-5 sm:p-6">
            <VisualizationHeading
              icon="bars"
              title={t("therapist.commonIssues")}
              description={t("therapist.issueFrequencyDescription")}
            />
            <DistributionBars
              entries={issueCounts}
              label={t("therapist.commonIssues")}
              labelForKey={pretty}
              emptyLabel={t("therapist.noIssueHistory")}
              tone="amber"
            />
          </Card>
        </div>
      ) : view === "patients" ? (
        <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
          <div className="flex flex-wrap gap-3 lg:col-span-2"><Button onClick={() => onNavigate("careTeam")}><Users size={18} />{t("nav.connections")}</Button></div>
          <Card className="p-5">
            <h2 className="font-bold">{t("therapist.createProfile")}</h2>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              {t("therapist.profileHelp")}
            </p>
            <form className="mt-4 space-y-3" onSubmit={createProfile}>
              <input
                aria-label={t("therapist.profileName")}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder={t("therapist.profilePlaceholder")}
              />
              <Button type="submit" disabled={!name.trim()}>
                <Plus size={16} />
                {t("therapist.createProfileButton")}
              </Button>
            </form>
          </Card>
          <div>
            {patients.length ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {patients.map((patient) => {
                  const sessionLabel =
                    patient.session_count === 1
                      ? t("therapist.sessionSingular")
                      : t("therapist.sessionPlural");
                  return (
                    <Card key={patient.patient_id} className="p-5">
                      <h2 className="font-bold">{patient.display_name}</h2>
                      <p className="mt-2 text-xs text-slate-500">
                        {pretty(patient.age_group || "unknown")} ·{" "}
                        {pretty(patient.clinical_group || "unknown")}
                      </p>
                      <p className="mt-3 text-sm">
                        {t("therapist.savedSessionCount", {
                          count: patient.session_count,
                          label: sessionLabel,
                        })}
                      </p>
                      <Button
                        className="mt-4"
                        variant="secondary"
                        onClick={() => openPatient(patient.patient_id)}
                      >
                        {t("therapist.viewProfile")}
                      </Button>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <EmptyState
                title={t("therapist.emptyProfiles")}
                description={t("therapist.emptyProfilesDescription")}
                icon={Users}
              />
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          <Button variant="ghost" onClick={() => changePrimaryView("patients")}>
            <ArrowLeft size={16} />
            {t("therapist.backToProfiles")}
          </Button>
          <Card className="p-5">
            <Badge tone="blue">{t("therapist.developmentProfile")}</Badge>
            <h2 className="mt-3 text-2xl font-bold">{detail?.display_name}</h2>
            <p className="mt-2 text-sm text-slate-500">
              {detail?.patient_id?.slice(0, 8)} ·{" "}
              {pretty(detail?.age_group || "unknown")} ·{" "}
              {pretty(detail?.clinical_group || "unknown")}
            </p>
          </Card>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-4">
              <p className="text-xs text-slate-500">
                {t("therapist.totalSessions")}
              </p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.total_sessions || 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">
                {t("therapist.averageScore")}
              </p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.average_movement_score ?? "—"}
              </p>
              <p className="mt-1 text-[11px] text-slate-500">
                {t("therapist.observationCount", {
                  count: progress?.movement_score_observation_count || 0,
                })}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">
                {t("therapist.averageConfidence")}
              </p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.average_analysis_confidence == null
                  ? "—"
                  : `${Math.round(progress.average_analysis_confidence * 100)}%`}
              </p>
              <p className="mt-1 text-[11px] text-slate-500">
                {t("therapist.observationCount", {
                  count: progress?.analysis_confidence_observation_count || 0,
                })}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">
                {t("therapist.lowConfidenceSessions")}
              </p>
              <p className="mt-2 text-2xl font-bold">
                {progress?.low_confidence_session_count || 0}
              </p>
            </Card>
          </section>
          <div className="grid gap-5 lg:grid-cols-2">
            <Card className="p-5 sm:p-6">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-bold">
                  <AlertTriangle size={19} className="text-amber-600" />
                  Care alerts
                </h2>
                <Badge tone={careAlerts.length ? "amber" : "teal"}>
                  {careAlerts.length}
                </Badge>
              </div>
              <div className="mt-4 space-y-2">
                {careAlerts.length ? (
                  careAlerts.slice(0, 5).map((item) => (
                    <div
                      key={item.notification_id}
                      className="rounded-xl border border-amber-100 bg-amber-50 p-3"
                    >
                      <p className="text-sm font-bold text-amber-950">
                        {item.title}
                      </p>
                      <p className="mt-1 text-xs leading-5 text-amber-900">
                        {item.body}
                      </p>
                    </div>
                  ))
                ) : (
                  <EmptyState
                    compact
                    title="No active pain or adherence alerts"
                  />
                )}
              </div>
            </Card>
            <Card className="p-5 sm:p-6">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-bold">
                  <CalendarDays size={19} className="text-blue-600" />
                  Upcoming appointments
                </h2>
                <Badge tone="blue">
                  {
                    appointments.filter((item) =>
                      ["scheduled", "confirmed"].includes(item.status),
                    ).length
                  }
                </Badge>
              </div>
              <div className="mt-4 space-y-2">
                {appointments
                  .filter((item) =>
                    ["scheduled", "confirmed"].includes(item.status),
                  )
                  .slice(0, 5)
                  .map((item) => (
                    <div
                      key={item.appointment_id}
                      className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 p-3"
                    >
                      <div>
                        <p className="text-sm font-bold">
                          {new Intl.DateTimeFormat(undefined, {
                            dateStyle: "medium",
                            timeStyle: "short",
                            timeZone: "Africa/Cairo",
                          }).format(new Date(item.starts_at))}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {item.delivery_mode} · {item.status}
                        </p>
                      </div>
                      <Badge tone={item.can_join ? "teal" : "slate"}>
                        {item.can_join ? "Join" : "Scheduled"}
                      </Badge>
                    </div>
                  ))}
              </div>
            </Card>
          </div>
          <ExercisePlanManager
            currentUser={user}
            patientId={detail.patient_id}
            plans={plans}
            onPlansChange={setPlans}
          />
          <Card className="overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div>
                <h2 className="font-bold text-[#071b4a]">
                  Exercise adherence & reported outcomes
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Patient-reported values remain separate from AI movement
                  metrics.
                </p>
              </div>
              <Badge tone="blue">{adherence.length}</Badge>
            </div>
            {adherence.length ? (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[820px] text-left text-sm">
                  <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-5 py-3">Date</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Pain before</th>
                      <th className="px-4 py-3">Pain after</th>
                      <th className="px-4 py-3">Difficulty</th>
                      <th className="px-4 py-3">Fatigue</th>
                      <th className="px-4 py-3">Effort</th>
                      <th className="px-4 py-3">Response & review</th>
                      <th className="px-4 py-3">AI analysis</th>
                      <th className="px-5 py-3">Patient comment</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {adherence.slice(0, 30).map((entry) => (
                      <tr key={entry.adherence_id}>
                        <td className="px-5 py-3.5 font-semibold">
                          {formatDate(entry.scheduled_date)}
                        </td>
                        <td className="px-4 py-3.5">
                          <Badge
                            tone={
                              entry.completion_status === "completed"
                                ? "teal"
                                : entry.completion_status === "partial"
                                  ? "amber"
                                  : "slate"
                            }
                          >
                            {pretty(entry.completion_status)}
                          </Badge>
                        </td>
                        <td className="px-4 py-3.5">
                          {entry.pain_before ?? "—"}
                        </td>
                        <td className="px-4 py-3.5">
                          {entry.pain_after ?? "—"}
                        </td>
                        <td className="px-4 py-3.5">
                          {entry.difficulty ?? "—"}
                        </td>
                        <td className="px-4 py-3.5">{entry.fatigue ?? "—"}</td>
                        <td className="px-4 py-3.5">
                          {entry.perceived_exertion ?? "—"}
                          {entry.perceived_exertion != null ? "/10" : ""}
                        </td>
                        <td className="px-4 py-3.5 align-top">
                          <ExerciseResponseReview
                            patientId={detail.patient_id}
                            entry={entry}
                            onReviewed={(reviewed) =>
                              setAdherence((rows) =>
                                rows.map((row) =>
                                  row.adherence_id === reviewed.adherence_id
                                    ? { ...row, ...reviewed }
                                    : row,
                                ),
                              )
                            }
                          />
                          {entry.symptom_flags?.length ? (
                            <p className="mt-2 max-w-56 text-[11px] leading-4 text-amber-800">
                              {entry.symptom_flags.map(pretty).join(", ")}
                            </p>
                          ) : null}
                        </td>
                        <td className="px-4 py-3.5">
                          {entry.analysis_session_id ? (
                            <Badge tone="blue">Linked</Badge>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td className="max-w-xs px-5 py-3.5 text-slate-600">
                          {entry.note || "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-5">
                <EmptyState compact title="No exercise check-ins yet" />
              </div>
            )}
          </Card>
          <BaselineComparison
            comparisons={progress?.exercise_comparisons || []}
          />
          <Alert tone="info" title={t("therapist.provenanceTitle")}>
            <p>
              {t("therapist.provenanceSummary", {
                date: formatDate(progress?.latest_session_date),
              })}
            </p>
            {progress?.metric_provenance?.length ? (
              <ul className="mt-2 list-disc space-y-1 ps-5">
                {progress.metric_provenance.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2">{t("therapist.noProvenance")}</p>
            )}
          </Alert>
          <Card className="p-5">
            <h2 className="font-bold">{t("therapist.exerciseHistory")}</h2>
            {Object.keys(progress?.sessions_by_exercise || {}).length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {Object.entries(progress.sessions_by_exercise).map(
                  ([key, value]) => (
                    <Badge key={key} tone="blue">
                      {exerciseText(key).name}: {value}
                    </Badge>
                  ),
                )}
              </div>
            )}
            {sessions.length ? (
              <ul className="mt-4 space-y-3">
                {sessions.map((item) => (
                  <li
                    key={item.session_id}
                    className="rounded-xl border border-slate-100 p-3 text-sm"
                  >
                    {sessionExerciseName(item)} ·{" "}
                    {t("therapist.rowReps", { value: item.total_reps ?? "—" })}{" "}
                    ·{" "}
                    {t("therapist.rowScore", {
                      value: item.movement_score ?? item.score ?? "—",
                    })}{" "}
                    ·{" "}
                    {t("therapist.rowConfidence", {
                      value: item.analysis_confidence_level || "—",
                    })}{" "}
                    · {formatDate(item.created_at)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                {t("therapist.noAssignedSessions")}
              </p>
            )}
            <h3 className="mt-6 font-bold">
              {t("therapist.detectedIssueCounts")}
            </h3>
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
        {t("therapist.productionNotice")}
      </p>
    </main>
  );
}
