import { BarChart3, ChartNoAxesColumnIncreasing } from "lucide-react";
import { Card, EmptyState } from "../common/UI.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const COLORS = { knee: "#2563eb", hip: "#0f8f83", trunk: "#f59e0b" };
const SHOULDER_COLORS = { shoulder: "#2563eb", trunk: "#f59e0b" };
const HIP_ABDUCTION_COLORS = { hip_abduction: "#0f8f83", trunk: "#f59e0b" };
const ELBOW_COLORS = { elbow: "#2563eb", trunk: "#f59e0b" };

export function MovementScoreGauge({ score = 0, size = 180 }) {
  const { t } = useLocale();
  const bounded = Math.max(0, Math.min(100, Number(score) || 0));
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  return <div className="relative mx-auto" style={{ width: size, height: size }} role="img" aria-label={`${t("results.movementScore")} ${bounded} ${t("chart.outOf100")}`}><svg viewBox="0 0 160 160" className="-rotate-90"><circle cx="80" cy="80" r={radius} fill="none" stroke="#e8eef3" strokeWidth="13" /><circle cx="80" cy="80" r={radius} fill="none" stroke="url(#scoreGradient)" strokeWidth="13" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - bounded / 100)} /><defs><linearGradient id="scoreGradient"><stop stopColor="#2563eb" /><stop offset="1" stopColor="#0f8f83" /></linearGradient></defs></svg><div className="absolute inset-0 grid place-content-center text-center"><span className="text-4xl font-bold text-clinical-ink">{bounded}</span><span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{t("chart.outOf100")}</span></div></div>;
}

function points(rows, key, width = 600, height = 190) {
  if (!rows.length) return "";
  return rows.map((row, index) => {
    const x = rows.length === 1 ? width / 2 : (index / (rows.length - 1)) * width;
    const y = height - (Math.max(0, Math.min(180, Number(row[key]) || 0)) / 180) * height;
    return `${x},${y}`;
  }).join(" ");
}

export function AngleTrendChart({ frames = [] }) {
  const { t, pretty } = useLocale();
  if (!frames.length) return <EmptyState compact title={t("chart.angleUnavailable")} description={t("chart.angleHelp")} icon={BarChart3} />;
  const colors = frames.some((frame) => frame.hip_abduction_angle != null) ? HIP_ABDUCTION_COLORS : frames.some((frame) => frame.shoulder_angle != null) ? SHOULDER_COLORS : frames.some((frame) => frame.elbow_angle != null) ? ELBOW_COLORS : COLORS;
  return <div><div className="mb-4 flex flex-wrap gap-4 text-xs font-semibold text-slate-600">{Object.entries(colors).map(([key, color]) => <span key={key} className="flex items-center gap-2"><i className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />{pretty(key)}</span>)}</div><div className="overflow-hidden rounded-xl bg-slate-50 p-3"><svg viewBox="0 0 600 210" className="h-56 w-full" role="img" aria-label={t("chart.angleAria")}><g stroke="#dce6ee" strokeWidth="1">{[0, 60, 120, 180].map((value) => <line key={value} x1="0" x2="600" y1={190 - value / 180 * 190} y2={190 - value / 180 * 190} />)}</g>{Object.entries(colors).map(([key, color]) => <polyline key={key} points={points(frames, `${key}_angle`)} fill="none" stroke={color} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />)}<text x="4" y="207" fill="#64748b" fontSize="11">{t("chart.start")}</text><text x="566" y="207" fill="#64748b" fontSize="11">{t("chart.end")}</text></svg></div></div>;
}

export function IssueBreakdownChart({ report }) {
  const { t, pretty } = useLocale();
  const frameIssues = report.frame_analysis?.map((row) => row.detected_issue).filter(Boolean) || [];
  const source = frameIssues.length ? frameIssues : report.detected_issues || [];
  const counts = source.reduce((all, issue) => ({ ...all, [issue]: (all[issue] || 0) + 1 }), {});
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return <EmptyState compact title={t("chart.noIssueBreakdown")} description={t("chart.noIssueHelp")} icon={ChartNoAxesColumnIncreasing} />;
  const max = Math.max(...entries.map(([, count]) => count));
  return <div className="space-y-4">{entries.map(([issue, count]) => <div key={issue}><div className="mb-1.5 flex justify-between gap-3 text-xs"><span className="font-semibold text-slate-700">{pretty(issue)}</span><span className="text-slate-500">{frameIssues.length ? t("chart.sampledFrames", { count }) : t("common.detected")}</span></div><div className="h-2.5 rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-orange-500" style={{ width: `${Math.max(12, count / max * 100)}%` }} /></div></div>)}</div>;
}

