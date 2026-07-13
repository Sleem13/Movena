import { useEffect, useState } from "react";
import { Activity, AlertTriangle, BrainCircuit, CheckCircle2, Download, FileJson, FileText, Gauge, HeartPulse, Info, RotateCcw, ShieldAlert, Sparkles, Video, VideoOff } from "lucide-react";
import { artifactUrl } from "../../services/api.js";
import { Alert, Badge, Button, Card, EmptyState } from "../common/UI.jsx";
import { AngleTrendChart, ChartCard, IssueBreakdownChart, MovementRadarChart, MovementScoreGauge, RepQualityChart } from "../charts/MovementCharts.jsx";

const DISCLAIMER = "This analysis is for exercise monitoring and educational support only. It does not replace assessment, diagnosis, or treatment by a licensed physiotherapist or healthcare professional.";
const pretty = (value = "") => value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export function MetricCard({ label, value, unit, icon: Icon = Activity, tone = "blue" }) {
  const colors = tone === "teal" ? "bg-teal-50 text-clinical-teal" : tone === "amber" ? "bg-amber-50 text-amber-600" : "bg-blue-50 text-clinical-blue";
  return <Card className="p-4 sm:p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p><p className="mt-3 flex items-baseline gap-1.5"><span className="text-3xl font-bold tracking-tight text-clinical-ink">{value ?? "—"}</span>{unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}</p></div><span className={`grid h-10 w-10 place-items-center rounded-xl ${colors}`}><Icon size={19} aria-hidden="true" /></span></div></Card>;
}

export function KPIGrid({ report }) {
  return <section aria-label="Analysis key metrics" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7"><MetricCard label="Movement score" value={report.movement_score} unit="/ 100" icon={Gauge} /><MetricCard label="Analysis confidence" value={report.analysis_confidence ? `${Math.round(report.analysis_confidence.score * 100)}%` : "Not available"} icon={ShieldAlert} tone={report.analysis_confidence?.level === "low" ? "amber" : "teal"} /><MetricCard label="Total reps" value={report.total_reps} icon={Activity} tone="teal" /><MetricCard label="Average knee" value={report.average_knee_angle} unit="degrees" icon={HeartPulse} /><MetricCard label="Average hip" value={report.average_hip_angle} unit="degrees" icon={HeartPulse} /><MetricCard label="Average trunk" value={report.average_trunk_angle} unit="degrees" icon={HeartPulse} /><MetricCard label="Detected issues" value={report.detected_issues?.length || 0} icon={AlertTriangle} tone="amber" /></section>;
}

export function ConfidenceAndScoringPanel({ report }) {
  const confidence = report.analysis_confidence;
  const pose = report.pose_quality;
  const breakdown = report.score_breakdown;
  const rows = breakdown ? [["Depth", breakdown.depth_score], ["Knee alignment", breakdown.knee_alignment_score], ["Trunk control", breakdown.trunk_control_score], ["Consistency", breakdown.consistency_score], ["Pose confidence", breakdown.pose_confidence_score]] : [];
  const confidenceTone = confidence?.level === "high" ? "teal" : confidence?.level === "low" ? "amber" : "blue";
  return <div className="grid gap-5 lg:grid-cols-2"><Card className="p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-widest text-clinical-teal">Reliability</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">Analysis confidence</h2></div><Badge tone={confidenceTone}>{confidence ? `${pretty(confidence.level)} confidence` : "Not available"}</Badge></div><div className="mt-4 grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold text-slate-500">Rep count confidence</p><p className="mt-2 text-2xl font-bold text-clinical-ink">{report.rep_count_confidence == null ? "Not available" : `${Math.round(report.rep_count_confidence * 100)}%`}</p><p className="mt-1 text-xs text-slate-500">{report.ignored_partial_reps || 0} partial cycle{report.ignored_partial_reps === 1 ? "" : "s"} ignored</p></div><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold text-slate-500">Pose quality</p><p className="mt-2 text-2xl font-bold text-clinical-ink">{pose ? `${Math.round(pose.score * 100)}%` : "Not available"}</p><p className="mt-1 text-xs text-slate-500">{pose ? `${pretty(pose.level)} · ${Math.round(pose.pose_detection_rate * 100)}% frames detected` : "Recording quality was not measured."}</p></div></div>{confidence?.warnings?.length ? <Alert className="mt-4" tone="warning" title="Review recording quality">{confidence.warnings.join(" ")}</Alert> : <p className="mt-4 text-sm text-slate-500">No additional confidence warnings were returned.</p>}</Card><Card className="p-5"><p className="text-xs font-bold uppercase tracking-widest text-clinical-blue">Explainable score</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">Score breakdown</h2>{rows.length ? <div className="mt-4 space-y-3">{rows.map(([label, value]) => <div key={label}><div className="mb-1.5 flex justify-between text-xs"><span className="font-semibold text-slate-600">{label}</span><span className="font-bold text-slate-800">{value}/100</span></div><div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-clinical-blue to-clinical-teal" style={{ width: `${value}%` }} /></div></div>)}</div> : <EmptyState title="Score breakdown unavailable" description="This analysis used an older API response." icon={Gauge} />}</Card></div>;
}

