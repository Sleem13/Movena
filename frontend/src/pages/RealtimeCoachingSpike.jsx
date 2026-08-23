import { useEffect, useRef, useState } from "react";
import { BrainCircuit, Camera, CheckCircle2, Info, ShieldCheck, Square } from "lucide-react";

import { Card, Alert, Button, Badge } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import RecognitionUploadCard from "../components/recognition/RecognitionUploadCard.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { getCoachingReadiness, getRecognitionModels } from "../services/api.js";
import { getLocalPoseLandmarkExtractor } from "../services/poseLandmarkExtractor.js";
import { connectRealtimeCoaching } from "../services/realtimeCoaching.js";

const SAMPLE_INTERVAL_MS = 125;
const SAMPLE_WIDTH = 160;
const SAMPLE_HEIGHT = 90;
const MAX_SAMPLES = 20;
const POSE_CONNECTIONS = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], [11, 23], [12, 24], [23, 24],
  [23, 25], [25, 27], [27, 29], [29, 31], [24, 26], [26, 28], [28, 30], [30, 32],
];
const EXERCISES = ["bicep_curl", "hammer_curl", "bodyweight_squat", "shoulder_press", "shoulder_abduction"];
const WORKING_LANDMARKS = {
  bicep_curl: [11, 12, 13, 14, 15, 16],
  hammer_curl: [11, 12, 13, 14, 15, 16],
  bodyweight_squat: [23, 24, 25, 26, 27, 28],
  shoulder_press: [11, 12, 13, 14, 15, 16],
  shoulder_abduction: [11, 12, 13, 14, 15, 16, 23, 24],
};

const CAMERA_ERROR_KEYS = {
  NotFoundError: "coach.noCameraError",
  DevicesNotFoundError: "coach.noCameraError",
  NotAllowedError: "coach.permissionDeniedError",
  PermissionDeniedError: "coach.permissionDeniedError",
  SecurityError: "coach.permissionDeniedError",
  NotReadableError: "coach.cameraBusyError",
  TrackStartError: "coach.cameraBusyError",
  OverconstrainedError: "coach.cameraConstraintsError",
  ConstraintNotSatisfiedError: "coach.cameraConstraintsError",
};

const PHASE_CUE_KEYS = {
  seeking_start: "coach.cue.seekingStart",
  ready: "coach.cue.ready",
  working: "coach.cue.working",
  returning: "coach.cue.returning",
};

export function coachingCueKey(status, phase) {
  if (status === "connecting") return "coach.cue.connecting";
  if (status === "active") return PHASE_CUE_KEYS[phase] || "coach.cue.tracking";
  if (status === "saved") return "coach.cue.saved";
  return "coach.cue.idle";
}

export function cameraErrorMessageKey(error) {
  return CAMERA_ERROR_KEYS[error?.name] || "coach.permissionError";
}

export function summarizeFrame(canvas) {
  const context = canvas.getContext("2d", { willReadFrequently: true });
  if (!context) return null;
  const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
  let brightness = 0;
  let visiblePixels = 0;
  for (let index = 0; index < data.length; index += 4) {
    const alpha = data[index + 3] / 255;
    const value = (data[index] + data[index + 1] + data[index + 2]) / 3;
    brightness += value;
    if (alpha > 0 && value > 20) visiblePixels += 1;
  }
  const pixelCount = data.length / 4 || 1;
  return {
    brightness: Math.round(brightness / pixelCount),
    visibilityProxy: Math.round((visiblePixels / pixelCount) * 100),
    capturedAt: new Date().toISOString(),
  };
}

export async function readOptionalLandmarkSummary(videoElement, localExtractor) {
  const extractor = localExtractor || window.physioVisionLandmarkExtractor;
  if (!extractor || typeof extractor.estimate !== "function") {
    return { enabled: false, landmarkCount: 0, averageConfidence: null };
  }
  const result = await extractor.estimate(videoElement);
  const landmarks = Array.isArray(result?.landmarks) ? result.landmarks : [];
  const confidenceValues = landmarks
    .map((item) => item.visibility ?? item.score ?? item.confidence)
    .filter((value) => Number.isFinite(value));
  const averageConfidence = confidenceValues.length
    ? confidenceValues.reduce((sum, value) => sum + value, 0) / confidenceValues.length
    : null;
  return {
    enabled: true,
    landmarkCount: landmarks.length,
    averageConfidence: averageConfidence == null ? null : Number(averageConfidence.toFixed(3)),
    landmarks,
    hands: Array.isArray(result?.hands) ? result.hands : [],
  };
}

