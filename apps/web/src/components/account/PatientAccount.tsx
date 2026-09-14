"use client";
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { coreClient } from "../../../../../packages/contracts/client";
import type {
  PatientHealthProfile,
  ConsentRecord,
  NotificationSummary,
} from "../../../../../packages/contracts/generated";
import { api } from "../../lib/api";
import {
  healthFields,
  healthPayload,
  notificationDestination,
  recordDate,
} from "../../lib/patient-account.mjs";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "../care/Views";
const client = coreClient(api);
export function HealthProfileView() {
  const profile = useResource<PatientHealthProfile>("patient/health-profile");
  const consents = useResource<ConsentRecord[]>("patient/consents");
  const { t, locale } = usePreferences();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [saved, setSaved] = useState(false);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const values = healthPayload(new FormData(event.currentTarget));
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await client.updateHealthProfile(values);
      setSaved(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const consentLabels: Record<string, string> = {
    privacy: t("consent_privacy"),
    terms: t("consent_terms"),
    care_data: t("consent_care_data"),
    media_upload: t("consent_media_upload"),
  };
  return (
    <div className="narrow">
      {!profile.data ? (
        <ResourceState {...profile} retry={profile.refresh} />
      ) : (
        <section className="panel">
          <p>{t("healthIntro")}</p>
          <form onSubmit={save} onChange={() => setSaved(false)}>
            <fieldset disabled={busy}>
              {healthFields.map(([key, label, max]) => (
                <label key={key}>
                  {t(label as "medicalSummary")}
                  {Number(max) > 120 ? (
                    <textarea
                      name={key}
                      maxLength={Number(max)}
                      rows={5}
                      defaultValue={
                        profile.data?.[key as keyof PatientHealthProfile] ?? ""
                      }
                    />
                  ) : (
                    <input
                      name={key}
                      type={key.endsWith("phone") ? "tel" : "text"}
                      maxLength={Number(max)}
                      defaultValue={
                        profile.data?.[key as keyof PatientHealthProfile] ?? ""
                      }
                      autoComplete="off"
                    />
                  )}
                </label>
              ))}
              {error && <p role="alert">{error}</p>}
              {saved && <p role="status">{t("changesSaved")}</p>}
              <button className="primary" disabled={busy}>
                {t(busy ? "loading" : "saveChanges")}
              </button>
            </fieldset>
          </form>
        </section>
      )}
      <section className="panel">
        <h2>{t("consentHistory")}</h2>
        {!consents.data ? (
          <ResourceState {...consents} retry={consents.refresh} />
        ) : consents.data.length === 0 ? (
          <p>{t("noConsents")}</p>
        ) : (
          consents.data.map((row, index) => (
            <article
              className="consent-record"
              key={`${row.consent_type}-${row.version}-${index}`}
            >
              <h3>{consentLabels[row.consent_type] ?? row.consent_type}</h3>
              <p>
                {t(row.accepted ? "consentAccepted" : "consentDeclined")} ·{" "}
                {t("consentVersion")} {row.version}
              </p>
              <p className="muted">{recordDate(row.accepted_at, locale)}</p>
            </article>
          ))
        )}
      </section>
    </div>
  );
}
export function NotificationsView() {
  const resource = useResource<NotificationSummary[]>("patient/notifications");
  const { t, locale } = usePreferences();
  const [busy, setBusy] = useState<string | null>(null),
    [error, setError] = useState("");
  const [readIds, setReadIds] = useState<Set<string>>(() => new Set());
  async function read(id: string) {
    if (busy) return;
    setBusy(id);
    setError("");
    try {
      await client.readNotification(id);
      setReadIds((old) => new Set([...old, id]));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }
  if (!resource.data)
    return <ResourceState {...resource} retry={resource.refresh} />;
  return (
    <div className="narrow">
      {error && <p role="alert">{error}</p>}
      {!resource.data.length && (
        <section className="panel">
          <p>{t("noNotifications")}</p>
        </section>
      )}
      {resource.data.map((row) => {
        const unread = !row.read_at && !readIds.has(row.notification_id),
          target = notificationDestination(row.action_url);
        return (
          <article className="panel notification" key={row.notification_id}>
            <span className={unread ? "status-badge" : "muted"}>
              {t(unread ? "unread" : "read")}
            </span>
            <h2>{row.title}</h2>
            <p className="preserve-lines">{row.body}</p>
            <p className="muted">{recordDate(row.created_at, locale)}</p>
            {target && (
              <Link className="secondary" href={target}>
                {t("openNotification")}
              </Link>
            )}
            {unread && (
              <button
                className="secondary"
                disabled={busy !== null}
                onClick={() => read(row.notification_id)}
              >
                {t(busy === row.notification_id ? "loading" : "markRead")}
              </button>
            )}
          </article>
        );
      })}
      {resource.data.length >= 100 && (
        <p className="fine-print">{t("inboxLimit")}</p>
      )}
    </div>
  );
}
