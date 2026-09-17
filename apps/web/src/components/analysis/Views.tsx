"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { Activity, ArrowRight, UploadCloud } from "lucide-react";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "../care/Views";
import { api } from "../../lib/api";
import type { AnalysisResult, Exercise, Job } from "../../lib/types";

export function AnalyzeView({
  initialExercise = "",
  patientId,
  onCompleted,
}: {
  initialExercise?: string;
  patientId?: string;
  onCompleted?: (sessionId: string) => void;
} = {}) {
  const resource = useResource<Exercise[]>("exercises");
  const activeJobs = useResource<Job[]>(patientId ? null : "analysis-jobs");
  const { t, exerciseName } = usePreferences();
  const [exercise, setExercise] = useState(initialExercise);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const controller = useRef<AbortController | null>(null);
  const requestKey = useRef<string | null>(null);
  const restoredJob = useRef(false);
  useEffect(() => {
    if (!initialExercise)
      setExercise(
        new URLSearchParams(window.location.search).get("exercise") || "",
      );
    return () => controller.current?.abort();
  }, [initialExercise]);
  useEffect(() => {
    if (restoredJob.current || !activeJobs.data) return;
    restoredJob.current = true;
    const candidate = initialExercise
      ? activeJobs.data.find((row) => row.exercise_id === initialExercise)
      : activeJobs.data[0];
    if (candidate) setJob(candidate);
  }, [activeJobs.data, initialExercise]);
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const abort = new AbortController();
    const timeout = setTimeout(
      () =>
        api<Job>(`analysis-jobs/${encodeURIComponent(job.job_id)}`, {
          signal: abort.signal,
        })
          .then(setJob)
          .catch((e) => {
            if (!abort.signal.aborted) setError(e.message);
          }),
      1500,
    );
    return () => {
      clearTimeout(timeout);
      abort.abort();
    };
  }, [job]);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file || !exercise) return;
    if (file.size > 100 * 1024 * 1024) {
      setError(t("videoSizeLimit"));
      return;
    }
    if (
      !requestKey.current ||
      (job && ["failed", "cancelled"].includes(job.status))
    )
      requestKey.current = crypto.randomUUID();
    setBusy(true);
    setError("");
    const form = new FormData();
    form.set("video", file);
    controller.current = new AbortController();
    try {
      setJob(
        await api<Job>(
          `analysis-jobs/${encodeURIComponent(exercise)}?save_session=true${patientId ? `&patient_id=${encodeURIComponent(patientId)}` : ""}`,
          {
            method: "POST",
            body: form,
            signal: controller.current.signal,
            headers: { "Idempotency-Key": requestKey.current! },
          },
        ),
      );
    } catch (e) {
      if (!(e instanceof DOMException && e.name === "AbortError"))
        setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function cancel() {
    if (!job) {
      controller.current?.abort();
      return;
    }
    try {
      await api(`analysis-jobs/${encodeURIComponent(job.job_id)}/cancel`, {
        method: "POST",
      });
      setJob(await api<Job>(`analysis-jobs/${encodeURIComponent(job.job_id)}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  if (!resource.data)
    return <ResourceState {...resource} retry={resource.refresh} />;
  return (
    <div className="narrow">
      <section className="panel">
        <div className="hero-icon">
          <Activity size={28} />
        </div>
        <h2>{t("analyze")}</h2>
        <p className="muted">{t("analyzeHint")}</p>
        <form onSubmit={submit}>
          <label>
            {t("exercise")}
            <select
              required
              value={exercise}
              disabled={
                !!onCompleted ||
                busy ||
                (!!job && ["queued", "running"].includes(job.status))
              }
              onChange={(e) => {
                setExercise(e.target.value);
                requestKey.current = null;
                setJob(null);
              }}
            >
              <option value="">{t("selectExercise")}</option>
              {resource.data
                .filter((x) => x.supported_in_app && x.endpoint_path)
                .map((x) => {
                  const id = x.exercise_id || x.id || "";
                  return (
                    <option key={id} value={id}>
                      {exerciseName(id)}
                    </option>
                  );
                })}
            </select>
          </label>
          <label className="upload-zone">
            <UploadCloud size={32} />
            <strong>{t("video")}</strong>
            <input
              type="file"
              accept="video/*"
              required={!file}
              disabled={
                busy || (!!job && ["queued", "running"].includes(job.status))
              }
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setJob(null);
                requestKey.current = null;
                setError("");
              }}
            />
          </label>
          {preview && (
            <video
              controls
              playsInline
              src={preview}
              className="video-preview"
            />
          )}
          {!job || ["failed", "cancelled"].includes(job.status) ? (
            <button className="primary" disabled={busy || !file || !exercise}>
              {busy ? t("loading") : t("upload")}
              <ArrowRight size={18} />
            </button>
          ) : null}
        </form>
        {(busy || (job && ["queued", "running"].includes(job.status))) && (
          <div className="job-state">
            <p role="status">{job ? t("loading") : t("upload")}</p>
            {job && <progress max={100} value={job.progress} />}
            <button className="secondary" onClick={cancel}>
              {t("cancel")}
            </button>
          </div>
        )}
        {job?.status === "completed" && job.result && (
          <>
            <ResultSummary result={job.result} />
            {onCompleted &&
              job.result.status === "success" &&
              job.result.session_id && (
                <button
                  className="primary"
                  onClick={() => onCompleted(job.result!.session_id!)}
                >
                  {t("next")}
                </button>
              )}
          </>
        )}{" "}
        {job?.status === "failed" && (
          <p role="alert" className="error">
            {job.message || t("unavailable")}
          </p>
        )}
        {job?.status === "cancelled" && <p role="status">{t("cancelled")}</p>}
        {error && (
          <div role="alert" className="error">
            <p>{error}</p>
            {job && (
              <button
                className="secondary"
                onClick={() =>
                  api<Job>(`analysis-jobs/${encodeURIComponent(job.job_id)}`)
                    .then(setJob)
                    .then(() => setError(""))
                    .catch((e) => setError(e.message))
                }
              >
                {t("retry")}
              </button>
            )}
          </div>
        )}
      </section>
      <p className="fine-print">{t("analysisDisclaimer")}</p>
    </div>
  );
}
export function ResultView({ id }: { id: string }) {
  const resource = useResource<AnalysisResult>(
    id ? `sessions/${encodeURIComponent(id)}` : null,
  );
  const { t } = usePreferences();
  if (!resource.data)
    return <ResourceState {...resource} retry={resource.refresh} />;
  const result = (resource.data.result ||
    resource.data.report ||
    resource.data) as AnalysisResult;
  return (
    <section className="panel narrow">
      <ResultSummary result={result} />
      <Link href="/workspace/progress" className="text-link">
        {t("back")}
      </Link>
    </section>
  );
}
function ResultSummary({ result }: { result: AnalysisResult }) {
  const { t } = usePreferences();
  const valid = result.status === "success";
  return (
    <section className="result-summary">
      <h2>{t("results")}</h2>
      {!valid && (
        <p className="notice">
          {result.message ||
            t(result.status === "error" ? "analysisError" : "rejected")}
        </p>
      )}
      {valid && (
        <div className="metrics">
          <div>
            <small>{t("reps")}</small>
            <strong>{result.total_reps ?? t("unavailable")}</strong>
          </div>
          <div>
            <small>{t("score")}</small>
            <strong>{result.movement_score ?? t("unavailable")}</strong>
          </div>
        </div>
      )}
      <p>
        {t("confidence")}:{" "}
        {result.analysis_confidence_level ??
          result.analysis_confidence?.level ??
          t("unavailable")}
      </p>
      {result.feedback?.length ? (
        <ul>
          {result.feedback.map((text, i) => (
            <li key={i}>{text}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">{t("noFeedback")}</p>
      )}
      <p className="fine-print">{t("analysisDisclaimer")}</p>
    </section>
  );
}