export function drawPoseOverlay(canvas, landmarks, exerciseId) {
  const context = canvas?.getContext("2d");
  if (!context) return;
  context.clearRect(0, 0, canvas.width, canvas.height);
  if (!Array.isArray(landmarks) || landmarks.length < 29) return;
  const visible = (point) => point && (point.visibility ?? 1) >= 0.5;
  const highlighted = new Set(WORKING_LANDMARKS[exerciseId] || []);
  context.lineCap = "round";
  context.lineJoin = "round";
  for (const [from, to] of POSE_CONNECTIONS) {
    const a = landmarks[from];
    const b = landmarks[to];
    if (!visible(a) || !visible(b)) continue;
    context.beginPath();
    context.moveTo(a.x * canvas.width, a.y * canvas.height);
    context.lineTo(b.x * canvas.width, b.y * canvas.height);
    context.lineWidth = highlighted.has(from) && highlighted.has(to) ? 5 : 3;
    context.strokeStyle = highlighted.has(from) && highlighted.has(to) ? "#22d3ee" : "rgba(255,255,255,0.78)";
    context.stroke();
  }
  landmarks.forEach((point, index) => {
    if (!visible(point) || index > 32) return;
    context.beginPath();
    context.arc(point.x * canvas.width, point.y * canvas.height, highlighted.has(index) ? 5 : 3, 0, Math.PI * 2);
    context.fillStyle = highlighted.has(index) ? "#fbbf24" : "#ffffff";
    context.fill();
  });
}