export function ScoreGaugeCard({ report }) {
  return <Card className="p-5"><div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-widest text-clinical-teal">Session overview</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">Movement score</h2></div><Badge tone={report.detected_issues?.length ? "amber" : "teal"}>{report.detected_issues?.length ? `${report.detected_issues.length} observation${report.detected_issues.length === 1 ? "" : "s"}` : "No major flags"}</Badge></div><MovementScoreGauge score={report.movement_score} /><p className="text-center text-xs leading-5 text-slate-500">A rule-based session summary, not a diagnosis or clinical outcome measure.</p></Card>;
}

export function AnnotatedVideoPreview({ url }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [url]);
  if (!url || failed) return <EmptyState title={failed ? "Annotated preview could not be loaded" : "No annotated preview was generated for this analysis."} description={failed ? "The temporary artifact may have expired. Retry the analysis to generate a new overlay." : "Enable Annotated video on the upload page to request an experimental 2D skeleton overlay."} icon={VideoOff} />;
  return <div><video aria-label="Annotated squat movement preview" className="aspect-video w-full rounded-xl bg-slate-950 object-contain" controls preload="metadata" onError={() => setFailed(true)}><source src={url} type="video/mp4" />Your browser does not support video playback.</video><p className="mt-2 text-xs leading-5 text-slate-500">Experimental 2D overlay; markers may shift with occlusion, motion blur, or camera angle.</p></div>;
}

export function VideoReviewPanel({ report, originalVideoUrl }) {
  const overlayUrl = artifactUrl(report.overlay_preview_url || report.overlay_download_url);
  return <Card className="p-5"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-clinical-blue"><Video size={19} aria-hidden="true" /></span><div><h2 className="text-lg font-bold text-clinical-ink">Video review</h2><p className="text-xs text-slate-500">Compare the source recording with the generated pose overlay.</p></div></div><div className="grid gap-5 xl:grid-cols-2"><div><p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">Original upload</p>{originalVideoUrl ? <video aria-label="Original uploaded squat video" className="aspect-video w-full rounded-xl bg-slate-950 object-contain" controls src={originalVideoUrl} /> : <EmptyState title="Original preview unavailable" description="Local previews are available immediately after uploading in this browser session." icon={VideoOff} />}</div><div><p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">Annotated movement preview</p><AnnotatedVideoPreview url={overlayUrl} /></div></div></Card>;
}

export function DetectedIssuesList({ issues = [] }) {
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><AlertTriangle size={19} className="text-amber-500" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">Detected issues</h2></div>{issues.length ? <ul className="space-y-2">{issues.map((issue) => <li key={issue} className="flex items-center justify-between gap-3 rounded-xl border border-amber-100 bg-amber-50/70 px-3.5 py-3 text-sm font-semibold text-amber-950"><span>{pretty(issue)}</span><Badge tone="amber">Review</Badge></li>)}</ul> : <div className="flex gap-3 rounded-xl border border-teal-100 bg-teal-50 p-4 text-sm text-teal-900"><CheckCircle2 className="shrink-0" size={18} aria-hidden="true" /><p>No major movement issues were flagged by the current rules.</p></div>}</Card>;
}

export function FeedbackPanel({ report }) {
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><Sparkles size={19} className="text-clinical-teal" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">Summary and feedback</h2></div><div className="rounded-xl bg-blue-50/70 p-4 text-sm leading-6 text-slate-700">{report.summary || "No summary returned."}</div><h3 className="mb-2 mt-5 text-xs font-bold uppercase tracking-wider text-slate-500">Corrective feedback</h3>{report.feedback?.length ? <ul className="space-y-2">{report.feedback.map((item, index) => <li key={`${item}-${index}`} className="flex gap-3 rounded-xl border border-slate-100 px-3.5 py-3 text-sm leading-6 text-slate-700"><CheckCircle2 className="mt-1 shrink-0 text-clinical-teal" size={16} aria-hidden="true" /><span>{item}</span></li>)}</ul> : <p className="text-sm text-slate-500">No corrective feedback returned.</p>}</Card>;
}

