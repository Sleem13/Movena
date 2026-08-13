import { useEffect, useState } from "react";
import { Activity, AlertTriangle, BrainCircuit, CheckCircle2, Download, FileJson, FileText, Gauge, HeartPulse, Info, RotateCcw, ShieldAlert, Sparkles, Video, VideoOff } from "lucide-react";
import { artifactUrl } from "../../services/api.js";
import { Alert, Badge, Button, Card, EmptyState } from "../common/UI.jsx";
import { AngleTrendChart, ChartCard, IssueBreakdownChart, MovementRadarChart, MovementScoreGauge, RepQualityChart } from "../charts/MovementCharts.jsx";
import CameraGuide from "../upload/CameraGuide.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const movementKey = (exercise) => (exercise || "bodyweight_squat").replace(/(^|_)([a-z])/g, (_, prefix, letter) => (prefix ? "" : "") + letter.toUpperCase());
const tryAgainKey = (exercise) => `results.tryAgain${movementKey(exercise)}`;

export function MetricCard({ label, value, unit, icon: Icon = Activity, tone = "blue" }) {
  const colors = tone === "teal" ? "bg-teal-50 text-clinical-teal" : tone === "amber" ? "bg-amber-50 text-amber-600" : "bg-blue-50 text-clinical-blue";
  return <Card className="p-4 sm:p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p><p className="mt-3 flex items-baseline gap-1.5"><span className="text-3xl font-bold tracking-tight text-clinical-ink">{value ?? "—"}</span>{unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}</p></div><span className={`grid h-10 w-10 place-items-center rounded-xl ${colors}`}><Icon size={19} aria-hidden="true" /></span></div></Card>;
}

export function KPIGrid({ report }) {
  const { t } = useLocale();
  const confidenceValue = report.analysis_confidence ? `${Math.round(report.analysis_confidence.score * 100)}%` : t("common.notAvailable");
  const confidenceTone = report.analysis_confidence?.level === "low" ? "amber" : "teal";
  const common = [
    <MetricCard key="score" label={t("results.movementScore")} value={report.movement_score} unit="/ 100" icon={Gauge} />,
    <MetricCard key="confidence" label={t("results.analysisConfidence")} value={confidenceValue} icon={ShieldAlert} tone={confidenceTone} />,
    <MetricCard key="reps" label={t("results.totalReps")} value={report.total_reps} icon={Activity} tone="teal" />,
  ];
  const issue = <MetricCard key="issues" label={t("results.detectedIssues")} value={report.detected_issues?.length || 0} icon={AlertTriangle} tone="amber" />;
  if (report.exercise === "balance") {
    const balance = report.balance_metrics || {};
    const mode = balance.balance_mode ? balance.balance_mode.replaceAll("_", " ") : t("common.notAvailable");
    return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-8"><MetricCard label={t("results.movementScore")} value={report.movement_score} unit="/ 100" icon={Gauge} /><MetricCard label={t("results.analysisConfidence")} value={confidenceValue} icon={ShieldAlert} tone={confidenceTone} /><MetricCard label={t("results.balanceDuration")} value={balance.hold_duration_sec} unit={t("results.unitSeconds")} icon={Activity} tone="teal" /><MetricCard label={t("results.balanceSway")} value={balance.sway_rms} unit={t("results.unitNormalized")} icon={HeartPulse} /><MetricCard label={t("results.balanceVelocity")} value={balance.sway_velocity} unit={t("results.unitNormalized")} icon={HeartPulse} /><MetricCard label={t("results.balanceTrunkLean")} value={balance.max_trunk_lean_deg} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.balanceMode")} value={mode} icon={Activity} tone="teal" />{issue}</section>;
  }
  if (report.exercise === "walking_gait_screen") {
    const gait = report.gait_metrics || {};
    const stanceSwing = gait.average_stance_percent == null || gait.average_swing_percent == null
      ? t("common.notAvailable")
      : `${gait.average_stance_percent}% / ${gait.average_swing_percent}%`;
    return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-8">{common}<MetricCard label={t("results.gaitCadence")} value={gait.cadence_steps_per_min} unit={t("results.unitStepsMin")} icon={Activity} /><MetricCard label={t("results.gaitCycles")} value={gait.gait_cycles} icon={Activity} tone="teal" /><MetricCard label={t("results.gaitStanceSwing")} value={stanceSwing} icon={HeartPulse} /><MetricCard label={t("results.gaitSymmetry")} value={gait.temporal_symmetry_index} unit={t("results.unitPercent")} icon={HeartPulse} />{issue}</section>;
  }
  if (["shoulder_abduction", "shoulder_flexion"].includes(report.exercise)) return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">{common}<MetricCard label={t("results.averageShoulder")} value={report.average_shoulder_angle} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.averageTrunk")} value={report.average_trunk_angle} unit={t("results.unitDegrees")} icon={HeartPulse} />{issue}</section>;
  if (report.exercise === "hip_abduction") return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">{common}<MetricCard label={t("results.averageHipAbduction")} value={report.average_hip_abduction_angle} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.averageTrunk")} value={report.average_trunk_angle} unit={t("results.unitDegrees")} icon={HeartPulse} />{issue}</section>;
  if (["push_up", "shoulder_press", "bicep_curl", "hammer_curl"].includes(report.exercise)) return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">{common}<MetricCard label={t("results.averageElbow")} value={report.average_elbow_angle} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.averageTrunk")} value={report.average_trunk_angle} unit={t("results.unitDegrees")} icon={HeartPulse} />{issue}</section>;
  return <section aria-label={t("results.metrics")} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">{common}<MetricCard label={t("results.averageKnee")} value={report.average_knee_angle} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.averageHip")} value={report.average_hip_angle} unit={t("results.unitDegrees")} icon={HeartPulse} /><MetricCard label={t("results.averageTrunk")} value={report.average_trunk_angle} unit={t("results.unitDegrees")} icon={HeartPulse} />{issue}</section>;
}

