import { useEffect, useState } from "react";
import { CalendarClock, ExternalLink, History, RefreshCw } from "lucide-react";
import { artifactUrl, getSavedSession, listSavedSessions } from "../services/api.js";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function SessionHistory() {
  const { t, exerciseText, pretty } = useLocale();
  const [exercise, setExercise] = useState("");
  const [status, setStatus] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const sessionExerciseName = (item) => {
    const id = item.exercise_id || item.exercise;
    return id ? exerciseText(id).name : item.exercise_display_name;
  };

  async function load() {
    setLoading(true);
    setError("");
    setSelected(null);
    try {
      const data = await listSavedSessions({
        ...(exercise ? { exercise_id: exercise } : {}),
        ...(status ? { status } : {}),
      });
      setSessions(data.items || []);
    } catch (requestError) {
      setError(requestError.response?.data?.message || t("history.loadError"));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, [exercise, status]);

  const visibleSessions = sortOrder === "oldest" ? [...sessions].reverse() : sessions;

  async function openDetail(sessionId) {
    try {
      setSelected(await getSavedSession(sessionId));
    } catch {
      setError(t("history.detailError"));
    }
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader
        eyebrow={t("history.eyebrow")}
        title={t("history.title")}
        description={t("history.description")}
        actions={<Button variant="secondary" onClick={load}><RefreshCw size={16} />{t("common.refresh")}</Button>}
      />
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <label className="text-sm font-semibold text-slate-600" htmlFor="history-exercise">{t("common.exercise")}</label>
        <select id="history-exercise" className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" value={exercise} onChange={(event) => setExercise(event.target.value)}>
          <option value="">{t("history.allExercises")}</option>
          {["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction", "push_up", "shoulder_press", "bicep_curl"].map((id) => <option key={id} value={id}>{exerciseText(id).name}</option>)}
        </select>
        <label className="text-sm font-semibold text-slate-600" htmlFor="history-status">{t("common.status")}</label>
        <select id="history-status" className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">{t("history.allStatuses")}</option><option value="success">{t("common.success")}</option><option value="rejected">{t("common.rejected")}</option></select>
        <label className="text-sm font-semibold text-slate-600" htmlFor="history-sort">{t("common.date")}</label>
        <select id="history-sort" className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" value={sortOrder} onChange={(event) => setSortOrder(event.target.value)}><option value="newest">{t("history.newest")}</option><option value="oldest">{t("history.oldest")}</option></select>
      </div>
      {error && <Alert title={t("history.unavailable")}>{error}</Alert>}
      {loading ? (
        <Card className="grid min-h-48 place-items-center"><LoadingSpinner label={t("history.loading")} /></Card>
      ) : sessions.length === 0 ? (
        <EmptyState title={t("history.emptyTitle")} description={t("history.emptyDescription")} icon={History} />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {visibleSessions.map((session) => (
            <Card key={session.session_id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-slate-500">{new Date(session.created_at).toLocaleString()}</p>
                  <h2 className="mt-1 text-lg font-bold text-clinical-ink">{sessionExerciseName(session)}</h2>
                </div>
                <Badge tone={session.status === "success" ? "teal" : "amber"}>{pretty(session.status)}</Badge>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                <div><p className="text-xs text-slate-500">{t("common.reps")}</p><p className="font-bold">{session.total_reps ?? "—"}</p></div>
                <div><p className="text-xs text-slate-500">{t("common.score")}</p><p className="font-bold">{session.movement_score ?? "—"}</p></div>
                <div><p className="text-xs text-slate-500">{t("common.confidence")}</p><p className="font-bold">{pretty(session.analysis_confidence_level || "unknown")}</p></div>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500">{session.detected_issues?.length ? session.detected_issues.map(pretty).join(", ") : t("history.noFlags")}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button variant="secondary" onClick={() => openDetail(session.session_id)}><CalendarClock size={15} />{t("history.viewDetails")}</Button>
                {session.report_download_url && <Button as="a" variant="ghost" href={artifactUrl(session.report_download_url)}><ExternalLink size={15} />{t("history.report")}</Button>}
                {session.overlay_preview_url && <Button as="a" variant="ghost" href={artifactUrl(session.overlay_preview_url)}><ExternalLink size={15} />{t("history.overlay")}</Button>}
              </div>
            </Card>
          ))}
        </div>
      )}
      {selected && (
        <Card className="mt-5 p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-clinical-teal">{t("history.detail")}</p>
              <h2 className="mt-1 text-xl font-bold">{sessionExerciseName(selected)}</h2>
            </div>
            <Badge tone="blue">{selected.session_id.slice(0, 8)}</Badge>
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">{selected.summary || selected.message || t("history.noSummary")}</p>
          {selected.feedback?.length > 0 && <ul className="mt-4 space-y-2 text-sm text-slate-600">{selected.feedback.map((item) => <li key={item}>• {item}</li>)}</ul>}
        </Card>
      )}
      <p className="mt-6 text-xs leading-5 text-slate-500">{t("history.notice")}</p>
    </main>
  );
}