export default function RealtimeCoachingSpike({ onConfirmSuggestion }) {
  const { t } = useLocale();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const landmarkExtractorRef = useRef(null);
  const samplingRef = useRef(false);
  const coachingConnectionRef = useRef(null);
  const startedAtRef = useRef(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [samples, setSamples] = useState([]);
  const [landmarkSummary, setLandmarkSummary] = useState({ enabled: false, landmarkCount: 0, averageConfidence: null });
  const [landmarkStatus, setLandmarkStatus] = useState("idle");
  const [recognition, setRecognition] = useState({ status: "checking", models: [] });
  const [readiness, setReadiness] = useState({ status: "checking", capabilities: {} });
  const [exerciseId, setExerciseId] = useState("bicep_curl");
  const [coaching, setCoaching] = useState({ status: "idle", reps: 0, phase: "—", grip: "—", jointAngle: null, sessionId: null, lastRep: null });

  useEffect(() => {
    let cancelled = false;
    getRecognitionModels()
      .then((result) => { if (!cancelled) setRecognition(result); })
      .catch(() => { if (!cancelled) setRecognition({ status: "not_available", models: [] }); });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    getCoachingReadiness()
      .then((result) => { if (!cancelled) setReadiness(result); })
      .catch(() => { if (!cancelled) setReadiness({ status: "not_available", capabilities: {} }); });
    return () => { cancelled = true; };
  }, []);

  function handleCoachingMessage(message) {
    if (message.type === "session_started") {
      setCoaching((current) => ({ ...current, status: "active", sessionId: message.session_id }));
    } else if (message.type === "frame_feedback") {
      setCoaching((current) => ({ ...current, reps: message.reps, phase: message.phase, grip: message.grip, jointAngle: message.joint_angle }));
    } else if (message.type === "rep_event") {
      setCoaching((current) => ({ ...current, reps: message.rep_number, grip: message.grip, lastRep: message }));
    } else if (message.type === "session_summary") {
      setCoaching((current) => ({ ...current, status: "saved", reps: message.total_reps }));
    } else if (message.type === "error") {
      setCoaching((current) => ({ ...current, status: message.code === "AUTH_REQUIRED" || message.code === "INVALID_TOKEN" ? "auth_required" : "error" }));
    }
  }

  function startCoachingConnection() {
    try {
      coachingConnectionRef.current = connectRealtimeCoaching(exerciseId, {
        onMessage: handleCoachingMessage,
        onError: () => setCoaching((current) => ({ ...current, status: "error" })),
      });
      setCoaching({ status: "connecting", reps: 0, phase: "—", grip: "—", jointAngle: null, sessionId: null, lastRep: null });
    } catch {
      setCoaching((current) => ({ ...current, status: "auth_required" }));
    }
  }

  function stopCamera() {
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    if (overlayRef.current) overlayRef.current.width = overlayRef.current.width;
    coachingConnectionRef.current?.stop();
    coachingConnectionRef.current = null;
    setStatus((current) => (current === "active" || current === "requesting" ? "stopped" : current));
  }

  useEffect(() => stopCamera, []);

  async function sampleCurrentFrame() {
    if (samplingRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) return;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frameSummary = summarizeFrame(canvas);
    if (frameSummary) {
      const elapsedMs = startedAtRef.current ? Math.round(performance.now() - startedAtRef.current) : 0;
      setSamples((current) => [...current.slice(-(MAX_SAMPLES - 1)), { ...frameSummary, elapsedMs }]);
    }
    samplingRef.current = true;
    try {
      const summary = await readOptionalLandmarkSummary(video, landmarkExtractorRef.current);
      setLandmarkSummary(summary);
      const overlay = overlayRef.current;
      if (overlay && video.videoWidth && video.videoHeight) {
        if (overlay.width !== video.videoWidth) overlay.width = video.videoWidth;
        if (overlay.height !== video.videoHeight) overlay.height = video.videoHeight;
        drawPoseOverlay(overlay, summary.landmarks, exerciseId);
      }
      coachingConnectionRef.current?.sendLandmarks({
        timestamp_ms: performance.now(),
        pose_landmarks: summary.landmarks,
        hands: summary.hands,
      });
    } catch {
      setLandmarkStatus("error");
      setLandmarkSummary({ enabled: false, landmarkCount: 0, averageConfidence: null });
    } finally {
      samplingRef.current = false;
    }
  }

  async function ensureLandmarkExtractor() {
    if (landmarkExtractorRef.current) return true;
    setLandmarkStatus("loading");
    try {
      landmarkExtractorRef.current = window.physioVisionLandmarkExtractor || await getLocalPoseLandmarkExtractor();
      setLandmarkStatus("ready");
      return true;
    } catch {
      setLandmarkStatus("error");
      return false;
    }
  }

  async function startCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setError(t("coach.unsupported"));
      setStatus("idle");
      return;
    }
    setError("");
    setStatus("requesting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      startedAtRef.current = performance.now();
      setStatus("active");
      await ensureLandmarkExtractor();
      if (streamRef.current !== stream) return;
      startCoachingConnection();
      timerRef.current = window.setInterval(sampleCurrentFrame, SAMPLE_INTERVAL_MS);
      await sampleCurrentFrame();
    } catch (cameraError) {
      stopCamera();
      setError(t(cameraErrorMessageKey(cameraError)));
      setStatus("idle");
    }
  }

  const latest = samples.at(-1);
  const selectedExercise = {
    label: t(`coach.exercise.${exerciseId}`),
    view: t(`coach.exercise.${exerciseId}.view`),
    setup: t(`coach.exercise.${exerciseId}.setup`),
    motion: t(`coach.exercise.${exerciseId}.motion`),
    note: t(`coach.exercise.${exerciseId}.note`),
  };
  const gripExercise = exerciseId === "bicep_curl" || exerciseId === "hammer_curl";
  const coachingCue = t(coachingCueKey(coaching.status, coaching.phase));
  const latency = samples.length ? Math.round(samples.reduce((sum, item) => sum + item.elapsedMs, 0) / samples.length) : null;
  const capabilityReady = readiness.status === "ready" && Object.values(readiness.capabilities || {}).every(Boolean);
  const readinessSteps = [
    [t("coach.stepData"), Boolean(readiness.capabilities?.pose_data_pipeline)],
    [t("coach.stepRecognition"), Boolean(readiness.capabilities?.recognition_models)],
    [t("coach.stepAnalyzersComplete"), Boolean(readiness.capabilities?.hand_orientation_evidence)],
    [t("coach.stepRealtimeComplete"), Boolean(readiness.capabilities?.authenticated_streaming && readiness.capabilities?.rep_events && readiness.capabilities?.metadata_persistence)],
  ];

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <PageHeader
        eyebrow={t("coach.eyebrow")}
        title={t("coach.title")}
        description={t("coach.description")}
      />
      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <Card className="overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5">
            <div>
              <p className="text-sm font-bold text-clinical-ink">{t("coach.cameraTitle")}</p>
              <p className="mt-1 text-xs leading-5 text-slate-500">{t("coach.cameraHelp")}</p>
            </div>
            <Badge tone={status === "active" ? "teal" : status === "requesting" ? "amber" : "slate"}>
              {t(`coach.status.${status}`)}
            </Badge>
          </div>
          <div className="bg-slate-950 p-4">
            <div className="relative aspect-video w-full overflow-hidden rounded-2xl bg-slate-900">
            <video
              ref={videoRef}
              muted
              playsInline
              className="absolute inset-0 h-full w-full scale-x-[-1] object-cover"
              aria-label={t("coach.videoLabel")}
            />
            <canvas ref={overlayRef} className="pointer-events-none absolute inset-0 h-full w-full scale-x-[-1]" aria-label={t("coach.overlayLabel")} />
            <div className="absolute left-3 top-3 flex items-center gap-2 rounded-md bg-slate-950/80 px-2.5 py-1.5 text-xs font-semibold text-white">
              <span className={`h-2 w-2 rounded-full ${status === "active" ? "bg-emerald-400" : "bg-slate-500"}`} />
              {status === "active" ? t("coach.overlayActive") : t("coach.overlayWaiting")}
            </div>
            </div>
            <canvas ref={canvasRef} width={SAMPLE_WIDTH} height={SAMPLE_HEIGHT} className="hidden" aria-hidden="true" />
          </div>
          <div className="flex flex-wrap gap-3 p-5">
            <label className="min-w-44 text-xs font-semibold text-slate-600">
              {t("coach.exerciseMode")}
              <select value={exerciseId} onChange={(event) => setExerciseId(event.target.value)} disabled={status === "active" || status === "requesting"} className="mt-1 block h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-clinical-ink">
                {EXERCISES.map((id) => <option key={id} value={id}>{t(`coach.exercise.${id}`)}</option>)}
              </select>
            </label>
            <Button type="button" onClick={startCamera} disabled={status === "requesting" || status === "active"}>
              <Camera size={16} aria-hidden="true" />
              {t("coach.start")}
            </Button>
            <Button type="button" variant="secondary" onClick={stopCamera} disabled={status !== "active" && status !== "requesting"}>
              <Square size={16} aria-hidden="true" />
              {t("coach.stop")}
            </Button>
          </div>
          {error && <div className="px-5 pb-5"><Alert title={t("coach.errorTitle")}>{error}</Alert></div>}
          <div className="grid grid-cols-3 gap-3 border-t border-slate-100 p-5 text-sm">
            <div><p className="text-xs text-slate-500">{t("coach.liveReps")}</p><p className="mt-1 font-bold">{coaching.reps}</p></div>
            <div><p className="text-xs text-slate-500">{t("coach.livePhase")}</p><p className="mt-1 font-bold capitalize">{coaching.phase}</p></div>
            <div><p className="text-xs text-slate-500">{gripExercise ? t("coach.liveGrip") : t("coach.liveAngle")}</p><p className="mt-1 font-bold capitalize">{gripExercise ? coaching.grip.replace("_", " ") : coaching.jointAngle == null ? "—" : `${coaching.jointAngle}°`}</p></div>
          </div>
          <div className="mx-5 mb-5 rounded-2xl border border-blue-100 bg-blue-50/70 p-4" aria-live="polite">
            <p className="text-xs font-bold uppercase tracking-wider text-clinical-blue">{t("coach.liveCue")}</p>
            <p className="mt-1 text-sm font-semibold text-clinical-ink">{coachingCue}</p>
            {coaching.lastRep && (
              <p className="mt-2 text-xs text-slate-600">
                {t("coach.lastRepAnalysis", {
                  rep: coaching.lastRep.rep_number,
                  duration: coaching.lastRep.duration_sec,
                  range: Math.round(coaching.lastRep.maximum_angle - coaching.lastRep.minimum_angle),
                })}
              </p>
            )}
          </div>
          <div className="mx-5 mb-5 border-l-2 border-clinical-blue pl-4">
            <div className="flex items-center gap-2 text-sm font-bold text-clinical-ink"><Info size={16} aria-hidden="true" />{selectedExercise.label}</div>
            <dl className="mt-3 grid gap-x-6 gap-y-3 text-xs leading-5 sm:grid-cols-2">
              <div><dt className="font-semibold text-slate-700">{t("coach.cameraView")}</dt><dd className="text-slate-500">{selectedExercise.view}</dd></div>
              <div><dt className="font-semibold text-slate-700">{t("coach.setup")}</dt><dd className="text-slate-500">{selectedExercise.setup}</dd></div>
              <div><dt className="font-semibold text-slate-700">{t("coach.movement")}</dt><dd className="text-slate-500">{selectedExercise.motion}</dd></div>
              <div><dt className="font-semibold text-slate-700">{t("coach.note")}</dt><dd className="text-slate-500">{selectedExercise.note}</dd></div>
            </dl>
          </div>
          {coaching.status === "auth_required" && <div className="px-5 pb-5"><Alert tone="warning">{t("coach.loginRequired")}</Alert></div>}
          {coaching.status === "saved" && <div className="px-5 pb-5"><Alert tone="info">{t("coach.sessionSaved")}</Alert></div>}
        </Card>

        <div className="space-y-6">
          <Alert tone="info" title={t("coach.safetyTitle")}>
            {t("coach.safetyText")}
          </Alert>
          <Card className="p-5">
            <div className="flex items-center gap-2 text-sm font-bold text-clinical-ink">
              <ShieldCheck size={16} aria-hidden="true" />
              {t("coach.derivedTitle")}
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-2xl bg-slate-50 p-3">
                <dt className="text-xs text-slate-500">{t("coach.samples")}</dt>
                <dd className="mt-1 font-bold text-clinical-ink">{samples.length}</dd>
              </div>
              <div className="rounded-2xl bg-slate-50 p-3">
                <dt className="text-xs text-slate-500">{t("coach.brightness")}</dt>
                <dd className="mt-1 font-bold text-clinical-ink">{latest?.brightness ?? "—"}</dd>
              </div>
              <div className="rounded-2xl bg-slate-50 p-3">
                <dt className="text-xs text-slate-500">{t("coach.visibility")}</dt>
                <dd className="mt-1 font-bold text-clinical-ink">{latest ? `${latest.visibilityProxy}%` : "—"}</dd>
              </div>
              <div className="rounded-2xl bg-slate-50 p-3">
                <dt className="text-xs text-slate-500">{t("coach.latency")}</dt>
                <dd className="mt-1 font-bold text-clinical-ink">{latency == null ? "—" : `${latency} ms`}</dd>
              </div>
            </dl>
            <div className="mt-4 rounded-2xl border border-dashed border-slate-200 p-3 text-xs leading-5 text-slate-500">
              {landmarkSummary.enabled
                ? t("coach.landmarksEnabled", { count: landmarkSummary.landmarkCount, confidence: landmarkSummary.averageConfidence ?? "—" })
                : landmarkStatus === "loading"
                  ? t("coach.landmarksLoading")
                  : landmarkStatus === "error"
                    ? t("coach.landmarksError")
                    : t("coach.landmarksIdle")}
            </div>
          </Card>
          <Card className="p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-sm font-bold text-clinical-ink">
                <BrainCircuit size={17} aria-hidden="true" />
                {t("coach.modelTitle")}
              </div>
              <Badge tone={capabilityReady ? "teal" : recognition.models?.length ? "blue" : "slate"}>
                {capabilityReady ? t("coach.complete") : recognition.models?.length ? t("coach.modelAvailable") : t("coach.modelPending")}
              </Badge>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-500">{t("coach.modelDescription")}</p>
            <ol className="mt-4 space-y-3 text-xs text-slate-600">
              {readinessSteps.map(([step, complete]) => (
                <li key={step} className="flex items-start gap-2">
                  <CheckCircle2 className={`mt-0.5 shrink-0 ${complete ? "text-clinical-teal" : "text-slate-300"}`} size={15} aria-hidden="true" />
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </Card>
        </div>
        <RecognitionUploadCard models={recognition.models || []} onConfirmSuggestion={onConfirmSuggestion} />
      </div>
    </main>
  );
}
