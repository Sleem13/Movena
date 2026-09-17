"use client";
import { useState } from "react";
import Link from "next/link";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "./Views";
import {
  historyPageSize,
  historyPath,
  historyRepetitions,
  historyStatuses,
  historyStatusKey,
} from "../../lib/history.mjs";
import { recordDate } from "../../lib/patient-account.mjs";
import { reportHref } from "../../lib/reports.mjs";
import type {
  ProgressReportSummary,
  SessionListResponse,
} from "../../../../../packages/contracts/generated";

export function ProgressView() {
  const [page, setPage] = useState({ offset: 0, status: "" });
  const { t, locale, exerciseName } = usePreferences();
  const resource = useResource<SessionListResponse>(
    historyPath(page.offset, page.status),
  );
  const reports = useResource<ProgressReportSummary[]>("patient/reports");
  const number = (value: number) => new Intl.NumberFormat(locale).format(value);
  return (
    <div className="history-stack">
      <section className="panel history-panel">
        <h2>{t("historyTitle")}</h2>
        <div className="history-controls">
          <label>
            {t("historyOutcome")}
            <select
              value={page.status}
              onChange={(event) =>
                setPage({ offset: 0, status: event.target.value })
              }
            >
              {historyStatuses.map((status) => (
                <option key={status} value={status}>
                  {t(status ? historyStatusKey(status) : "historyAll")}
                </option>
              ))}
            </select>
          </label>
          <button
            className="secondary"
            disabled={resource.loading}
            onClick={resource.refresh}
          >
            {t("historyRefresh")}
          </button>
        </div>
        <ResourceState {...resource} retry={resource.refresh} />
        {resource.data && (
          <>
            <p role="status" className="muted">
              {t("historyRecords")}: {number(resource.data.total)}
            </p>
            {resource.data.items.length === 0 && (
              <p className="empty">
                {t(
                  page.status || page.offset
                    ? "historyNoMatches"
                    : "noSessions",
                )}
              </p>
            )}
            {resource.data.items.map((session) => {
              const repetitions = historyRepetitions(session);
              return (
                <Link
                  className="data-row history-row"
                  key={session.session_id}
                  href={`/workspace/result/${encodeURIComponent(session.session_id)}?source=session`}
                >
                  <div>
                    <strong>
                      {locale === "ar"
                        ? exerciseName(session.exercise_id)
                        : session.exercise_display_name ||
                          exerciseName(session.exercise_id)}
                    </strong>
                    <small>
                      {recordDate(session.created_at, locale)} ·{" "}
                      {t(historyStatusKey(session.status))}
                    </small>
                  </div>
                  <span>
                    {repetitions === null
                      ? t("unavailable")
                      : `${number(repetitions)} ${t("reps")}`}
                  </span>
                </Link>
              );
            })}
          </>
        )}
        <nav className="history-controls" aria-label={t("historyPages")}>
          <button
            className="secondary"
            disabled={page.offset === 0}
            onClick={() =>
              setPage((p) => ({
                ...p,
                offset: Math.max(0, p.offset - historyPageSize),
              }))
            }
          >
            {t("historyNewer")}
          </button>
          <button
            className="secondary"
            disabled={
              resource.loading ||
              !resource.data ||
              page.offset + historyPageSize >= resource.data.total
            }
            onClick={() =>
              setPage((p) => ({ ...p, offset: p.offset + historyPageSize }))
            }
          >
            {t("historyOlder")}
          </button>
        </nav>
      </section>
      <section className="panel history-panel">
        <h2>{t("progressReports")}</h2>
        <ResourceState {...reports} retry={reports.refresh} />
        {reports.data?.length === 0 && (
          <p className="empty">{t("noProgressReports")}</p>
        )}
        {reports.data?.map((report) => (
          <article
            className="data-row history-row"
            key={report.progress_report_id}
          >
            <div>
              <strong>{t("reportPeriod")}</strong>
              <small>
                {recordDate(report.period_start, locale)} ·{" "}
                {recordDate(report.period_end, locale)}
              </small>
            </div>
            {reportHref(report.download_url) && (
              <a
                className="secondary compact"
                href={reportHref(report.download_url)!}
                target="_blank"
                rel="noopener noreferrer"
              >
                {t("downloadReport")}
              </a>
            )}
          </article>
        ))}
      </section>
    </div>
  );
}
