import { useState } from "react";
import { Check, FileVideo2, UploadCloud, X } from "lucide-react";
import { Alert, Button, Card, LoadingSpinner } from "../common/UI.jsx";
import UploadProgress from "./UploadProgress.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

export default function UploadCard({
  exercise = "bodyweight_squat",
  file,
  fileSource,
  error,
  canContinueAfterWarning = false,
  isLoading,
  progress,
  onFileChange,
  onFileSelect,
  onSubmit,
}) {
  const { locale, t, exerciseText } = useLocale();
  const [dragging, setDragging] = useState(false);
  const names = exerciseText(exercise);
  const uploadName = exercise === "bodyweight_squat" && locale === "en" ? "Squat" : names.short;

  function drop(event) {
    event.preventDefault();
    setDragging(false);
    const selected = event.dataTransfer.files?.[0];
    if (selected) onFileSelect(selected);
  }

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-slate-100 bg-gradient-to-r from-white to-blue-50/50 p-5 sm:p-6">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-blue-50 text-clinical-blue">
            <FileVideo2 size={22} aria-hidden="true" />
          </span>
          <div>
            <h2 className="text-lg font-bold text-clinical-ink">
              {t("upload.cardTitle", { exercise: uploadName })}
            </h2>
            <p className="text-xs text-slate-500">{t("upload.fileTypes")}</p>
          </div>
        </div>
      </div>
      <div className="p-5 sm:p-6">
        {file && fileSource === "recognition" ? (
          <div role="status" className="mb-4 flex items-start gap-3 rounded-2xl border border-teal-200 bg-teal-50 p-4 text-teal-950">
            <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full bg-teal-100 text-clinical-teal">
              <Check size={17} aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-bold">{t("upload.recognitionReadyTitle")}</p>
              <p className="mt-1 text-xs leading-5 text-teal-800">{t("upload.recognitionReadyText", { exercise: names.short })}</p>
            </div>
          </div>
        ) : null}
        <label
          onDragEnter={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={() => setDragging(false)}
          onDrop={drop}
          className={`flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 text-center transition duration-200 ${
            dragging
              ? "scale-[1.01] border-clinical-blue bg-blue-50"
              : file
                ? "border-teal-200 bg-teal-50/50"
                : "border-slate-200 bg-slate-50/70 hover:border-blue-300 hover:bg-blue-50/40"
          }`}
        >
          <span className={`grid h-16 w-16 place-items-center rounded-2xl transition ${file ? "bg-teal-100 text-clinical-teal" : "bg-white text-clinical-blue shadow-soft ring-1 ring-slate-100"}`}>
            {file ? <Check size={27} aria-hidden="true" /> : <UploadCloud size={27} aria-hidden="true" />}
          </span>
          <span className="mt-4 text-sm font-bold text-slate-800">
            {file ? file.name : t("upload.drag", { exercise: names.short })}
          </span>
          <span className="mt-1 text-xs text-slate-500">
            {file ? t("upload.selected", { size: (file.size / 1024 / 1024).toFixed(1) }) : t("upload.browse")}
          </span>
          <input
            className="sr-only"
            aria-label={t("upload.chooseVideo", { exercise: names.short })}
            type="file"
            accept=".mp4,.mov,.avi,.mkv,.webm"
            onChange={onFileChange}
            disabled={isLoading}
          />
        </label>
        {error && (
          <div className="mt-4">
            <Alert title={canContinueAfterWarning ? t("upload.warningTitle") : t("upload.errorTitle")}>
              <div className="space-y-3">
                <p>{error}</p>
                {canContinueAfterWarning ? (
                  <div>
                    <p className="text-sm leading-6">{t("upload.subjectSwitchOverrideHelp")}</p>
                    <p className="mt-2 text-sm font-semibold">{t("upload.subjectSwitchAutoProceed")}</p>
                  </div>
                ) : null}
              </div>
            </Alert>
          </div>
        )}
        <UploadProgress progress={progress} isLoading={isLoading} />
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
          <p className="flex max-w-sm items-center gap-2 text-xs leading-5 text-slate-500">
            <X size={14} className="shrink-0" aria-hidden="true" />
            {t("upload.temporary")}
          </p>
          <Button type="submit" onClick={onSubmit} disabled={!file || isLoading}>
            {isLoading ? (
              <LoadingSpinner label={t("common.analyzing")} />
            ) : (
              <>
                <UploadCloud size={17} aria-hidden="true" />
                {t("upload.analyze", { exercise: names.short })}
              </>
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
}
