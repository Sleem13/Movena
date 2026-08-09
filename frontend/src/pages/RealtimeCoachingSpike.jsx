import { useEffect, useRef, useState } from "react";
import { BrainCircuit, Camera, CheckCircle2, ShieldCheck, Square } from "lucide-react";

import { Card, Alert, Button, Badge } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import RecognitionUploadCard from "../components/recognition/RecognitionUploadCard.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { getRecognitionModels } from "../services/api.js";

const SAMPLE_INTERVAL_MS = 500;
const SAMPLE_WIDTH = 160;
const SAMPLE_HEIGHT = 90;
const MAX_SAMPLES = 20;

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

export async function readOptionalLandmarkSummary(videoElement) {
  const extractor = window.physioVisionLandmarkExtractor;
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
  };
}

export default function RealtimeCoachingSpike({ onConfirmSuggestion }) {
  const { t } = useLocale();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const startedAtRef = useRef(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [samples, setSamples] = useState([]);
  const [landmarkSummary, setLandmarkSummary] = useState({ enabled: false, landmarkCount: 0, averageConfidence: null });
  const [recognition, setRecognition] = useState({ status: "checking", models: [] });

  useEffect(() => {
    let cancelled = false;
    getRecognitionModels()
      .then((result) => { if (!cancelled) setRecognition(result); })
      .catch(() => { if (!cancelled) setRecognition({ status: "not_available", models: [] }); });
    return () => { cancelled = true; };
  }, []);

  function stopCamera() {
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setStatus((current) => (current === "active" || current === "requesting" ? "stopped" : current));
  }

  useEffect(() => stopCamera, []);

  async function sampleCurrentFrame() {
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
    try {
      setLandmarkSummary(await readOptionalLandmarkSummary(video));
    } catch {
      setLandmarkSummary({ enabled: false, landmarkCount: 0, averageConfidence: null });
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
      timerRef.current = window.setInterval(sampleCurrentFrame, SAMPLE_INTERVAL_MS);
      await sampleCurrentFrame();
    } catch (cameraError) {
      stopCamera();
      setError(t(cameraErrorMessageKey(cameraError)));
      setStatus("idle");
    }
  }

  const latest = samples.at(-1);
  const latency = samples.length ? Math.round(samples.reduce((sum, item) => sum + item.elapsedMs, 0) / samples.length) : null;

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
            <video
              ref={videoRef}
              muted
              playsInline
              className="aspect-video w-full rounded-2xl bg-slate-900 object-cover"
              aria-label={t("coach.videoLabel")}
            />
            <canvas ref={canvasRef} width={SAMPLE_WIDTH} height={SAMPLE_HEIGHT} className="hidden" aria-hidden="true" />
          </div>
          <div className="flex flex-wrap gap-3 p-5">
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
                : t("coach.landmarksDisabled")}
            </div>
          </Card>
          <Card className="p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-sm font-bold text-clinical-ink">
                <BrainCircuit size={17} aria-hidden="true" />
                {t("coach.modelTitle")}
              </div>
              <Badge tone={recognition.models?.length ? "blue" : "slate"}>
                {recognition.models?.length ? t("coach.modelAvailable") : t("coach.modelPending")}
              </Badge>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-500">{t("coach.modelDescription")}</p>
            <ol className="mt-4 space-y-3 text-xs text-slate-600">
              {[t("coach.stepData"), t("coach.stepRecognition"), t("coach.stepAnalyzers"), t("coach.stepRealtime")].map((step, index) => (
                <li key={step} className="flex items-start gap-2">
                  <CheckCircle2 className={index < 2 ? "mt-0.5 shrink-0 text-clinical-teal" : index === 2 ? "mt-0.5 shrink-0 text-clinical-blue" : "mt-0.5 shrink-0 text-slate-300"} size={15} aria-hidden="true" />
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
