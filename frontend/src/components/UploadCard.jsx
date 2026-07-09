import { FileVideo, Loader2, Upload } from "lucide-react";

export default function UploadCard({
  file,
  error,
  isLoading,
  onFileChange,
  onSubmit,
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="w-full max-w-2xl rounded-lg border border-clinical-line bg-white p-6 shadow-panel"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-clinical-mint text-clinical-teal">
          <FileVideo size={22} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-clinical-ink">Squat video upload</h2>
          <p className="text-sm text-slate-600">MP4, MOV, AVI, MKV, or WEBM</p>
        </div>
      </div>

      <label className="mt-6 flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-clinical-panel px-4 text-center transition hover:border-clinical-teal">
        <Upload className="mb-3 text-clinical-teal" size={28} aria-hidden="true" />
        <span className="text-sm font-medium text-slate-800">
          {file ? file.name : "Choose a squat exercise video"}
        </span>
        <input
          className="sr-only"
          type="file"
          accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm"
          onChange={onFileChange}
        />
      </label>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!file || isLoading}
        className="mt-5 inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-clinical-teal px-5 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isLoading ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <Upload size={18} aria-hidden="true" />}
        {isLoading ? "Analyzing" : "Analyze squat"}
      </button>
    </form>
  );
}
