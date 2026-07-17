import { useState } from "react";
import { Check, FileVideo2, UploadCloud, X } from "lucide-react";
import { Alert, Button, Card, LoadingSpinner } from "../common/UI.jsx";
import UploadProgress from "./UploadProgress.jsx";

const EXERCISE_NAMES = {
  bodyweight_squat: { short: "squat", title: "Squat" },
  sit_to_stand: { short: "sit-to-stand", title: "Sit-to-stand" },
  knee_extension: { short: "knee extension", title: "Knee extension" },
  shoulder_abduction: { short: "shoulder abduction", title: "Shoulder abduction" },
};

export default function UploadCard({ exercise = "bodyweight_squat", file, error, isLoading, progress, onFileChange, onFileSelect, onSubmit }) {
  const [dragging, setDragging] = useState(false);
  const names = EXERCISE_NAMES[exercise] || { short: "movement", title: "Movement" };
  function drop(event) {
    event.preventDefault(); setDragging(false);
    const selected = event.dataTransfer.files?.[0];
    if (selected) onFileSelect(selected);
  }
  return <Card className="p-5 sm:p-6"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-clinical-blue"><FileVideo2 size={22} aria-hidden="true" /></span><div><h2 className="text-lg font-bold text-clinical-ink">{names.title} video upload</h2><p className="text-xs text-slate-500">MP4, MOV, AVI, MKV, or WEBM · Maximum 100 MB</p></div></div><label onDragEnter={(event) => { event.preventDefault(); setDragging(true); }} onDragOver={(event) => event.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={drop} className={`mt-5 flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 text-center transition ${dragging ? "border-clinical-blue bg-blue-50" : file ? "border-teal-200 bg-teal-50/50" : "border-slate-200 bg-slate-50/70 hover:border-blue-300 hover:bg-blue-50/40"}`}><span className={`grid h-14 w-14 place-items-center rounded-2xl ${file ? "bg-teal-100 text-clinical-teal" : "bg-white text-clinical-blue shadow-sm"}`}>{file ? <Check size={25} aria-hidden="true" /> : <UploadCloud size={25} aria-hidden="true" />}</span><span className="mt-4 text-sm font-bold text-slate-800">{file ? file.name : `Drag and drop your ${names.short} video`}</span><span className="mt-1 text-xs text-slate-500">{file ? `${(file.size / 1024 / 1024).toFixed(1)} MB selected` : "or click to browse files"}</span><input className="sr-only" aria-label={`Choose a ${names.short} exercise video`} type="file" accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm" onChange={onFileChange} disabled={isLoading} /></label>{error && <div className="mt-4"><Alert title="Analysis could not start">{error}</Alert></div>}<UploadProgress progress={progress} isLoading={isLoading} /><div className="mt-5 flex flex-wrap items-center justify-between gap-3"><p className="flex items-center gap-2 text-xs text-slate-500"><X size={14} aria-hidden="true" />Uploads are processed temporarily and are not patient records.</p><Button type="submit" onClick={onSubmit} disabled={!file || isLoading}>{isLoading ? <LoadingSpinner label="Analyzing" /> : <><UploadCloud size={17} aria-hidden="true" />Analyze {names.short}</>}</Button></div></Card>;
}
