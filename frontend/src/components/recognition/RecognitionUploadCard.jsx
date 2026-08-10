import { useState } from "react";
import { BrainCircuit, CheckCircle2, FileVideo2, UploadCloud } from "lucide-react";

import { Alert, Badge, Button, Card, LoadingSpinner } from "../common/UI.jsx";
import { EXERCISES, exerciseById } from "../../data/exercises.js";
import { useLocale } from "../../i18n/LocaleContext.jsx";
import { confirmRecognitionSuggestion, recognizeExerciseVideo } from "../../services/api.js";


function confidencePercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}


export default function RecognitionUploadCard({ models = [], onConfirmSuggestion }) {
  const { t, exerciseText } = useLocale();
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmationError, setConfirmationError] = useState("");
  const sequenceModel = models.find((model) => model.artifact_format === "torchscript_sequence");
  const suggested = result ? exerciseById(result.suggested_exercise_id, EXERCISES) : null;
  const isUncertain = result?.status === "uncertain";

  function selectFile(event) {
    setFile(event.target.files?.[0] || null);
    setResult(null);
    setError("");
    setProgress(0);
    setConfirmationError("");
  }

  async function confirmSuggestion() {
    if (!suggested?.supported_in_app || isUncertain) return;
    setConfirmationError("");
    setIsConfirming(true);
    try {
      if (result.recognition_event_id) {
        await confirmRecognitionSuggestion(result.recognition_event_id, suggested.exercise_id);
      }
      onConfirmSuggestion?.(suggested.exercise_id, file);
    } catch {
      setConfirmationError(t("coach.confirmationAuditError"));
    } finally {
      setIsConfirming(false);
    }
  }

  async function identifyExercise() {
    if (!file || !sequenceModel) return;
    setIsLoading(true);
    setError("");
    setResult(null);
    setProgress(0);
    try {
      setResult(await recognizeExerciseVideo(file, setProgress));
    } catch (requestError) {
      setError(
        requestError.response?.data?.error_code === "SUBJECT_SWITCH_DETECTED"
          ? t("upload.subjectSwitch")
          : requestError.response?.data?.message || t("coach.recognitionError"),
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card className="overflow-hidden lg:col-span-2" aria-labelledby="recognition-upload-title">
      <div className="border-b border-slate-100 bg-gradient-to-r from-white via-blue-50/40 to-teal-50/40 p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-blue-50 text-clinical-blue">
              <BrainCircuit size={22} aria-hidden="true" />
            </span>
            <div>
              <h2 id="recognition-upload-title" className="text-lg font-bold text-clinical-ink">{t("coach.recognitionTitle")}</h2>
              <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-500">{t("coach.recognitionDescription")}</p>
            </div>
          </div>
          <Badge tone={sequenceModel ? "teal" : "slate"}>
            {sequenceModel ? t("coach.candidateReady") : t("coach.modelPending")}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 p-5 sm:p-6 lg:grid-cols-[0.85fr_1.15fr]">
        <div>
          <label className={`flex min-h-48 flex-col items-center justify-center rounded-2xl border-2 border-dashed px-5 text-center transition ${file ? "border-teal-200 bg-teal-50/50" : "border-slate-200 bg-slate-50/70 hover:border-blue-300 hover:bg-blue-50/40"}`}>
            <span className={`grid h-14 w-14 place-items-center rounded-2xl ${file ? "bg-teal-100 text-clinical-teal" : "bg-white text-clinical-blue shadow-soft ring-1 ring-slate-100"}`}>
              {file ? <CheckCircle2 size={25} aria-hidden="true" /> : <FileVideo2 size={25} aria-hidden="true" />}
            </span>
            <span className="mt-4 text-sm font-bold text-slate-800">{file ? file.name : t("coach.recognitionChoose")}</span>
            <span className="mt-1 text-xs text-slate-500">{file ? t("coach.recognitionSelected", { size: (file.size / 1024 / 1024).toFixed(1) }) : t("coach.recognitionFormats")}</span>
            <input
              className="sr-only"
              type="file"
              accept=".mp4,.mov,.avi,.mkv,.webm"
              aria-label={t("coach.recognitionChoose")}
              onChange={selectFile}
              disabled={isLoading || !sequenceModel}
            />
          </label>
          <div className="mt-4 flex items-center justify-between gap-3">
            <p className="text-xs leading-5 text-slate-500">{t("coach.recognitionTemporary")}</p>
            <Button type="button" onClick={identifyExercise} disabled={!file || !sequenceModel || isLoading}>
              {isLoading ? <LoadingSpinner label={t("coach.recognitionProcessing")} /> : <><UploadCloud size={17} aria-hidden="true" />{t("coach.recognitionAction")}</>}
            </Button>
          </div>
          {isLoading ? <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-clinical-blue transition-all" style={{ width: `${Math.max(progress, 8)}%` }} /></div> : null}
          {error ? <Alert className="mt-4" title={t("coach.recognitionErrorTitle")}>{error}</Alert> : null}
        </div>

        <div className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4 sm:p-5" aria-live="polite">
          {!result ? (
            <div className="flex min-h-48 flex-col items-center justify-center text-center">
              <BrainCircuit className="text-slate-300" size={30} aria-hidden="true" />
              <p className="mt-3 text-sm font-bold text-slate-700">{t("coach.recognitionEmptyTitle")}</p>
              <p className="mt-1 max-w-sm text-xs leading-5 text-slate-500">{t("coach.recognitionEmptyText")}</p>
            </div>
          ) : (
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-clinical-blue">{t("coach.recognitionSuggestion")}</p>
              <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xl font-bold text-clinical-ink">{exerciseText(result.suggested_exercise_id).name}</p>
                  <p className="mt-1 text-xs text-slate-500">{t("coach.recognitionConfidence", { confidence: confidencePercent(result.confidence) })}</p>
                </div>
                <Badge tone={suggested?.supported_in_app && !isUncertain ? "teal" : "amber"}>
                  {isUncertain ? t("coach.uncertainBadge") : suggested?.supported_in_app ? t("status.supported") : t("status.notAvailable")}
                </Badge>
              </div>
              <div className="mt-5 space-y-3">
                {(result.top_predictions || []).map((prediction) => (
                  <div key={prediction.exercise_id}>
                    <div className="flex justify-between gap-3 text-xs font-semibold text-slate-700">
                      <span>{exerciseText(prediction.exercise_id).name}</span>
                      <span>{confidencePercent(prediction.confidence)}</span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full rounded-full bg-clinical-blue" style={{ width: confidencePercent(prediction.confidence) }} />
                    </div>
                  </div>
                ))}
              </div>
              {isUncertain ? (
                <Alert tone="warning" className="mt-5" title={t("coach.uncertainTitle")}>
                  {t("coach.uncertainText", { threshold: confidencePercent(result.confidence_threshold) })}
                </Alert>
              ) : suggested?.supported_in_app ? (
                <Button className="mt-5 w-full" type="button" onClick={confirmSuggestion} disabled={isConfirming}>
                  <CheckCircle2 size={17} aria-hidden="true" />{isConfirming ? t("coach.confirmingSuggestion") : t("coach.confirmSuggestion", { exercise: exerciseText(suggested.exercise_id).short })}
                </Button>
              ) : (
                <Alert tone="warning" className="mt-5" title={t("coach.noAnalyzerTitle")}>{t("coach.noAnalyzerText")}</Alert>
              )}
              {confirmationError ? <Alert className="mt-3" title={t("coach.confirmationAuditTitle")}>{confirmationError}</Alert> : null}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
