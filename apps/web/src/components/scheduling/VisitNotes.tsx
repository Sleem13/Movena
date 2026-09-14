"use client";
import { useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "../care/Views";
import { api, ApiError } from "../../lib/api";
import { recordDate } from "../../lib/patient-account.mjs";
import { notePayload, uncertainNote } from "../../lib/visit-notes.mjs";
import { coreClient } from "../../../../../packages/contracts/client";
import type {
  AppointmentSummary,
  ClinicalNoteDetail,
} from "../../../../../packages/contracts/generated";

export function VisitNotes({
  appointmentId,
  staff,
}: {
  appointmentId: string;
  staff: boolean;
}) {
  const { t, locale } = usePreferences();
  const path = `${staff ? "therapist" : "patient"}/appointments/${encodeURIComponent(appointmentId)}/session-notes`;
  const notes = useResource<ClinicalNoteDetail[]>(path);
  const appointments = useResource<AppointmentSummary[]>(
    `${staff ? "therapist" : "patient"}/appointments`,
  );
  const connections =
    useResource<
      {
        patient_id: string;
        therapist_user_id: string;
        patient_name: string;
        therapist_name: string;
      }[]
    >("connections");
  const appointment = appointments.data?.find(
    (row) => row.appointment_id === appointmentId,
  );
  const connection = connections.data?.find(
    (row) =>
      row.patient_id === appointment?.patient_id &&
      row.therapist_user_id === appointment?.therapist_user_id,
  );
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);
  return (
    <div className="narrow">
      <Link className="secondary" href="/workspace/schedule">
        {t("back")}
      </Link>
      <ResourceState {...appointments} retry={appointments.refresh} />
      {appointment && (
        <section aria-label={t("visitNotes")}>
          <h2>
            {new Intl.DateTimeFormat(locale, {
              dateStyle: "medium",
              timeStyle: "short",
            }).format(new Date(appointment.starts_at))}
          </h2>
          {connection && (
            <p>{staff ? connection.patient_name : connection.therapist_name}</p>
          )}
          <p className="muted">
            {t(
              appointment.delivery_mode === "video" ? "videoVisit" : "inPerson",
            )}
          </p>
        </section>
      )}
      <p className="muted">
        {staff ? t("visitNotesStaffHint") : t("visitNotesPatientHint")}
      </p>
      {saved && <p role="status">{t("visitNoteSaved")}</p>}
      <ResourceState {...notes} retry={notes.refresh} />
      {staff && !editing && notes.data && appointment && (
        <button
          className="primary"
          onClick={() => {
            setSaved(false);
            setEditing(true);
          }}
        >
          {t("addVisitNote")}
        </button>
      )}
      {staff && editing && (
        <NoteEditor
          appointmentId={appointmentId}
          onSaved={() => {
            setEditing(false);
            setSaved(true);
            notes.refresh();
          }}
        />
      )}
      {notes.data && notes.data.length === 0 && (
        <p className="panel">
          {t(staff ? "noVisitNotes" : "noSharedVisitNotes")}
        </p>
      )}
      {notes.data?.map((note) => (
        <article className="panel visit-note" key={note.note_id}>
          <p className="muted">
            {recordDate(note.created_at, locale)} ·{" "}
            {t(note.patient_visible ? "noteShared" : "notePrivate")}
          </p>
          {note.author_name && (
            <p>
              {t("noteAuthor")}: {note.author_name}
            </p>
          )}
          <h2>{t("visitSummary")}</h2>
          <p className="preserve-lines">{note.summary}</p>
          {note.recommendations && (
            <>
              <h3>{t("visitRecommendations")}</h3>
              <p className="preserve-lines">{note.recommendations}</p>
            </>
          )}
        </article>
      ))}
    </div>
  );
}
function NoteEditor({
  appointmentId,
  onSaved,
}: {
  appointmentId: string;
  onSaved: () => void;
}) {
  const { t } = usePreferences();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [uncertain, setUncertain] = useState(false);
  const request = useRef<{
    body: ReturnType<typeof notePayload>;
    key: string;
  } | null>(null);
  const sending = useRef(false);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sending.current) return;
    const body =
      uncertain && request.current
        ? request.current.body
        : notePayload(new FormData(event.currentTarget));
    if (!body.summary) {
      setError(t("requiredField"));
      return;
    }
    if (
      !request.current ||
      JSON.stringify(body) !== JSON.stringify(request.current.body)
    )
      request.current = { body, key: crypto.randomUUID() };
    sending.current = true;
    setBusy(true);
    setError("");
    try {
      await coreClient(api).createVisitNote(
        appointmentId,
        body,
        request.current.key,
      );
      onSaved();
    } catch (e) {
      setError((e as Error).message);
      setUncertain(uncertainNote(e instanceof ApiError ? e.status : 0));
    } finally {
      sending.current = false;
      setBusy(false);
    }
  }
  return (
    <form className="panel visit-note" onSubmit={save}>
      <h2>{t("addVisitNote")}</h2>
      <fieldset disabled={busy || uncertain}>
        <label>
          {t("visitSummary")}
          <textarea name="summary" required maxLength={10000} rows={6} />
        </label>
        <label>
          {t("visitRecommendations")}
          <textarea name="recommendations" maxLength={10000} rows={4} />
        </label>
        <label className="check-label">
          <input type="checkbox" name="patient_visible" />
          {t("shareVisitNote")}
        </label>
        <p className="muted">{t("noteVisibilityHint")}</p>
      </fieldset>
      {error && <p role="alert">{error}</p>}
      {uncertain && <p role="status">{t("noteUncertain")}</p>}
      <button className="primary" disabled={busy}>
        {t(busy ? "loading" : uncertain ? "retrySameNote" : "saveVisitNote")}
      </button>
    </form>
  );
}
