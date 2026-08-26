import { useLocale } from "../../i18n/LocaleContext.jsx";

export default function UploadProgress({ progress = 0, isLoading }) {
  const { t } = useLocale();
  if (!isLoading) return null;
  const safeProgress = Math.max(3, Math.min(100, progress || 8));
  return (
    <div className="mt-5" aria-live="polite">
      <div className="flex items-center justify-between text-xs font-semibold">
        <span className="text-slate-700">{progress >= 20 ? t("upload.progressProcessing") : t("upload.progressUploading")}</span>
        <span className="text-clinical-blue">{Math.round(progress)}%</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-gradient-to-r from-clinical-blue to-clinical-teal transition-all duration-500" style={{ width: `${safeProgress}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-500">{t("upload.progressHelp")}</p>
    </div>
  );
}
