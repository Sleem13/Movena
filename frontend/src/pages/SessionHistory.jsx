import { useEffect, useState } from "react";
import { CalendarClock, ExternalLink, History, RefreshCw } from "lucide-react";
import {
  artifactUrl,
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
import { PageHeader } from "../components/layout/AppShell.jsx";

const pretty = (value = "") =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function SessionHistory() {
  const [exercise, setExercise] = useState("");
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    setSelected(null);
    try {
      const data = await listSavedSessions(
        exercise ? { exercise_id: exercise } : {},
      );
      setSessions(data.items || []);
    } catch (requestError) {
      setError(
        requestError.response?.data?.message ||
          "Session history could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, [exercise]);

  async function openDetail(sessionId) {
    try {
      setSelected(await getSavedSession(sessionId));
    } catch {
      setError("Saved session detail could not be loaded.");
    }
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader
        eyebrow="Local development history"
        title="Saved sessions"
        description="Analysis metadata saved in the current local database. Do not use this as a patient record system."
        actions={
          <Button variant="secondary" onClick={load}>
            <RefreshCw size={16} />
            Refresh
          </Button>
        }
      />
      <div className="mb-5 flex items-center gap-3">
        <label
          className="text-sm font-semibold text-slate-600"
          htmlFor="history-exercise"
        >
          Exercise
        </label>
        <select
          id="history-exercise"
          className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
          value={exercise}
          onChange={(event) => setExercise(event.target.value)}
        >
          <option value="">All exercises</option>
          <option value="bodyweight_squat">Bodyweight Squat</option>
          <option value="sit_to_stand">Sit-to-Stand</option>
          <option value="knee_extension">Knee Extension</option>
          <option value="shoulder_abduction">Shoulder Abduction</option>
        </select>
      </div>
      {error && <Alert title="History unavailable">{error}</Alert>}
      {loading ? (
        <Card className="grid min-h-48 place-items-center">
          <LoadingSpinner label="Loading sessions" />
        </Card>
      ) : sessions.length === 0 ? (
        <EmptyState
          title="No saved sessions yet. Analyze a video and enable Save Session."
          description="Only analysis metadata is stored locally; uploaded videos are not retained."
          icon={History}
        />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {sessions.map((session) => (
            <Card key={session.session_id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-slate-500">
                    {new Date(session.created_at).toLocaleString()}
                  </p>
                  <h2 className="mt-1 text-lg font-bold text-clinical-ink">
                    {session.exercise_display_name}
                  </h2>
                </div>
                <Badge tone={session.status === "success" ? "teal" : "amber"}>
                  {pretty(session.status)}
                </Badge>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <p className="text-xs text-slate-500">Reps</p>
                  <p className="font-bold">{session.total_reps ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Score</p>
                  <p className="font-bold">{session.movement_score ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Confidence</p>
                  <p className="font-bold">
                    {pretty(session.analysis_confidence_level || "unknown")}
                  </p>
                </div>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500">
                {session.detected_issues?.length
                  ? session.detected_issues.map(pretty).join(", ")
                  : "No saved issue flags."}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button
                  variant="secondary"
                  onClick={() => openDetail(session.session_id)}
                >
                  <CalendarClock size={15} />
                  View details
                </Button>
                {session.report_download_url && (
                  <Button
                    as="a"
                    variant="ghost"
                    href={artifactUrl(session.report_download_url)}
                  >
                    <ExternalLink size={15} />
                    Report
                  </Button>
                )}
                {session.overlay_preview_url && (
                  <Button
                    as="a"
                    variant="ghost"
                    href={artifactUrl(session.overlay_preview_url)}
                  >
                    <ExternalLink size={15} />
                    Overlay
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
      {selected && (
        <Card className="mt-5 p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-clinical-teal">
                Saved session detail
              </p>
              <h2 className="mt-1 text-xl font-bold">
                {selected.exercise_display_name}
              </h2>
            </div>
            <Badge tone="blue">{selected.session_id.slice(0, 8)}</Badge>
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            {selected.summary || selected.message || "No summary was saved."}
          </p>
          {selected.feedback?.length > 0 && (
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              {selected.feedback.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          )}
        </Card>
      )}
      <p className="mt-6 text-xs leading-5 text-slate-500">
        Development authentication is enabled, but this is not a medical
        record. Do not store real names, diagnoses, or identifying information.
      </p>
    </main>
  );
}
