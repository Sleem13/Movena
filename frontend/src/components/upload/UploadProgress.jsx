export default function UploadProgress({ progress = 0, isLoading }) {
  if (!isLoading) return null;
  const safeProgress = Math.max(3, Math.min(100, progress || 8));
  return <div className="mt-5" aria-live="polite"><div className="flex items-center justify-between text-xs font-semibold"><span className="text-slate-700">{progress >= 100 ? "Processing movement…" : "Uploading video…"}</span><span className="text-clinical-blue">{Math.round(progress)}%</span></div><div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-clinical-blue to-clinical-teal transition-all duration-500" style={{ width: `${safeProgress}%` }} /></div><p className="mt-2 text-xs text-slate-500">Keep this page open while pose landmarks and selected artifacts are prepared.</p></div>;
}