export function ConfidenceAndScoringPanel({ report }) {
  const { t, pretty } = useLocale();
  const confidence = report.analysis_confidence;
  const pose = report.pose_quality;
  const breakdown = report.score_breakdown;
  const scoreRows = {
    sit_to_stand: [[t("results.breakdown.completion"), breakdown?.completion_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.trunkControl"), breakdown?.trunk_control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.poseConfidence"), breakdown?.pose_confidence_score]],
    knee_extension: [[t("results.breakdown.extensionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    shoulder_abduction: [[t("results.breakdown.abductionRange"), breakdown?.abduction_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    shoulder_flexion: [[t("results.breakdown.flexionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    hip_abduction: [[t("results.breakdown.abductionRange"), breakdown?.abduction_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score], [t("results.breakdown.pelvisTrunkStability"), breakdown?.pelvis_trunk_stability_score]],
    walking_gait_screen: [[t("results.breakdown.gaitPhase"), breakdown?.gait_phase_score], [t("results.breakdown.cadence"), breakdown?.cadence_score], [t("results.breakdown.symmetry"), breakdown?.symmetry_score], [t("results.breakdown.strideConsistency"), breakdown?.stride_consistency_score], [t("results.breakdown.kinematicRange"), breakdown?.kinematic_range_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score]],
    balance: [[t("results.breakdown.holdDuration"), breakdown?.hold_duration_score], [t("results.breakdown.swayControl"), breakdown?.sway_control_score], [t("results.breakdown.trunkControl"), breakdown?.trunk_control_score], [t("results.breakdown.pelvisControl"), breakdown?.pelvis_control_score], [t("results.breakdown.kneeStability"), breakdown?.knee_stability_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score]],
    push_up: [[t("results.breakdown.extensionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    shoulder_press: [[t("results.breakdown.extensionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    bicep_curl: [[t("results.breakdown.flexionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    hammer_curl: [[t("results.breakdown.flexionRange"), breakdown?.extension_range_score], [t("results.breakdown.movementControl"), breakdown?.control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.visibility"), breakdown?.posture_visibility_score], [t("results.breakdown.repCompletion"), breakdown?.rep_completion_score]],
    bodyweight_squat: [[t("results.breakdown.depth"), breakdown?.depth_score], [t("results.breakdown.kneeAlignment"), breakdown?.knee_alignment_score], [t("results.breakdown.trunkControl"), breakdown?.trunk_control_score], [t("results.breakdown.consistency"), breakdown?.consistency_score], [t("results.breakdown.poseConfidence"), breakdown?.pose_confidence_score]],
  };
  const rows = breakdown ? (scoreRows[report.exercise] || scoreRows.bodyweight_squat).filter(([, value]) => value != null) : [];
  const confidenceTone = confidence?.level === "high" ? "teal" : confidence?.level === "low" ? "amber" : "blue";
  const partialCount = report.ignored_partial_reps || 0;
  return <div className="grid gap-5 lg:grid-cols-2"><Card className="p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-widest text-clinical-teal">{t("results.reliability")}</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">{t("results.analysisConfidence")}</h2></div><Badge tone={confidenceTone}>{confidence ? t("results.confidenceLabel", { level: pretty(confidence.level) }) : t("common.notAvailable")}</Badge></div><div className="mt-4 grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold text-slate-500">{t("results.repCountConfidence")}</p><p className="mt-2 text-2xl font-bold text-clinical-ink">{report.rep_count_confidence == null ? t("common.notAvailable") : `${Math.round(report.rep_count_confidence * 100)}%`}</p><p className="mt-1 text-xs text-slate-500">{t("results.partialIgnored", { count: partialCount, cycle: partialCount === 1 ? t("results.cycleSingular") : t("results.cyclePlural") })}</p></div><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold text-slate-500">{t("results.poseQuality")}</p><p className="mt-2 text-2xl font-bold text-clinical-ink">{pose ? `${Math.round(pose.score * 100)}%` : t("common.notAvailable")}</p><p className="mt-1 text-xs text-slate-500">{pose ? t("results.framesDetected", { level: pretty(pose.level), rate: Math.round(pose.pose_detection_rate * 100) }) : t("results.qualityNotMeasured")}</p></div></div>{confidence?.warnings?.length ? <Alert className="mt-4" tone="warning" title={t("results.reviewQuality")}>{confidence.warnings.join(" ")}</Alert> : <p className="mt-4 text-sm text-slate-500">{t("results.noConfidenceWarnings")}</p>}</Card><Card className="p-5"><p className="text-xs font-bold uppercase tracking-widest text-clinical-blue">{t("results.explainableScore")}</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">{t("results.scoreBreakdown")}</h2>{rows.length ? <div className="mt-4 space-y-3">{rows.map(([label, value]) => <div key={label}><div className="mb-1.5 flex justify-between text-xs"><span className="font-semibold text-slate-600">{label}</span><span className="font-bold text-slate-800">{value}/100</span></div><div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-clinical-blue to-clinical-teal" style={{ width: `${value}%` }} /></div></div>)}</div> : <EmptyState title={t("results.breakdownUnavailable")} description={t("results.breakdownOlder")} icon={Gauge} />}</Card></div>;
}

export function RepCountReliabilityNotice({ report }) {
  const { t } = useLocale();
  const partials = report.ignored_partial_reps || 0;
  const lowConfidence = report.rep_count_confidence != null && report.rep_count_confidence < 0.5;
  if (!lowConfidence && partials === 0) return null;
  return <Card className="p-5"><div className="flex flex-wrap items-center gap-3"><Activity size={19} className="text-amber-600" aria-hidden="true" /><h2 className="font-bold text-clinical-ink">{t("results.repReview")}</h2>{lowConfidence && <Badge tone="amber">{t("results.manualReview")}</Badge>}</div><p className="mt-3 text-sm leading-6 text-slate-600">{lowConfidence ? t("results.lowConfidenceText") : t("results.partialText", { count: partials, cycle: partials === 1 ? t("results.cycleSingular") : t("results.cyclePlural"), verb: partials === 1 ? "was" : "were" })}</p>{lowConfidence && <p className="mt-2 text-xs leading-5 text-slate-500">{report.exercise === "bodyweight_squat" ? t("results.trimSquat") : t("results.trimExercise")}</p>}</Card>;
}

export function ScoreGaugeCard({ report }) {
  const { t } = useLocale();
  const issueCount = report.detected_issues?.length || 0;
  const issueLabel = issueCount === 1 ? t("results.observationSingular") : t("results.observationPlural");
  return <Card className="p-5"><div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-widest text-clinical-teal">{t("results.sessionOverview")}</p><h2 className="mt-1 text-lg font-bold text-clinical-ink">{t("results.movementScore")}</h2></div><Badge tone={issueCount ? "amber" : "teal"}>{issueCount ? t("results.observationCount", { count: issueCount, label: issueLabel }) : t("results.noMajorFlags")}</Badge></div><MovementScoreGauge score={report.movement_score} /><p className="text-center text-xs leading-5 text-slate-500">{t("results.scoreDisclaimer")}</p></Card>;
}

export function AnnotatedVideoPreview({ url, exercise = "bodyweight_squat" }) {
  const { t, exerciseText } = useLocale();
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [url]);
  if (!url || failed) return <EmptyState title={failed ? t("results.annotatedLoadFailed") : t("results.annotatedNotGenerated")} description={failed ? t("results.artifactExpired") : t("results.enableOverlay")} icon={VideoOff} />;
  return <div><video aria-label={`Annotated ${exerciseText(exercise).short} movement preview`} className="aspect-video w-full rounded-xl bg-slate-950 object-contain" controls preload="metadata" onError={() => setFailed(true)}><source src={url} type="video/mp4" />{t("results.videoUnsupported")}</video><p className="mt-2 text-xs leading-5 text-slate-500">{t("results.overlayHelp")}</p></div>;
}

export function VideoReviewPanel({ report, originalVideoUrl }) {
  const { t, exerciseText } = useLocale();
  const overlayUrl = artifactUrl(report.overlay_preview_url || report.overlay_download_url);
  return <Card className="p-5"><div className="mb-5 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-clinical-blue"><Video size={19} aria-hidden="true" /></span><div><h2 className="text-lg font-bold text-clinical-ink">{t("results.videoReview")}</h2><p className="text-xs text-slate-500">{t("results.videoReviewHelp")}</p></div></div><div className="grid gap-5 xl:grid-cols-2"><div><p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">{t("results.originalUpload")}</p>{originalVideoUrl ? <video aria-label={`Original uploaded ${exerciseText(report.exercise).short} video`} className="aspect-video w-full rounded-xl bg-slate-950 object-contain" controls src={originalVideoUrl} /> : <EmptyState title={t("results.originalPreviewUnavailable")} description={t("results.originalPreviewHelp")} icon={VideoOff} />}</div><div><p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">{t("results.annotatedPreview")}</p><AnnotatedVideoPreview url={overlayUrl} exercise={report.exercise} /></div></div></Card>;
}

export function DetectedIssuesList({ issues = [] }) {
  const { t, pretty } = useLocale();
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><AlertTriangle size={19} className="text-amber-500" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">{t("results.detectedIssues")}</h2></div>{issues.length ? <ul className="space-y-2">{issues.map((issue) => <li key={issue} className="flex items-center justify-between gap-3 rounded-xl border border-amber-100 bg-amber-50/70 px-3.5 py-3 text-sm font-semibold text-amber-950"><span>{pretty(issue)}</span><Badge tone="amber">{t("common.review")}</Badge></li>)}</ul> : <div className="flex gap-3 rounded-xl border border-teal-100 bg-teal-50 p-4 text-sm text-teal-900"><CheckCircle2 className="shrink-0" size={18} aria-hidden="true" /><p>{t("results.noIssues")}</p></div>}</Card>;
}

export function FeedbackPanel({ report }) {
  const { t } = useLocale();
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><Sparkles size={19} className="text-clinical-teal" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">{t("results.summaryFeedback")}</h2></div><div className="rounded-xl bg-blue-50/70 p-4 text-sm leading-6 text-slate-700">{report.summary || t("results.noSummary")}</div><h3 className="mb-2 mt-5 text-xs font-bold uppercase tracking-wider text-slate-500">{t("results.correctiveFeedback")}</h3>{report.feedback?.length ? <ul className="space-y-2">{report.feedback.map((item, index) => <li key={`${item}-${index}`} className="flex gap-3 rounded-xl border border-slate-100 px-3.5 py-3 text-sm leading-6 text-slate-700"><CheckCircle2 className="mt-1 shrink-0 text-clinical-teal" size={16} aria-hidden="true" /><span>{item}</span></li>)}</ul> : <p className="text-sm text-slate-500">{t("results.noFeedback")}</p>}</Card>;
}

export function MLSecondOpinionCard({ prediction }) {
  const { t, pretty } = useLocale();
  if (!prediction) return null;
  const confidence = prediction.confidence == null ? t("common.notAvailable") : `${Math.round(prediction.confidence * 100)}%`;
  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-clinical-line bg-violet-50/60 p-5">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-100 text-violet-700"><BrainCircuit size={20} aria-hidden="true" /></span>
          <div><h2 className="text-lg font-bold text-clinical-ink">{t("results.mlTitle")}</h2><p className="text-xs text-slate-500">{t("results.mlHelp")}</p></div>
        </div>
        <Badge tone="amber">{t("results.mlBadge")}</Badge>
      </div>
      <div className="p-5">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl bg-slate-50 p-3">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{t("results.predictedLabel")}</p>
            <p className="mt-2 text-sm font-bold text-slate-800">{prediction.predicted_label ? pretty(prediction.predicted_label) : t("common.unavailable")}</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{t("common.confidence")}</p>
            <p className="mt-2 text-sm font-bold text-slate-800">{confidence}</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{t("results.model")}</p>
            <p className="mt-2 text-sm font-bold text-slate-800">{prediction.model_name || t("results.baselineUnavailable")}</p>
            <p className="mt-1 text-[11px] text-slate-500">{prediction.model_version}</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{t("results.providerStatus")}</p>
            <p className="mt-2 text-sm font-bold text-slate-800">{prediction.provider_status ? pretty(prediction.provider_status) : t("common.unavailable")}</p>
            <p className="mt-1 text-[11px] text-slate-500">{prediction.model_mode ? pretty(prediction.model_mode) : t("results.modelMode")}</p>
          </div>
        </div>
        <div className="mt-4"><Alert tone="warning" title={t("results.mlPrimary")}>{prediction.warning || t("results.mlWarning")}</Alert></div>
      </div>
    </Card>
  );
}