export function MLSecondOpinionCard({ prediction }) {
  if (!prediction) return null;
  const confidence = prediction.confidence == null ? "Not available" : `${Math.round(prediction.confidence * 100)}%`;
  return <Card className="overflow-hidden"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-clinical-line bg-violet-50/60 p-5"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-100 text-violet-700"><BrainCircuit size={20} aria-hidden="true" /></span><div><h2 className="text-lg font-bold text-clinical-ink">ML second opinion</h2><p className="text-xs text-slate-500">Optional experimental comparison</p></div></div><Badge tone="amber">Experimental · not clinically validated</Badge></div><div className="p-5"><div className="grid gap-3 sm:grid-cols-3"><div className="rounded-xl bg-slate-50 p-3"><p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Predicted label</p><p className="mt-2 text-sm font-bold text-slate-800">{prediction.predicted_label ? pretty(prediction.predicted_label) : "Unavailable"}</p></div><div className="rounded-xl bg-slate-50 p-3"><p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Confidence</p><p className="mt-2 text-sm font-bold text-slate-800">{confidence}</p></div><div className="rounded-xl bg-slate-50 p-3"><p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Model</p><p className="mt-2 text-sm font-bold text-slate-800">{prediction.model_name || "Baseline unavailable"}</p><p className="mt-1 text-[11px] text-slate-500">{prediction.model_version}</p></div></div><div className="mt-4"><Alert tone="warning" title="Rule-based analysis remains primary">{prediction.warning || "This output is experimental and must not guide clinical decisions."}</Alert></div></div></Card>;
}

export function MLDisagreementNote({ prediction }) {
  if (!prediction?.disagreement_note) return null;
  return <Alert tone="warning" title="Experimental ML disagreement">{prediction.disagreement_note}</Alert>;
}

export function LimitationsCard({ limitations = [] }) {
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><Info size={19} className="text-slate-500" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">Known limitations</h2></div>{limitations.length ? <ul className="space-y-2 text-sm leading-6 text-slate-600">{limitations.map((item) => <li key={item} className="flex gap-3"><span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-300" />{item}</li>)}</ul> : <p className="text-sm text-slate-500">No additional limitations returned.</p>}<div className="mt-5 flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950"><ShieldAlert className="mt-0.5 shrink-0" size={19} aria-hidden="true" /><div><p className="font-bold">Medical disclaimer</p><p className="mt-1">{DISCLAIMER}</p></div></div></Card>;
}

export function ExportActions({ report }) {
  const reportUrl = artifactUrl(report.report_download_url);
  const overlayUrl = artifactUrl(report.overlay_download_url);
  function exportJson() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a"); link.href = url; link.download = "physiovision-squat-analysis.json"; link.click(); URL.revokeObjectURL(url);
  }
  return <div className="flex flex-wrap gap-2">{reportUrl && <Button as="a" href={reportUrl} download><FileText size={16} aria-hidden="true" />Download PDF report</Button>}{overlayUrl && <Button as="a" variant="secondary" href={overlayUrl} download><Download size={16} aria-hidden="true" />Download annotated video</Button>}<Button variant="secondary" type="button" onClick={exportJson}><FileJson size={16} aria-hidden="true" />Export JSON</Button></div>;
}

export default function ResultsDashboard({ report, originalVideoUrl, onAnalyzeAnother }) {
  return <div className="space-y-5"><KPIGrid report={report} /><ConfidenceAndScoringPanel report={report} /><div className="grid gap-5 lg:grid-cols-[340px_1fr]"><ScoreGaugeCard report={report} /><ChartCard title="Angle trend" description="Sampled angle estimates across the analyzed video."><AngleTrendChart frames={report.frame_analysis || []} /></ChartCard></div><VideoReviewPanel report={report} originalVideoUrl={originalVideoUrl} /><div className="grid gap-5 lg:grid-cols-2"><DetectedIssuesList issues={report.detected_issues} /><FeedbackPanel report={report} /></div><MLSecondOpinionCard prediction={report.ml_prediction} /><MLDisagreementNote prediction={report.ml_prediction} /><section aria-label="Movement charts" className="grid gap-5 lg:grid-cols-3"><ChartCard title="Issue breakdown" description="Summary flags or sampled frame issue counts."><IssueBreakdownChart report={report} /></ChartCard><ChartCard title="Movement profile" description="Normalized descriptive values from this session."><MovementRadarChart report={report} /></ChartCard><ChartCard title="Rep quality" description="Individual repetition scoring requires rep-level API data."><RepQualityChart reps={report.rep_analysis || []} /></ChartCard></section><LimitationsCard limitations={report.limitations} /><div className="flex flex-col gap-3 rounded-2xl border border-clinical-line bg-white p-4 shadow-panel sm:flex-row sm:items-center sm:justify-between"><ExportActions report={report} /><Button variant="ghost" type="button" onClick={onAnalyzeAnother}><RotateCcw size={16} aria-hidden="true" />Analyze another video</Button></div></div>;
}

export { DISCLAIMER };