export function MovementRadarChart({ report }) {
  const { t } = useLocale();
  const shoulder = report.exercise === "shoulder_abduction";
  const hipAbduction = report.exercise === "hip_abduction";
  const primaryAngle = shoulder ? report.average_shoulder_angle : hipAbduction ? report.average_hip_abduction_angle : report.average_knee_angle;
  const secondaryValue = shoulder || hipAbduction ? (report.pose_quality?.critical_landmark_visibility || 0) * 100 : (report.average_hip_angle || 0) / 1.8;
  const values = [Math.max(0, Math.min(100, report.movement_score || 0)), Math.min(100, (primaryAngle || 0) / 1.8), Math.min(100, secondaryValue), Math.max(0, 100 - (report.average_trunk_angle || 0) / 0.9), Math.max(0, 100 - (report.detected_issues?.length || 0) * 20)];
  const labels = shoulder ? [t("chart.score"), t("chart.shoulder"), t("chart.visibility"), t("chart.trunk"), t("chart.issueLoad")] : hipAbduction ? [t("chart.score"), t("chart.hip"), t("chart.visibility"), t("chart.trunk"), t("chart.issueLoad")] : [t("chart.score"), t("chart.knee"), t("chart.hip"), t("chart.trunk"), t("chart.issueLoad")];
  const center = 120, radius = 78;
  const vertex = (index, scale = 1) => { const angle = -Math.PI / 2 + index * Math.PI * 2 / values.length; return [center + Math.cos(angle) * radius * scale, center + Math.sin(angle) * radius * scale]; };
  const polygon = values.map((value, index) => vertex(index, value / 100).join(",")).join(" ");
  return <div><svg viewBox="0 0 240 240" className="mx-auto h-60 w-full max-w-xs" role="img" aria-label={t("chart.profileAria")}><g fill="none" stroke="#dce6ee">{[.25, .5, .75, 1].map((scale) => <polygon key={scale} points={values.map((_, index) => vertex(index, scale).join(",")).join(" ")} />)}{values.map((_, index) => <line key={index} x1={center} y1={center} x2={vertex(index)[0]} y2={vertex(index)[1]} />)}</g><polygon points={polygon} fill="rgba(37,99,235,.18)" stroke="#2563eb" strokeWidth="2.5" />{labels.map((label, index) => { const [x, y] = vertex(index, 1.18); return <text key={label} x={x} y={y} textAnchor="middle" dominantBaseline="middle" fill="#64748b" fontSize="10">{label}</text>; })}</svg><p className="text-center text-[11px] leading-5 text-slate-500">{t("chart.normalized")}</p></div>;
}

export function RepQualityChart({ reps = [] }) {
  const { t } = useLocale();
  if (!reps.length) return <EmptyState compact title={t("chart.repPlanned")} description={t("chart.repHelp")} icon={ChartNoAxesColumnIncreasing} />;
  return <div className="flex h-44 items-end gap-3 rounded-xl bg-slate-50 p-4">{reps.map((rep, index) => <div key={rep.rep_index ?? index} className="flex flex-1 flex-col items-center gap-2"><div className="w-full rounded-t-lg bg-gradient-to-t from-clinical-blue to-clinical-teal" style={{ height: `${Math.max(8, rep.score || 0)}%` }} /><span className="text-[11px] font-semibold text-slate-500">{t("chart.rep", { count: index + 1 })}</span></div>)}</div>;
}

export function ChartCard({ title, description, children }) {
  return <Card className="p-5"><div className="mb-5"><h3 className="text-base font-bold text-clinical-ink">{title}</h3>{description && <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>}</div>{children}</Card>;
}
