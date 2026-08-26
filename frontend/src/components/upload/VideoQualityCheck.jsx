import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, LoaderCircle, ScanSearch, ShieldCheck, XCircle } from "lucide-react";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const SAMPLE_WIDTH = 160;
const SAMPLE_HEIGHT = 90;

export function evaluateVideoMetadata({ duration, width, height }) {
  const shortestSide = Math.min(width || 0, height || 0);
  const aspectRatio = width && height ? width / height : 0;
  return [
    {
      code: "duration",
      status: duration < 2 ? "fail" : duration > 180 ? "warn" : "pass",
      value: Number.isFinite(duration) ? `${duration.toFixed(1)}s` : "—",
    },
    {
      code: "resolution",
      status: shortestSide < 360 ? "fail" : shortestSide < 480 ? "warn" : "pass",
      value: width && height ? `${width}×${height}` : "—",
    },
    {
      code: "framing",
      status: aspectRatio >= 0.5 && aspectRatio <= 2 ? "pass" : "warn",
      value: aspectRatio ? aspectRatio.toFixed(2) : "—",
    },
  ];
}

export function evaluateFrameSamples({ brightnessValues, motionValues }) {
  const brightness = brightnessValues.length
    ? brightnessValues.reduce((sum, value) => sum + value, 0) / brightnessValues.length
    : null;
  const motion = motionValues.length
    ? motionValues.reduce((sum, value) => sum + value, 0) / motionValues.length
    : null;
  return [
    {
      code: "lighting",
      status: brightness == null ? "unavailable" : brightness < 45 || brightness > 220 ? "warn" : "pass",
      value: brightness == null ? "—" : Math.round(brightness),
    },
    {
      code: "motion",
      status: motion == null ? "unavailable" : motion < 4 ? "warn" : "pass",
      value: motion == null ? "—" : motion.toFixed(1),
    },
  ];
}

function waitForMediaEvent(target, eventName, timeoutMs = 6000) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => finish(reject, new Error(`Timed out waiting for ${eventName}`)), timeoutMs);
    const onReady = () => finish(resolve);
    const onError = () => finish(reject, new Error("Video could not be decoded"));
    function finish(callback, value) {
      clearTimeout(timeout);
      target.removeEventListener(eventName, onReady);
      target.removeEventListener("error", onError);
      callback(value);
    }
    target.addEventListener(eventName, onReady, { once: true });
    target.addEventListener("error", onError, { once: true });
  });
}

function frameBrightness(pixels) {
  let total = 0;
  for (let index = 0; index < pixels.length; index += 4) {
    total += pixels[index] * 0.2126 + pixels[index + 1] * 0.7152 + pixels[index + 2] * 0.0722;
  }
  return total / (pixels.length / 4);
}

function frameDifference(previous, current) {
  if (!previous || previous.length !== current.length) return null;
  let total = 0;
  for (let index = 0; index < current.length; index += 4) {
    total += Math.abs(current[index] - previous[index]);
    total += Math.abs(current[index + 1] - previous[index + 1]);
    total += Math.abs(current[index + 2] - previous[index + 2]);
  }
  return total / ((current.length / 4) * 3);
}

export async function inspectVideo(file) {
  if (typeof document === "undefined" || typeof URL === "undefined" || typeof URL.createObjectURL !== "function") {
    throw new Error("Local video inspection is unavailable");
  }
  const video = document.createElement("video");
  const objectUrl = URL.createObjectURL(file);
  video.preload = "metadata";
  video.muted = true;
  video.playsInline = true;
  try {
    const metadataReady = waitForMediaEvent(video, "loadedmetadata");
    video.src = objectUrl;
    await metadataReady;
    const metadataChecks = evaluateVideoMetadata({
      duration: video.duration,
      width: video.videoWidth,
      height: video.videoHeight,
    });
    const canvas = document.createElement("canvas");
    canvas.width = SAMPLE_WIDTH;
    canvas.height = SAMPLE_HEIGHT;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context || !Number.isFinite(video.duration) || video.duration <= 0) {
      return { checks: [...metadataChecks, ...evaluateFrameSamples({ brightnessValues: [], motionValues: [] })] };
    }
    const brightnessValues = [];
    const motionValues = [];
    let previousFrame = null;
    for (const fraction of [0.2, 0.5, 0.8]) {
      const targetTime = Math.min(Math.max(video.duration * fraction, 0.05), Math.max(0.05, video.duration - 0.05));
      const seeked = waitForMediaEvent(video, "seeked");
      video.currentTime = targetTime;
      await seeked;
      context.drawImage(video, 0, 0, SAMPLE_WIDTH, SAMPLE_HEIGHT);
      const pixels = context.getImageData(0, 0, SAMPLE_WIDTH, SAMPLE_HEIGHT).data;
      brightnessValues.push(frameBrightness(pixels));
      const difference = frameDifference(previousFrame, pixels);
      if (difference != null) motionValues.push(difference);
      previousFrame = new Uint8ClampedArray(pixels);
    }
    return { checks: [...metadataChecks, ...evaluateFrameSamples({ brightnessValues, motionValues })] };
  } finally {
    video.removeAttribute("src");
    video.load?.();
    URL.revokeObjectURL(objectUrl);
  }
}

