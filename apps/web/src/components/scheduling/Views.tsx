"use client";
import { useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { CalendarDays, Check, RefreshCw, Video } from "lucide-react";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "../care/Views";
import { api } from "../../lib/api";
import {
  calendarDay,
  shiftDay,
  minutes,
  visitUrl,
} from "../../lib/scheduling.mjs";
import { coreClient } from "../../../../../packages/contracts/client";
import type {
  AppointmentSummary,
  AppointmentSlot,
  AvailabilitySlots,
  AvailabilityDetail,
  AppointmentUpdate,
} from "../../../../../packages/contracts/generated";
import type { User } from "../../lib/types";

type Connection = {
  assignment_id: string;
  patient_id: string;
  therapist_user_id: string;
  patient_name: string;
  therapist_name: string;
  status: string;
};
const client = coreClient(api);
const weekdays = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
] as const;

export function ScheduleView({ user }: { user: User }) {
  const { t, locale } = usePreferences();
  const schedule = useResource<AppointmentSummary[]>(
    user.role === "patient" ? "patient/appointments" : "therapist/appointments",
  );
  const connections = useResource<Connection[]>("connections");
  const [booking, setBooking] = useState(false);
  const [revision, setRevision] = useState(0);
  const refresh = () => {
    schedule.refresh();
    setRevision((value) => value + 1);
  };
  const rows = [...(schedule.data ?? [])].sort(
    (a, b) => Date.parse(a.starts_at) - Date.parse(b.starts_at),
  );
  const upcoming = rows.filter(
    (row) =>
      ["scheduled", "confirmed"].includes(row.status) &&
      Date.parse(row.ends_at) >= Date.now(),
  );
  const history = rows.filter((row) => !upcoming.includes(row)).reverse();
  const active = (connections.data ?? []).filter(
    (row) => row.status === "active",
  );
  return (
    <div className="schedule-workspace">
      <div className="section-heading">
        <p className="muted">{t("deviceTimezone")}</p>
        <div className="button-row">
          <button
            className="secondary"
            onClick={refresh}
            aria-label={t("refresh")}
          >
            <RefreshCw size={18} />
          </button>
          <button
            className="primary"
            onClick={() => setBooking(!booking)}
            aria-expanded={booking}
          >
            <CalendarDays size={18} />
            {t("bookAppointment")}
          </button>
        </div>
      </div>
      {booking && (
        <section className="panel narrow">
          <h2>{t("bookAppointment")}</h2>
          <ResourceState {...connections} retry={connections.refresh} />
          {connections.data && (
            <BookingForm
              connections={active}
              locale={locale}
              revision={revision}
              onSaved={refresh}
            />
          )}
        </section>
      )}
      <ResourceState {...schedule} retry={schedule.refresh} />
      {schedule.data && (
        <div className="schedule-columns">
          {[
            [t("upcoming"), upcoming],
            [t("pastAppointments"), history],
          ].map(([heading, items]) => (
            <section key={heading as string}>
              <h2>{heading as string}</h2>
              {(items as AppointmentSummary[]).length === 0 && (
                <div className="panel empty">{t("noAppointments")}</div>
              )}
              <div className="appointment-list">
                {(items as AppointmentSummary[]).map((row) => (
                  <AppointmentCard
                    key={`${row.appointment_id}:${row.starts_at}:${row.status}`}
                    row={row}
                    staff={user.role !== "patient"}
                    connection={connections.data?.find(
                      (c) =>
                        c.patient_id === row.patient_id &&
                        c.therapist_user_id === row.therapist_user_id,
                    )}
                    onChanged={refresh}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
      {user.role === "therapist" && <AvailabilityEditor />}
    </div>
  );
}

function CalendarField({
  day,
  onChange,
  disabled = false,
}: {
  day: string;
  onChange: (day: string) => void;
  disabled?: boolean;
}) {
  const { t } = usePreferences();
  return (
    <div>
      <label>
        {t("calendarDay")}
        <input
          type="date"
          required
          min={calendarDay()}
          value={day}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
        />
      </label>
      <div className="button-row">
        <button
          type="button"
          className="secondary"
          disabled={disabled || !day || day <= calendarDay()}
          onClick={() => onChange(shiftDay(day, -1))}
        >
          {t("previousDay")}
        </button>
        <button
          type="button"
          className="secondary"
          disabled={disabled || !day}
          onClick={() => onChange(shiftDay(day, 1))}
        >
          {t("nextDay")}
        </button>
      </div>
    </div>
  );
}

function Slots({
  therapist,
  day,
  onSelect,
  selected,
}: {
  therapist: string;
  day: string;
  onSelect: (slot: AppointmentSlot) => void;
  selected: string;
}) {
  const { t, locale } = usePreferences();
  const resource = useResource<AvailabilitySlots>(
    therapist && day
      ? `scheduling/availability?therapist_user_id=${encodeURIComponent(therapist)}&day=${encodeURIComponent(day)}`
      : null,
  );
  const slots = (resource.data?.slots ?? []).filter(
    (slot) => Date.parse(slot.starts_at) > Date.now(),
  );
  return (
    <div>
      <ResourceState {...resource} retry={resource.refresh} />
      {resource.data && (
        <>
          <p>{t("chooseSlot")}</p>
          {!slots.length && <p className="empty">{t("noSlots")}</p>}
          <div className="slot-grid" role="group" aria-label={t("chooseSlot")}>
            {slots.map((slot) => (
              <button
                type="button"
                key={slot.starts_at}
                className={
                  selected === slot.starts_at ? "primary" : "secondary"
                }
                aria-pressed={selected === slot.starts_at}
                onClick={() => onSelect(slot)}
              >
                {new Intl.DateTimeFormat(locale, {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                  timeZoneName: "short",
                }).format(new Date(slot.starts_at))}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function BookingForm({
  connections,
  locale,
  revision,
  onSaved,
}: {
  connections: Connection[];
  locale: string;
  revision: number;
  onSaved: () => void;
}) {
  const { t } = usePreferences();
  const [connectionId, setConnectionId] = useState("");
  const [day, setDay] = useState(calendarDay());
  const [slot, setSlot] = useState<AppointmentSlot | null>(null);
  const [slotRevision, setSlotRevision] = useState(revision);
  const currentSlot = slotRevision === revision ? slot : null;
  const [mode, setMode] = useState<"video" | "in_person">("video");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState<AppointmentSummary | null>(null);
  const submission = useRef<{ body: string; key: string } | null>(null);
  const connection = connections.find(
    (row) => row.assignment_id === connectionId,
  );
  async function book(event: FormEvent) {
    event.preventDefault();
    if (!connection || !currentSlot || busy) return;
    const values = {
      patient_id: connection.patient_id,
      therapist_user_id: connection.therapist_user_id,
      starts_at: currentSlot.starts_at,
      ends_at: currentSlot.ends_at,
      delivery_mode: mode,
    };
    const body = JSON.stringify(values);
    if (submission.current?.body !== body)
      submission.current = { body, key: crypto.randomUUID() };
    setBusy(true);
    setError("");
    try {
      setSaved(await client.bookAppointment(values, submission.current.key));
      onSaved();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (saved)
    return (
      <div role="status">
        <Check />
        <h3>{t("bookingSaved")}</h3>
        <p>{new Date(saved.starts_at).toLocaleString(locale)}</p>
        <button
          className="secondary"
          onClick={() => {
            setSaved(null);
            setSlot(null);
            submission.current = null;
          }}
        >
          {t("bookAppointment")}
        </button>
      </div>
    );
  if (!connections.length) return <p className="empty">{t("noConnections")}</p>;
  return (
    <form onSubmit={book}>
      <fieldset disabled={busy}>
        <label>
          {t("careConnection")}
          <select
            value={connectionId}
            required
            onChange={(event) => {
              setConnectionId(event.target.value);
              setSlot(null);
            }}
          >
            <option value="">{t("chooseConnection")}</option>
            {connections.map((row) => (
              <option key={row.assignment_id} value={row.assignment_id}>
                {row.patient_name} · {row.therapist_name}
              </option>
            ))}
          </select>
        </label>
        <CalendarField
          day={day}
          onChange={(value) => {
            setDay(value);
            setSlot(null);
          }}
        />
        {connection && day && (
          <Slots
            key={`${connectionId}:${day}:${revision}`}
            therapist={connection.therapist_user_id}
            day={day}
            selected={currentSlot?.starts_at ?? ""}
            onSelect={(value) => {
              setSlot(value);
              setSlotRevision(revision);
            }}
          />
        )}
        <label>
          {t("deliveryMode")}
          <select
            value={mode}
            onChange={(event) => setMode(event.target.value as typeof mode)}
          >
            <option value="video">{t("videoVisit")}</option>
            <option value="in_person">{t("inPerson")}</option>
          </select>
        </label>
        <p className="fine-print">{t("bookingNoCharge")}</p>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <button className="primary" disabled={!currentSlot || !connection}>
          {t(busy ? "loading" : "bookAppointment")}
        </button>
      </fieldset>
    </form>
  );
}

function AppointmentCard({
  row,
  staff,
  connection,
  onChanged,
}: {
  row: AppointmentSummary;
  staff: boolean;
  connection?: Connection;
  onChanged: () => void;
}) {
  const { t, locale } = usePreferences();
  const [action, setAction] = useState<"cancel" | "reschedule" | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [ready, setReady] = useState<{ url: string; expires: string } | null>(
    null,
  );
  const [day, setDay] = useState(calendarDay());
  const [slot, setSlot] = useState<AppointmentSlot | null>(null);
  const active = ["scheduled", "confirmed"].includes(row.status);
  async function update(body: AppointmentUpdate) {
    setBusy(true);
    setError("");
    try {
      await client.updateAppointment(row.appointment_id, body);
      setAction(null);
      onChanged();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function join() {
    setBusy(true);
    setError("");
    try {
      const grant = await client.joinAppointment(row.appointment_id);
      setReady({ url: visitUrl(grant), expires: grant.expires_at });
    } catch (error) {
      setError(error instanceof Error ? error.message : t("joinUnavailable"));
    } finally {
      setBusy(false);
    }
  }
  const status =
    row.status === "cancelled" ? "appointmentCancelled" : row.status;
  const payment =
    (
      {
        pending: "pending",
        paid: "paid",
        unpaid: "unpaid",
        not_required: "not_required",
      } as const
    )[row.payment_status as "pending"] ?? "unavailable";
  return (
    <article className="panel appointment-card">
      <span className="appointment-status">{t(status)}</span>
      <h3>
        {new Intl.DateTimeFormat(locale, {
          dateStyle: "medium",
          timeStyle: "short",
        }).format(new Date(row.starts_at))}
      </h3>
      {connection && (
        <p>{staff ? connection.patient_name : connection.therapist_name}</p>
      )}
      <p className="muted">
        {t(row.delivery_mode === "video" ? "videoVisit" : "inPerson")} ·{" "}
        {t("paymentStatus")}: {t(payment)}
      </p>
      <Link
        className="secondary"
        href={`/workspace/visit-notes/${encodeURIComponent(row.appointment_id)}`}
      >
        {t("visitNotes")}
      </Link>
      {active && row.delivery_mode === "video" && (
        <div>
          {ready ? (
            <a
              className="primary"
              href={ready.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(event) => {
                if (Date.parse(ready.expires) <= Date.now()) {
                  event.preventDefault();
                  setReady(null);
                  setError(t("joinUnavailable"));
                }
              }}
            >
              <Video size={18} />
              {t("openVisit")}
            </a>
          ) : (
            <button
              className="primary"
              onClick={join}
              disabled={busy || !row.can_join}
            >
              <Video size={18} />
              {t(row.can_join ? "joinVisit" : "joinWindow")}
            </button>
          )}
        </div>
      )}
      {active && (
        <div className="button-row">
          <button
            className="secondary"
            disabled={busy}
            onClick={() =>
              setAction(action === "reschedule" ? null : "reschedule")
            }
          >
            {t("reschedule")}
          </button>
          <button
            className="secondary"
            disabled={busy}
            onClick={() => setAction(action === "cancel" ? null : "cancel")}
          >
            {t("cancelAppointment")}
          </button>
        </div>
      )}
      {staff && active && (
        <div className="button-row staff-actions">
          {row.status === "scheduled" && (
            <button
              className="text-button"
              disabled={busy}
              onClick={() => update({ status: "confirmed" })}
            >
              {t("confirmAppointment")}
            </button>
          )}
          <button
            className="text-button"
            disabled={busy}
            onClick={() => update({ status: "completed" })}
          >
            {t("completeAppointment")}
          </button>
          <button
            className="text-button"
            disabled={busy}
            onClick={() => update({ status: "no_show" })}
          >
            {t("noShowAppointment")}
          </button>
        </div>
      )}
      {action === "cancel" && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            const data = new FormData(event.currentTarget);
            void update({
              status: "cancelled",
              cancellation_reason: String(data.get("reason")).trim(),
            });
          }}
        >
          <label>
            {t("cancellationReason")}
            <textarea name="reason" maxLength={500} required disabled={busy} />
          </label>
          <button className="primary" disabled={busy}>
            {t(busy ? "loading" : "cancelAppointment")}
          </button>
        </form>
      )}
      {action === "reschedule" && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            if (slot) void update(slot);
          }}
        >
          <CalendarField
            day={day}
            disabled={busy}
            onChange={(value) => {
              setDay(value);
              setSlot(null);
            }}
          />
          <fieldset disabled={busy}>
            <Slots
              key={day}
              therapist={row.therapist_user_id}
              day={day}
              selected={slot?.starts_at ?? ""}
              onSelect={setSlot}
            />
          </fieldset>
          <button className="primary" disabled={busy || !slot}>
            {t("saveAppointment")}
          </button>
        </form>
      )}
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
    </article>
  );
}

function AvailabilityEditor() {
  const { t, locale } = usePreferences();
  const resource = useResource<AvailabilityDetail[]>("therapist/availability");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const start = minutes(String(data.get("start"))),
      end = minutes(String(data.get("end")));
    if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
      setError(t("invalidTimeRange"));
      return;
    }
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await client.addAvailability({
        weekday: Number(data.get("weekday")),
        start_minute: start,
        end_minute: end,
        timezone_name: String(data.get("timezone")).trim(),
      });
      setSaved(true);
      resource.refresh();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel availability-editor">
      <h2>{t("availability")}</h2>
      <ResourceState {...resource} retry={resource.refresh} />
      {resource.data?.length === 0 && <p>{t("noAvailability")}</p>}
      {resource.data?.map((row) => (
        <p key={row.availability_id}>
          {t(weekdays[row.weekday])} ·{" "}
          {new Intl.DateTimeFormat(locale, {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: "UTC",
          }).format(new Date(Date.UTC(2026, 0, 5, 0, row.start_minute)))}
          –
          {new Intl.DateTimeFormat(locale, {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: "UTC",
          }).format(new Date(Date.UTC(2026, 0, 5, 0, row.end_minute)))}{" "}
          · <bdi>{row.timezone_name}</bdi>
        </p>
      ))}
      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <div className="form-columns">
            <label>
              {t("weekday")}
              <select name="weekday">
                {weekdays.map((day, index) => (
                  <option key={day} value={index}>
                    {t(day)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ianaTimezone")}
              <input
                name="timezone"
                defaultValue="UTC"
                required
                maxLength={64}
              />
            </label>
          </div>
          <div className="form-columns">
            <label>
              {t("startTime")}
              <input type="time" name="start" required defaultValue="09:00" />
            </label>
            <label>
              {t("endTime")}
              <input type="time" name="end" required defaultValue="17:00" />
            </label>
          </div>
          <button className="primary">
            {t(busy ? "loading" : "addAvailability")}
          </button>
        </fieldset>
      </form>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {saved && (
        <p role="status" className="success">
          {t("availabilitySaved")}
        </p>
      )}
    </section>
  );
}
