"use client";
import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CalendarDays,
  Check,
  ChevronRight,
  Plus,
  Users,
} from "lucide-react";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { api } from "../../lib/api";
import {
  createReportPath,
  localCalendarDay,
  reportHref,
  validReportPeriod,
} from "../../lib/reports.mjs";
import type { ProgressReportCreateResponse } from "../../../../../packages/contracts/generated";
import type {
  Connection,
  Invitation,
  Patient,
  ResponseRecord,
  Today,
  User,
} from "../../lib/types";

export function ResourceState({
  loading,
  error,
  retry,
}: {
  loading: boolean;
  error: string;
  retry: () => void;
}) {
  const { t } = usePreferences();
  return loading ? (
    <div className="panel loading" role="status">
      {t("loading")}
    </div>
  ) : error ? (
    <div className="panel error" role="alert">
      <p>{error}</p>
      <button className="secondary" onClick={retry}>
        {t("retry")}
      </button>
    </div>
  ) : null;
}
const reviewDispositions = [
  "reviewed_no_change",
  "contacted_patient",
  "plan_modified",
  "appointment_scheduled",
  "referred_for_medical_review",
] as const;
export function TodayView() {
  const resource = useResource<Today>("patient/today");
  const { data } = resource;
  const { t, locale, exerciseName } = usePreferences();
  if (!data) return <ResourceState {...resource} retry={resource.refresh} />;
  const items = data.plan_items ?? [];
  const completed = items.filter(
    (i) => i.completion_status === "completed",
  ).length;
  const next = items.find((i) => i.completion_status !== "completed");
  return (
    <div className="today-grid">
      <div>
        <Link className="secondary" href="/workspace/notifications">
          {t("notifications")} ·{" "}
          {new Intl.NumberFormat(locale).format(data.unread_notifications ?? 0)}
        </Link>
        <section className="plan-hero">
          <div className="hero-icon">
            <CalendarDays size={28} />
          </div>
          <p className="muted">
            {new Intl.DateTimeFormat(locale, {
              weekday: "long",
              month: "long",
              day: "numeric",
              timeZone: "UTC",
            }).format(new Date(data.date + "T12:00:00Z"))}
          </p>
          <h2>{data.plan_title || t("emptyPlan")}</h2>
          <p>
            {items.length
              ? `${new Intl.NumberFormat(locale).format(completed)} / ${new Intl.NumberFormat(locale).format(items.length)} ${t("complete")}`
              : t("emptyPlanBody")}
          </p>
          {next && (
            <Link
              className="primary"
              href={`/workspace/check-in/${encodeURIComponent(next.item_id)}`}
            >
              {t("start")}
              <ArrowRight size={20} />
            </Link>
          )}
        </section>
        <div className="section-heading">
          <h2>{t("assigned")}</h2>
          <span className="muted">
            {new Intl.NumberFormat(locale).format(items.length)}
          </span>
        </div>
        <div className="exercise-list">
          {items.map((item, index) => (
            <Link
              className="exercise-row"
              key={item.item_id}
              href={`/workspace/check-in/${encodeURIComponent(item.item_id)}`}
            >
              <span
                className={`exercise-number ${item.completion_status === "completed" ? "finished" : ""}`}
              >
                {item.completion_status === "completed" ? (
                  <Check size={22} />
                ) : (
                  new Intl.NumberFormat(locale).format(index + 1)
                )}
              </span>
              <span>
                <strong>{exerciseName(item.exercise_id)}</strong>
                <small>
                  {item.sets} {t("sets")} · {item.reps} {t("reps")}
                </small>
              </span>
              <ChevronRight size={20} />
            </Link>
          ))}
        </div>
      </div>
      <aside className="today-aside">
        <section className="panel">
          <div className="hero-icon">
            <Users size={24} />
          </div>
          <h2>{t("careTeam")}</h2>
          <p className="muted">{t("todayIntro")}</p>
          <Link href="/workspace/care" className="text-link">
            {t("care")}
            <ArrowRight size={18} />
          </Link>
        </section>
        <section className="quiet-panel">
          <h3>{t("analyze")}</h3>
          <p>{t("analyzeHint")}</p>
          <Link href="/workspace/analyze" className="secondary">
            {t("next")}
            <ArrowRight size={18} />
          </Link>
        </section>
        <p className="fine-print">{t("analysisDisclaimer")}</p>
      </aside>
    </div>
  );
}
export function CareView({ user }: { user: User }) {
  const connections = useResource<Connection[]>("connections");
  const invitations = useResource<Invitation[]>("care-invitations");
  const { t } = usePreferences();
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  async function respond(id: string, action: string) {
    setBusy(id);
    setError("");
    try {
      await api(`care-invitations/${encodeURIComponent(id)}/respond`, {
        method: "POST",
        body: JSON.stringify({ action }),
      });
      connections.refresh();
      invitations.refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <div className="two-columns">
      <section className="panel">
        <h2>{t("careTeam")}</h2>
        <Link className="secondary" href="/workspace/schedule">
          <CalendarDays size={18} />
          {t("appointments")}
        </Link>
        <ResourceState {...connections} retry={connections.refresh} />
        {connections.data?.length === 0 && (
          <p className="empty">{t("noConnections")}</p>
        )}
        {connections.data?.map((c) => (
          <div key={c.assignment_id} className="data-row">
            <span className="avatar">
              <Users size={22} />
            </span>
            <div>
              <strong>
                {user.role === "patient" ? c.therapist_name : c.patient_name}
              </strong>
              <small>{c.status}</small>
            </div>
          </div>
        ))}
      </section>
      <section className="panel">
        <h2>{t("invitations")}</h2>
        <ResourceState {...invitations} retry={invitations.refresh} />
        {invitations.data?.filter((i) => i.status === "pending").length ===
          0 && <p className="empty">{t("noInvitations")}</p>}
        {invitations.data
          ?.filter((i) => i.status === "pending")
          .map((i) => (
            <div className="invitation" key={i.invitation_id}>
              <strong>{i.therapist_name}</strong>
              <div className="button-row">
                <button
                  disabled={!!busy}
                  className="primary"
                  onClick={() => respond(i.invitation_id, "accept")}
                >
                  {t("accept")}
                </button>
                <button
                  disabled={!!busy}
                  className="secondary"
                  onClick={() => respond(i.invitation_id, "decline")}
                >
                  {t("decline")}
                </button>
              </div>
            </div>
          ))}
        {error && <p role="alert">{error}</p>}
      </section>
    </div>
  );
}
export function PatientsView() {
  const resource = useResource<Patient[]>("therapist/patients");
  const { t } = usePreferences();
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  async function invite(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const email = new FormData(e.currentTarget).get("email");
    try {
      await api("care-invitations", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setSent(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="two-columns">
      <section className="panel">
        <h2>{t("patients")}</h2>
        <input
          type="search"
          aria-label={t("patients")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <ResourceState {...resource} retry={resource.refresh} />
        {resource.data?.length === 0 && (
          <p className="empty">{t("noPatients")}</p>
        )}
        {resource.data
          ?.filter((p) =>
            p.display_name.toLowerCase().includes(search.toLowerCase()),
          )
          .map((p) => (
            <Link
              href={`/workspace/review?patient=${encodeURIComponent(p.patient_id)}`}
              className="data-row"
              key={p.patient_id}
            >
              <span className="avatar">{p.display_name.slice(0, 2)}</span>
              <strong>{p.display_name}</strong>
              <ChevronRight size={18} />
            </Link>
          ))}
      </section>
      <section className="panel">
        <h2>{t("invite")}</h2>
        <form onSubmit={invite}>
          <label>
            {t("email")}
            <input name="email" type="email" required />
          </label>
          <button className="primary" disabled={busy}>
            {t("invite")}
            <Plus size={18} />
          </button>
          {error && <p role="alert">{error}</p>}
          {sent && <p role="status">{t("inviteSent")}</p>}
        </form>
      </section>
    </div>
  );
}
export function ReviewView() {
  const patients = useResource<Patient[]>("therapist/patients");
  const [selected, setSelected] = useState("");
  useEffect(() => {
    setSelected(
      new URLSearchParams(window.location.search).get("patient") || "",
    );
  }, []);
  const id = selected || patients.data?.[0]?.patient_id || "";
  const responses = useResource<ResponseRecord[]>(
    id ? `therapist/patients/${encodeURIComponent(id)}/adherence` : null,
  );
  const { t, locale } = usePreferences();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  async function acknowledge(
    e: FormEvent<HTMLFormElement>,
    row: ResponseRecord,
  ) {
    e.preventDefault();
    setBusy(row.adherence_id);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      await api(
        `therapist/patients/${encodeURIComponent(id)}/adherence/${encodeURIComponent(row.adherence_id)}/acknowledge`,
        {
          method: "POST",
          body: JSON.stringify({
            disposition: form.get("disposition"),
            note: form.get("note") || null,
            clinician_attestation: form.get("attestation") === "on",
          }),
        },
      );
      responses.refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <div className="review-grid">
      <section className="panel">
        <h2>{t("patients")}</h2>
        <ResourceState {...patients} retry={patients.refresh} />
        {patients.data?.map((p) => (
          <button
            key={p.patient_id}
            className={`patient-choice ${p.patient_id === id ? "selected" : ""}`}
            onClick={() => setSelected(p.patient_id)}
          >
            <span className="avatar">{p.display_name.slice(0, 2)}</span>
            {p.display_name}
            <ChevronRight size={18} />
          </button>
        ))}
      </section>
      <section className="panel">
        <h2>
          {patients.data?.find((p) => p.patient_id === id)?.display_name ||
            t("review")}
        </h2>
        <ResourceState {...responses} retry={responses.refresh} />
        {id && (
          <>
            <Link
              className="secondary"
              href={`/workspace/plans/${encodeURIComponent(id)}`}
            >
              {t("carePlans")}
            </Link>
            <ProgressReportForm patientId={id} />
          </>
        )}
        {responses.data?.length === 0 && (
          <p className="empty">{t("noResponses")}</p>
        )}
        {responses.data?.map((row) => (
          <article className="review-response" key={row.adherence_id}>
            <strong>
              {new Intl.DateTimeFormat(locale, {
                dateStyle: "medium",
                timeZone: "UTC",
              }).format(new Date(row.scheduled_date + "T12:00:00Z"))}
            </strong>
            <p>
              {t(
                row.completion_status === "completed"
                  ? "complete"
                  : row.completion_status === "partial"
                    ? "partial"
                    : "missed",
              )}
            </p>
            <p>
              {t("painBefore")}: {row.pain_before ?? t("unavailable")} ·{" "}
              {t("painAfter")}: {row.pain_after ?? t("unavailable")}
            </p>
            {row.note && <p>{row.note}</p>}
            {row.analysis_session_id && (
              <Link
                className="text-link"
                href={`/workspace/result/${encodeURIComponent(row.analysis_session_id)}`}
              >
                {t("sessionDetails")}
              </Link>
            )}
            {row.supportive_instruction && (
              <p className="notice">{row.supportive_instruction}</p>
            )}
            {row.clinician_review_required && !row.reviewed_at ? (
              <ResponseReviewForm
                onSubmit={(event) => acknowledge(event, row)}
                busy={!!busy}
              />
            ) : (
              <p className="success">
                {t(row.reviewed_at ? "reviewSaved" : "noReviewRequired")}
              </p>
            )}
          </article>
        ))}
        {error && <p role="alert">{error}</p>}
      </section>
    </div>
  );
}

function ProgressReportForm({ patientId }: { patientId: string }) {
  const { t } = usePreferences();
  const now = new Date();
  const today = localCalendarDay(now);
  const priorDate = new Date(now);
  priorDate.setDate(priorDate.getDate() - 29);
  const prior = localCalendarDay(priorDate);
  const [start, setStart] = useState(prior);
  const [end, setEnd] = useState(today);
  const [share, setShare] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<ProgressReportCreateResponse | null>(
    null,
  );
  const reportLink = reportHref(report?.download_url);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validReportPeriod(start, end)) {
      setError(t("invalidReportPeriod"));
      return;
    }
    setBusy(true);
    setError("");
    setReport(null);
    try {
      setReport(
        await api<ProgressReportCreateResponse>(
          createReportPath(patientId, start, end, share),
          { method: "POST" },
        ),
      );
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <details className="report-creator">
      <summary>{t("createProgressReport")}</summary>
      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <label>
            {t("reportStart")}
            <input
              type="date"
              value={start}
              onChange={(event) => setStart(event.target.value)}
              required
            />
          </label>
          <label>
            {t("reportEnd")}
            <input
              type="date"
              value={end}
              onChange={(event) => setEnd(event.target.value)}
              required
            />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={share}
              onChange={(event) => setShare(event.target.checked)}
            />
            {t("shareReport")}
          </label>
          <button className="primary">
            {t(busy ? "loading" : "createProgressReport")}
          </button>
        </fieldset>
      </form>
      {error && <p role="alert">{error}</p>}
      {report && (
        <p role="status" className="success">
          {t("reportCreated")}{" "}
          {reportLink && (
            <a href={reportLink} target="_blank" rel="noopener noreferrer">
              {t("downloadReport")}
            </a>
          )}
        </p>
      )}
    </details>
  );
}

function ResponseReviewForm({
  onSubmit,
  busy,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
}) {
  const { t } = usePreferences();
  const [disposition, setDisposition] = useState<string>("reviewed_no_change");
  return (
    <form onSubmit={onSubmit}>
      <fieldset disabled={busy}>
        <label>
          {t("disposition")}
          <select
            name="disposition"
            value={disposition}
            onChange={(event) => setDisposition(event.target.value)}
          >
            {reviewDispositions.map((value) => (
              <option key={value} value={value}>
                {t(value)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("reviewNote")}
          <textarea
            name="note"
            required={disposition === "reviewed_no_change"}
            maxLength={2000}
          />
        </label>
        <label className="checkbox">
          <input type="checkbox" name="attestation" required />
          {t("attestation")}
        </label>
        <button className="primary">
          {t(busy ? "loading" : "reviewed")}
          <Check size={18} />
        </button>
      </fieldset>
    </form>
  );
}