function CheckIcon({ status }) {
  if (status === "pass") return <CheckCircle2 size={17} className="text-clinical-teal" aria-hidden="true" />;
  if (status === "fail") return <XCircle size={17} className="text-red-600" aria-hidden="true" />;
  return <AlertTriangle size={17} className="text-amber-600" aria-hidden="true" />;
}

export default function VideoQualityCheck({ file, onBlockingChange, inspect = inspectVideo }) {
  const { t } = useLocale();
  const [state, setState] = useState({ status: "idle", checks: [] });

  useEffect(() => {
    let cancelled = false;
    if (!file) {
      setState({ status: "idle", checks: [] });
      onBlockingChange?.(false);
      return () => { cancelled = true; };
    }
    setState({ status: "checking", checks: [] });
    onBlockingChange?.(false);
    inspect(file)
      .then(({ checks }) => {
        if (cancelled) return;
        const blocked = checks.some((check) => check.status === "fail");
        setState({ status: blocked ? "fail" : checks.some((check) => check.status === "warn") ? "warn" : "pass", checks });
        onBlockingChange?.(blocked);
      })
      .catch(() => {
        if (cancelled) return;
        setState({ status: "unavailable", checks: [] });
        onBlockingChange?.(false);
      });
    return () => { cancelled = true; };
  }, [file, inspect, onBlockingChange]);

  if (!file) return null;
  if (state.status === "checking") return <div role="status" className="mt-4 flex items-center gap-3 rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900"><LoaderCircle size={18} className="animate-spin" /><span><strong>{t("upload.qualityChecking")}</strong><span className="ms-2 text-xs text-blue-700">{t("upload.qualityLocal")}</span></span></div>;
  if (state.status === "unavailable") return <div className="mt-4 flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"><ScanSearch size={18} className="mt-0.5 shrink-0 text-slate-500" /><div><p className="text-sm font-semibold text-clinical-ink">{t("upload.qualityUnavailable")}</p><p className="mt-1 text-xs text-slate-500">{t("upload.qualityUnavailableHelp")}</p></div></div>;

  return <section aria-label={t("upload.qualityTitle")} className="mt-4 rounded-xl border border-clinical-line bg-slate-50/70 p-4">
    <div className="flex flex-wrap items-start justify-between gap-3"><div className="flex items-start gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-white text-clinical-blue ring-1 ring-clinical-line"><ShieldCheck size={18} /></span><div><h3 className="text-sm font-bold text-clinical-ink">{t(`upload.quality.${state.status}`)}</h3><p className="mt-1 text-xs text-slate-500">{t("upload.qualityLocal")}</p></div></div><span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${state.status === "pass" ? "bg-teal-50 text-teal-700" : state.status === "fail" ? "bg-red-50 text-red-700" : "bg-amber-50 text-amber-800"}`}>{t(`upload.qualityBadge.${state.status}`)}</span></div>
    <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">{state.checks.map((check) => <div key={check.code} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2.5 ring-1 ring-clinical-line"><CheckIcon status={check.status} /><div className="min-w-0"><p className="truncate text-[11px] font-semibold text-slate-700">{t(`upload.qualityCheck.${check.code}`)}</p><p className="mt-0.5 text-[10px] text-slate-500">{check.value}</p></div></div>)}</div>
    {state.status === "fail" ? <p className="mt-3 text-xs font-semibold text-red-700">{t("upload.qualityBlockingHelp")}</p> : state.status === "warn" ? <p className="mt-3 text-xs text-amber-800">{t("upload.qualityWarningHelp")}</p> : null}
  </section>;
}
