"use client";
import { useRef, useState } from "react";
import type { DataRightsRecord } from "../../../../../packages/contracts/generated";
import { api } from "../../lib/api";
import {
  newDataRightsKey,
  validDataRightsDetails,
} from "../../lib/data-rights.mjs";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";

function RequestRow({ row }: { row: DataRightsRecord }) {
  const { t, locale } = usePreferences();
  return (
    <article className="data-rights-row">
      <div>
        <strong>{t(`dataRightsType_${row.request_type}`)}</strong>
        <span className={`status-badge status-${row.status}`}>
          {t(`dataRightsStatus_${row.status}` as never)}
        </span>
      </div>
      {row.account_name && (
        <p>
          <strong>{row.account_name}</strong>
          <br />
          <span className="muted">{row.account_email}</span>
        </p>
      )}
      {row.details && <p className="preserve-lines">{row.details}</p>}
      <small>
        {new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
          new Date(row.created_at),
        )}
      </small>
      {row.retention_until && (
        <p>
          {t("retentionUntil")}:{" "}
          {new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(
            new Date(row.retention_until),
          )}
        </p>
      )}
    </article>
  );
}

export function PatientDataRights() {
  const { t } = usePreferences();
  const { data, error, loading, refresh } = useResource<DataRightsRecord[]>(
    "patient/data-rights-requests",
  );
  const [requestType, setRequestType] = useState("export");
  const [details, setDetails] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const key = useRef(newDataRightsKey());
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMessage("");
    if (!validDataRightsDetails(details))
      return setMessage(t("dataRightsTooLong"));
    setSaving(true);
    try {
      await api("patient/data-rights-requests", {
        method: "POST",
        headers: { "Idempotency-Key": key.current },
        body: JSON.stringify({
          request_type: requestType,
          details: details.trim() || null,
        }),
      });
      key.current = newDataRightsKey();
      setDetails("");
      setMessage(t("dataRightsSubmitted"));
      refresh();
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setSaving(false);
    }
  }
  return (
    <div className="narrow data-rights">
      <section className="panel">
        <h2>{t("dataRightsNew")}</h2>
        <p>{t("dataRightsIntro")}</p>
        <form onSubmit={submit}>
          <label>
            {t("requestType")}
            <select
              value={requestType}
              onChange={(e) => setRequestType(e.target.value)}
            >
              {(["export", "correction", "deletion"] as const).map((v) => (
                <option value={v} key={v}>
                  {t(`dataRightsType_${v}`)}
                </option>
              ))}
            </select>
          </label>
          {requestType === "deletion" && (
            <p className="warning" role="note">
              {t("deletionWarning")}
            </p>
          )}
          <label>
            {t("detailsOptional")}
            <textarea
              rows={5}
              maxLength={2001}
              value={details}
              onChange={(e) => setDetails(e.target.value)}
            />
          </label>
          <button className="primary" disabled={saving}>
            {saving ? t("loading") : t("submitRequest")}
          </button>
          {message && <p role="status">{message}</p>}
        </form>
      </section>
      <section className="panel">
        <h2>{t("requestHistory")}</h2>
        {loading ? (
          <p role="status">{t("loading")}</p>
        ) : error ? (
          <>
            <p role="alert">{error}</p>
            <button className="secondary" onClick={refresh}>
              {t("retry")}
            </button>
          </>
        ) : data?.length ? (
          data.map((row) => <RequestRow row={row} key={row.request_id} />)
        ) : (
          <p>{t("noDataRightsRequests")}</p>
        )}
      </section>
    </div>
  );
}

export function AdminDataRights() {
  const { t } = usePreferences();
  const { data, error, loading, refresh } = useResource<DataRightsRecord[]>(
    "admin/platform/data-rights-requests",
  );
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  async function review(row: DataRightsRecord, decision: "approve" | "reject") {
    const reason = reasons[row.request_id]?.trim() || "";
    if (reason.length < 3) return setMessage(t("reviewReasonRequired"));
    setBusy(row.request_id);
    setMessage("");
    try {
      await api(
        `admin/platform/data-rights-requests/${encodeURIComponent(row.request_id)}`,
        { method: "PATCH", body: JSON.stringify({ decision, reason }) },
      );
      setMessage(t("reviewSaved"));
      refresh();
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <section className="panel data-rights">
      <h2>{t("dataRightsQueue")}</h2>
      <p>{t("dataRightsAdminIntro")}</p>
      {message && <p role="status">{message}</p>}
      {loading ? (
        <p role="status">{t("loading")}</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : data?.length ? (
        data.map((row) => (
          <div key={row.request_id}>
            <RequestRow row={row} />
            {row.status === "pending" && (
              <div className="review-controls">
                <label>
                  {t("reviewReason")}
                  <textarea
                    rows={3}
                    maxLength={2000}
                    value={reasons[row.request_id] || ""}
                    onChange={(e) =>
                      setReasons({
                        ...reasons,
                        [row.request_id]: e.target.value,
                      })
                    }
                  />
                </label>
                <div className="button-row">
                  <button
                    className="primary"
                    disabled={busy === row.request_id}
                    onClick={() => review(row, "approve")}
                  >
                    {t("approve")}
                  </button>
                  <button
                    className="secondary"
                    disabled={busy === row.request_id}
                    onClick={() => review(row, "reject")}
                  >
                    {t("reject")}
                  </button>
                </div>
              </div>
            )}
          </div>
        ))
      ) : (
        <p>{t("noDataRightsRequests")}</p>
      )}
    </section>
  );
}
