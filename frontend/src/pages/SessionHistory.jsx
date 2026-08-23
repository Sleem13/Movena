import { useEffect, useRef, useState } from "react";
import { CalendarClock, Download, ExternalLink, History, RefreshCw, X } from "lucide-react";
import { getArtifactBlob, getSavedSession, listSavedSessions } from "../services/api.js";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { artifactFilename } from "../utils/artifactFilenames.js";

export default function SessionHistory() {
  const { t, exerciseText, pretty } = useLocale();
  const [exercise, setExercise] = useState("");
  const [status, setStatus] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detailLoadingId, setDetailLoadingId] = useState(null);
  const [artifact, setArtifact] = useState({ status: "idle", kind: null, exerciseId: null, url: null, error: "" });
  const artifactUrlRef = useRef(null);
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
    if (selected?.session_id === sessionId) {
      setSelected(null);
      return;
    }
    setDetailLoadingId(sessionId);
    setError("");
    try {
      setSelected(await getSavedSession(sessionId));
    } catch {
      setError(t("history.detailError"));
    } finally {
      setDetailLoadingId(null);
    }
  }

  function closeArtifact() {
    if (artifactUrlRef.current) URL.revokeObjectURL(artifactUrlRef.current);
    artifactUrlRef.current = null;
    setArtifact({ status: "idle", kind: null, exerciseId: null, url: null, error: "" });
  }

  useEffect(() => closeArtifact, []);

  async function openArtifact(kind, path, exerciseId) {
    closeArtifact();
    setArtifact({ status: "loading", kind, exerciseId, url: null, error: "" });
    try {
      const blob = await getArtifactBlob(path);
      const url = URL.createObjectURL(blob);
      artifactUrlRef.current = url;
      setArtifact({ status: "ready", kind, exerciseId, url, error: "" });
    } catch (requestError) {
      const code = requestError.response?.data?.error_code;
      setArtifact({
        status: "error", kind, exerciseId, url: null,
        error: code === "ARTIFACT_NOT_FOUND" || requestError.response?.status === 404
          ? t("history.artifactExpired")
          : t("history.artifactError"),
      });
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
          {["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "shoulder_flexion", "hip_abduction", "walking_gait_screen", "balance", "push_up", "shoulder_press", "bicep_curl", "hammer_curl"].map((id) => <option key={id} value={id}>{exerciseText(id).name}</option>)}
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
                <Button variant="secondary" onClick={() => openDetail(session.session_id)} disabled={detailLoadingId === session.session_id} aria-expanded={selected?.session_id === session.session_id}>
                  <CalendarClock size={15} />{detailLoadingId === session.session_id ? t("history.loadingDetail") : selected?.session_id === session.session_id ? t("history.hideDetails") : t("history.viewDetails")}
                </Button>
                {session.report_download_url && <Button variant="ghost" onClick={() => openArtifact("report", session.report_download_url, session.exercise_id || session.exercise)}><ExternalLink size={15} />{t("history.report")}</Button>}
                {session.overlay_preview_url && <Button variant="ghost" onClick={() => openArtifact("overlay", session.overlay_preview_url, session.exercise_id || session.exercise)}><ExternalLink size={15} />{t("history.overlay")}</Button>}
              </div>
              {selected?.session_id === session.session_id && (
                <div className="mt-5 border-t border-slate-100 pt-5" aria-live="polite">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-wider text-clinical-teal">{t("history.detail")}</p>
                      <h3 className="mt-1 text-base font-bold">{sessionExerciseName(selected)}</h3>
                    </div>
                    <Badge tone="blue">{selected.session_id.slice(0, 8)}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{selected.summary || selected.message || t("history.noSummary")}</p>
                  {selected.feedback?.length > 0 && <ul className="mt-3 space-y-2 text-sm text-slate-600">{selected.feedback.map((item) => <li key={item}>• {item}</li>)}</ul>}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
      {artifact.status !== "idle" && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/55 p-4" role="dialog" aria-modal="true" aria-label={artifact.kind === "report" ? t("history.reportViewer") : t("history.overlayViewer")}>
          <Card className="w-full max-w-4xl overflow-hidden rounded-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 p-4">
              <h2 className="font-bold text-clinical-ink">{artifact.kind === "report" ? t("history.reportViewer") : t("history.overlayViewer")}</h2>
              <button type="button" onClick={closeArtifact} className="grid h-10 w-10 place-items-center rounded-xl text-slate-500 hover:bg-slate-100" aria-label={t("common.close")}><X size={19} /></button>
            </div>
            <div className="min-h-64 bg-slate-50 p-4">
              {artifact.status === "loading" && <div className="grid min-h-64 place-items-center"><LoadingSpinner label={t("history.loadingArtifact")} /></div>}
              {artifact.status === "error" && <Alert title={t("history.artifactUnavailable")}>{artifact.error}</Alert>}
              {artifact.status === "ready" && artifact.kind === "report" && <iframe title={t("history.reportViewer")} src={artifact.url} className="h-[70vh] w-full rounded-xl bg-white" />}
              {artifact.status === "ready" && artifact.kind === "overlay" && <video controls autoPlay className="max-h-[70vh] w-full rounded-xl bg-slate-950"><source src={artifact.url} type="video/mp4" /></video>}
            </div>
            {artifact.status === "ready" && <div className="flex justify-end border-t border-slate-100 p-4"><Button as="a" href={artifact.url} download={artifactFilename(artifact.exerciseId, artifact.kind)}><Download size={16} />{t("common.download")}</Button></div>}
          </Card>
        </div>
      )}
      <p className="mt-6 text-xs leading-5 text-slate-500">{t("history.notice")}</p>
    </main>
  );
}
