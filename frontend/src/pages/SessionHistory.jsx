import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  CalendarClock,
  Check,
  Download,
  ExternalLink,
  GitCompareArrows,
  History,
  Radio,
  RefreshCw,
  UploadCloud,
  X,
} from "lucide-react";
import {
  getArtifactBlob,
  getSavedSession,
  listSavedSessions,
} from "../services/api.js";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  LoadingSpinner,
} from "../components/common/UI.jsx";
import Select from "../components/common/Select.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { getApiErrorMessage } from "../utils/requestErrors.js";
import { useAuth } from "../context/AuthContext.jsx";
import { artifactFilename } from "../utils/artifactFilenames.js";
import SessionComparison from "../components/history/SessionComparison.jsx";

const HISTORY_EXERCISES = [
  "bodyweight_squat",
  "sit_to_stand",
  "knee_extension",
  "shoulder_abduction",
  "shoulder_flexion",
  "hip_abduction",
  "walking_gait_screen",
  "balance",
  "push_up",
  "shoulder_press",
  "bicep_curl",
  "hammer_curl",
];

export default function SessionHistory({ onAnalyze, onCoach }) {
  const { t, exerciseText, pretty } = useLocale();
  const { user } = useAuth();
  const [exercise, setExercise] = useState("");
  const [status, setStatus] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [comparisonIds, setComparisonIds] = useState([]);
  const [comparisonDetails, setComparisonDetails] = useState([]);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonError, setComparisonError] = useState("");
  const [detailLoadingId, setDetailLoadingId] = useState(null);
  const [artifact, setArtifact] = useState({
    status: "idle",
    kind: null,
    exerciseId: null,
    url: null,
    error: "",
  });
  const artifactUrlRef = useRef(null);
  const artifactCloseRef = useRef(null);
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
    setComparisonIds([]);
    setComparisonDetails([]);
    setComparisonError("");
    try {
      const data = await listSavedSessions({
        ...(exercise ? { exercise_id: exercise } : {}),
        ...(status ? { status } : {}),
      });
      setSessions(data.items || []);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, t("history.loadError")));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, [exercise, status]);

  const visibleSessions =
    sortOrder === "oldest" ? [...sessions].reverse() : sessions;
  const comparisonSessions = comparisonIds
    .map((id) => sessions.find((item) => item.session_id === id))
    .filter(Boolean);

  function toggleComparison(session) {
    setComparisonError("");
    setComparisonDetails([]);
    setComparisonIds((current) => {
      if (current.includes(session.session_id))
        return current.filter((id) => id !== session.session_id);
      if (current.length >= 2) return current;
      const first = sessions.find((item) => item.session_id === current[0]);
      if (first && first.exercise_id !== session.exercise_id) return current;
      return [...current, session.session_id];
    });
  }

  useEffect(() => {
    if (comparisonIds.length !== 2) return undefined;
    let active = true;
    setComparisonLoading(true);
    setComparisonError("");
    Promise.all(comparisonIds.map((id) => getSavedSession(id)))
      .then((items) => {
        if (active) setComparisonDetails(items);
      })
      .catch(() => {
        if (active) setComparisonError(t("history.compareError"));
      })
      .finally(() => {
        if (active) setComparisonLoading(false);
      });
    return () => {
      active = false;
    };
  }, [comparisonIds, t]);

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
    setArtifact({
      status: "idle",
      kind: null,
      exerciseId: null,
      url: null,
      error: "",
    });
  }

  useEffect(() => closeArtifact, []);

  useEffect(() => {
    if (artifact.status === "idle") return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    requestAnimationFrame(() => artifactCloseRef.current?.focus());
    function handleKeyDown(event) {
      if (event.key === "Escape") closeArtifact();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [artifact.status]);

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
        status: "error",
        kind,
        exerciseId,
        url: null,
        error:
          code === "ARTIFACT_NOT_FOUND" || requestError.response?.status === 404
            ? t("history.artifactExpired")
            : t("history.artifactError"),
      });
    }
  }

  return (
    <main>
      <PageHeader
        title={
          user?.role === "patient"
            ? t("history.patientTitle")
            : user?.role === "therapist"
              ? t("history.therapistTitle")
              : t("history.title")
        }
        description={
          user?.role === "patient"
            ? t("history.patientDescription")
            : t("history.description")
        }
        actions={
          <Button variant="secondary" onClick={load}>
            <RefreshCw size={16} />
            {t("common.refresh")}
          </Button>
        }
      />
      <div className="mb-5 grid gap-3 sm:grid-cols-3 lg:flex lg:flex-wrap lg:items-end">
        <div className="min-w-48">
          <label
            className="mb-1.5 block text-xs font-semibold text-slate-600"
            htmlFor="history-exercise"
          >
            {t("common.exercise")}
          </label>
          <Select
            id="history-exercise"
            ariaLabel={t("common.exercise")}
            value={exercise}
            onChange={setExercise}
            options={[
              { value: "", label: t("history.allExercises") },
              ...HISTORY_EXERCISES.map((item) => ({
                value: item,
                label: exerciseText(item).name,
              })),
            ]}
          />
        </div>
        <div className="min-w-40">
          <label
            className="mb-1.5 block text-xs font-semibold text-slate-600"
            htmlFor="history-status"
          >
            {t("common.status")}
          </label>
          <Select
            id="history-status"
            ariaLabel={t("common.status")}
            value={status}
            onChange={setStatus}
            options={[
              { value: "", label: t("history.allStatuses") },
              { value: "success", label: t("common.success") },
              { value: "rejected", label: t("common.rejected") },
            ]}
          />
        </div>
        <div className="min-w-40">
          <label
            className="mb-1.5 block text-xs font-semibold text-slate-600"
            htmlFor="history-sort"
          >
            {t("common.date")}
          </label>
          <Select
            id="history-sort"
            ariaLabel={t("common.date")}
            value={sortOrder}
            onChange={setSortOrder}
            options={[
              { value: "newest", label: t("history.newest") },
              { value: "oldest", label: t("history.oldest") },
            ]}
          />
        </div>
      </div>
      {error && <Alert title={t("history.unavailable")}>{error}</Alert>}
      <SessionComparison
        selected={comparisonSessions}
        details={comparisonDetails}
        loading={comparisonLoading}
        error={comparisonError}
        onClear={() => {
          setComparisonIds([]);
          setComparisonDetails([]);
          setComparisonError("");
        }}
      />
      {loading ? (
        <Card className="grid min-h-48 place-items-center">
          <LoadingSpinner label={t("history.loading")} />
        </Card>
      ) : sessions.length === 0 ? (
        <EmptyState
          title={t("history.emptyTitle")}
          description={t("history.emptyDescription")}
          icon={History}
          actions={
            <>
              <Button onClick={onAnalyze}>
                <UploadCloud size={16} />
                {user?.role === "patient"
                  ? t("nav.aiExerciseCoach")
                  : t("nav.movementAnalysis")}
              </Button>
              {onCoach ? (
                <Button variant="secondary" onClick={onCoach}>
                  <Radio size={16} />
                  {t("nav.coach")}
                </Button>
              ) : null}
            </>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
          {visibleSessions.map((session) => (
            <Card
              key={session.session_id}
              className="rounded-none border-0 border-b border-slate-200 p-5 shadow-none ring-0 last:border-b-0 hover:bg-slate-50/70"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-slate-500">
                    {new Date(session.created_at).toLocaleString()}
                  </p>
                  <h2 className="mt-1 text-lg font-bold text-clinical-ink">
                    {sessionExerciseName(session)}
                  </h2>
                </div>
                <Badge tone={session.status === "success" ? "teal" : "amber"}>
                  {pretty(session.status)}
                </Badge>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <p className="text-xs text-slate-500">{t("common.reps")}</p>
                  <p className="font-bold">{session.total_reps ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">{t("common.score")}</p>
                  <p className="font-bold">{session.movement_score ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">
                    {t("common.confidence")}
                  </p>
                  <p className="font-bold">
                    {pretty(session.analysis_confidence_level || "unknown")}
                  </p>
                </div>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500">
                {session.detected_issues?.length
                  ? session.detected_issues.map(pretty).join(", ")
                  : t("history.noFlags")}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button
                  variant={
                    comparisonIds.includes(session.session_id)
                      ? "primary"
                      : "secondary"
                  }
                  onClick={() => toggleComparison(session)}
                  disabled={
                    (comparisonIds.length >= 2 &&
                      !comparisonIds.includes(session.session_id)) ||
                    Boolean(
                      comparisonSessions[0] &&
                      comparisonSessions[0].exercise_id !== session.exercise_id,
                    )
                  }
                  aria-pressed={comparisonIds.includes(session.session_id)}
                  title={
                    comparisonSessions[0] &&
                    comparisonSessions[0].exercise_id !== session.exercise_id
                      ? t("history.compareSameExercise")
                      : undefined
                  }
                >
                  {comparisonIds.includes(session.session_id) ? (
                    <Check size={15} />
                  ) : (
                    <GitCompareArrows size={15} />
                  )}
                  {t("history.compareAction")}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => openDetail(session.session_id)}
                  disabled={detailLoadingId === session.session_id}
                  aria-expanded={selected?.session_id === session.session_id}
                >
                  <CalendarClock size={15} />
                  {detailLoadingId === session.session_id
                    ? t("history.loadingDetail")
                    : selected?.session_id === session.session_id
                      ? t("history.hideDetails")
                      : t("history.viewDetails")}
                </Button>
                {session.report_download_url && (
                  <Button
                    variant="ghost"
                    onClick={() =>
                      openArtifact(
                        "report",
                        session.report_download_url,
                        session.exercise_id || session.exercise,
                      )
                    }
                  >
                    <ExternalLink size={15} />
                    {t("history.report")}
                  </Button>
                )}
                {session.overlay_preview_url && (
                  <Button
                    variant="ghost"
                    onClick={() =>
                      openArtifact(
                        "overlay",
                        session.overlay_preview_url,
                        session.exercise_id || session.exercise,
                      )
                    }
                  >
                    <ExternalLink size={15} />
                    {t("history.overlay")}
                  </Button>
                )}
              </div>
              {selected?.session_id === session.session_id && (
                <div
                  className="mt-5 border-t border-slate-100 pt-5"
                  aria-live="polite"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-wider text-clinical-teal">
                        {t("history.detail")}
                      </p>
                      <h3 className="mt-1 text-base font-bold">
                        {sessionExerciseName(selected)}
                      </h3>
                    </div>
                    <Badge tone="blue">{selected.session_id.slice(0, 8)}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {selected.summary ||
                      selected.message ||
                      t("history.noSummary")}
                  </p>
                  {selected.feedback?.length > 0 && (
                    <ul className="mt-3 space-y-2 text-sm text-slate-600">
                      {selected.feedback.map((item) => (
                        <li key={item}>• {item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
      {artifact.status !== "idle" &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] overflow-y-auto p-4"
            role="dialog"
            aria-modal="true"
            aria-label={
              artifact.kind === "report"
                ? t("history.reportViewer")
                : t("history.overlayViewer")
            }
          >
            <button
              type="button"
              className="fixed inset-0 cursor-default bg-slate-950/60 backdrop-blur-[2px]"
              onClick={closeArtifact}
              aria-label={t("common.close")}
            />
            <div className="relative grid min-h-full place-items-center">
              <Card className="relative z-10 flex max-h-[calc(100vh-2rem)] w-full max-w-4xl flex-col overflow-hidden rounded-2xl shadow-2xl">
                <div className="flex shrink-0 items-center justify-between border-b border-slate-100 bg-white p-4">
                  <h2 className="font-bold text-clinical-ink">
                    {artifact.kind === "report"
                      ? t("history.reportViewer")
                      : t("history.overlayViewer")}
                  </h2>
                  <button
                    ref={artifactCloseRef}
                    type="button"
                    onClick={closeArtifact}
                    className="grid h-10 w-10 shrink-0 place-items-center rounded-xl text-slate-500 transition hover:bg-slate-100 hover:text-clinical-ink focus-visible:ring-2 focus-visible:ring-blue-400"
                    aria-label={t("common.close")}
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="min-h-0 flex-1 overflow-auto bg-slate-50 p-4">
                  {artifact.status === "loading" && (
                    <div className="grid min-h-64 place-items-center">
                      <LoadingSpinner label={t("history.loadingArtifact")} />
                    </div>
                  )}
                  {artifact.status === "error" && (
                    <Alert title={t("history.artifactUnavailable")}>
                      {artifact.error}
                    </Alert>
                  )}
                  {artifact.status === "ready" &&
                    artifact.kind === "report" && (
                      <iframe
                        title={t("history.reportViewer")}
                        src={artifact.url}
                        className="h-[min(70vh,720px)] min-h-80 w-full rounded-xl bg-white"
                      />
                    )}
                  {artifact.status === "ready" &&
                    artifact.kind === "overlay" && (
                      <video
                        controls
                        playsInline
                        preload="auto"
                        src={artifact.url}
                        className="max-h-[70vh] w-full rounded-xl bg-slate-950 [backface-visibility:hidden] [transform:translateZ(0)]"
                      />
                    )}
                </div>
                {artifact.status === "ready" && (
                  <div className="flex shrink-0 justify-end border-t border-slate-100 bg-white p-4">
                    <Button
                      as="a"
                      href={artifact.url}
                      download={artifactFilename(
                        artifact.exerciseId,
                        artifact.kind,
                      )}
                    >
                      <Download size={16} />
                      {t("common.download")}
                    </Button>
                  </div>
                )}
              </Card>
            </div>
          </div>,
          document.body,
        )}
      <p className="mt-6 text-xs leading-5 text-slate-500">
        {t("history.notice")}
      </p>
    </main>
  );
}