export function MLDisagreementNote({ prediction }) {
  const { t } = useLocale();
  if (!prediction?.disagreement_note) return null;
  return <Alert tone="warning" title={t("results.mlDisagreement")}>{prediction.disagreement_note}</Alert>;
}

export function LimitationsCard({ limitations = [] }) {
  const { t } = useLocale();
  return <Card className="p-5"><div className="mb-4 flex items-center gap-2"><Info size={19} className="text-slate-500" aria-hidden="true" /><h2 className="text-lg font-bold text-clinical-ink">{t("results.knownLimitations")}</h2></div>{limitations.length ? <ul className="space-y-2 text-sm leading-6 text-slate-600">{limitations.map((item) => <li key={item} className="flex gap-3"><span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-300" />{item}</li>)}</ul> : <p className="text-sm text-slate-500">{t("results.noLimitations")}</p>}<div className="mt-5 flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950"><ShieldAlert className="mt-0.5 shrink-0" size={19} aria-hidden="true" /><div><p className="font-bold">{t("results.medicalDisclaimer")}</p><p className="mt-1">{t("results.disclaimer")}</p></div></div></Card>;
}

export function ExportActions({ report }) {
  const { t } = useLocale();
  const reportUrl = artifactUrl(report.report_download_url);
  const overlayUrl = artifactUrl(report.overlay_download_url);
  function exportJson() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `physiovision-${report.exercise || "movement"}-analysis.json`;
    link.click();
    URL.revokeObjectURL(url);
  }
  return <div className="flex flex-wrap gap-2">{reportUrl && <Button as="a" href={reportUrl} download><FileText size={16} aria-hidden="true" />{t("results.downloadPdf")}</Button>}{overlayUrl && <Button as="a" variant="secondary" href={overlayUrl} download><Download size={16} aria-hidden="true" />{t("results.downloadOverlay")}</Button>}<Button variant="secondary" type="button" onClick={exportJson}><FileJson size={16} aria-hidden="true" />{t("results.exportJson")}</Button></div>;
}

export function RejectedAnalysisCard({ report, onAnalyzeAnother }) {
  const { t, exerciseText } = useLocale();
  const warnings = report.validation_warnings || report.input_validity?.warnings || [];
  const exercise = exerciseText(report.exercise || "bodyweight_squat");
  return <div className="space-y-5"><Card className="border-amber-200 p-6"><div className="flex items-start gap-4"><span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-amber-100 text-amber-700"><AlertTriangle size={23} aria-hidden="true" /></span><div><Badge tone="amber">{t("results.recordingReview")}</Badge><h2 className="mt-3 text-2xl font-bold text-clinical-ink">{t("results.noValidMovement", { exercise: exercise.short })}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{report.message || t("results.rejectedDescription", { movement: exercise.short })}</p></div></div>{warnings.length > 0 && <ul className="mt-5 space-y-2 rounded-xl bg-amber-50 p-4 text-sm text-amber-950">{warnings.map((warning) => <li key={warning} className="flex gap-2"><span aria-hidden="true">•</span><span>{warning}</span></li>)}</ul>}<div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4"><p className="font-semibold text-clinical-ink">{t("results.tryAgain")}</p><p className="mt-1 text-sm leading-6 text-slate-600">{t(tryAgainKey(report.exercise || "bodyweight_squat"))}</p></div><Button className="mt-5" type="button" onClick={onAnalyzeAnother}><RotateCcw size={16} aria-hidden="true" />{t("results.analyzeAnother")}</Button></Card><CameraGuide exercise={report.exercise || "bodyweight_squat"} /><LimitationsCard limitations={report.limitations} /></div>;
}

export default function ResultsDashboard({ report, originalVideoUrl, onAnalyzeAnother }) {
  const { t } = useLocale();
  if (report.status === "rejected") return <RejectedAnalysisCard report={report} onAnalyzeAnother={onAnalyzeAnother} />;
  return <div className="space-y-5"><KPIGrid report={report} /><ConfidenceAndScoringPanel report={report} /><RepCountReliabilityNotice report={report} /><div className="grid gap-5 lg:grid-cols-[340px_1fr]"><ScoreGaugeCard report={report} /><ChartCard title={t("chart.angleTrend")} description={t("chart.angleTrendDescription")}><AngleTrendChart frames={report.frame_analysis || []} /></ChartCard></div><VideoReviewPanel report={report} originalVideoUrl={originalVideoUrl} /><div className="grid gap-5 lg:grid-cols-2"><DetectedIssuesList issues={report.detected_issues} /><FeedbackPanel report={report} /></div><MLSecondOpinionCard prediction={report.ml_prediction} /><MLDisagreementNote prediction={report.ml_prediction} /><section aria-label="Movement charts" className="grid gap-5 lg:grid-cols-3"><ChartCard title={t("chart.issueBreakdown")} description={t("chart.issueBreakdownDescription")}><IssueBreakdownChart report={report} /></ChartCard><ChartCard title={t("chart.movementProfile")} description={t("chart.movementProfileDescription")}><MovementRadarChart report={report} /></ChartCard><ChartCard title={t("chart.repQuality")} description={t("chart.repQualityDescription")}><RepQualityChart reps={report.rep_analysis || []} /></ChartCard></section><LimitationsCard limitations={report.limitations} /><div className="flex flex-col gap-3 rounded-2xl border border-clinical-line bg-white p-4 shadow-panel sm:flex-row sm:items-center sm:justify-between"><ExportActions report={report} /><Button variant="ghost" type="button" onClick={onAnalyzeAnother}><RotateCcw size={16} aria-hidden="true" />{t("results.analyzeAnother")}</Button></div></div>;
}

export const DISCLAIMER_KEY = "results.disclaimer";
