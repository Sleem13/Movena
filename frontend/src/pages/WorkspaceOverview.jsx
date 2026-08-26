import { useEffect, useState } from "react";
import { Activity, AlertCircle, CheckCircle2, ChevronRight, Download, MailCheck, Play, RefreshCw, ScanSearch, ShieldCheck, UploadCloud, UserRound, Video } from "lucide-react";

import { Button, LoadingSpinner } from "../components/common/UI.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { listSavedSessions } from "../services/api.js";

function formatSessionDate(value, locale) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(locale, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function statusPresentation(status) {
  if (status === "success") return { label: "Completed", Icon: CheckCircle2, className: "text-emerald-700" };
  if (status === "rejected") return { label: "Needs attention", Icon: AlertCircle, className: "text-amber-700" };
  return { label: "Review ready", Icon: CheckCircle2, className: "text-emerald-700" };
}

export default function WorkspaceOverview({ onNavigate }) {
  const { user } = useAuth();
  const { locale, t, exerciseText, pretty } = useLocale();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const rawDisplayName = user?.full_name || user?.username || user?.email?.split("@")[0] || "there";
  const displayName = rawDisplayName.charAt(0).toUpperCase() + rawDisplayName.slice(1).split(" ")[0];

  async function load() {
    setLoading(true); setError("");
    try { const data = await listSavedSessions({ limit: 3 }); setSessions(data.items || []); }
    catch (requestError) { setError(requestError.response?.data?.message || t("history.loadError")); }
    finally { setLoading(false); }
  }
  useEffect(() => { load(); }, []);

  const workflow = [[UploadCloud,t("workspace.stepUpload"),t("workspace.stepUploadHelp")],[Activity,t("workspace.stepAnalyze"),t("workspace.stepAnalyzeHelp")],[ScanSearch,t("workspace.stepReview"),t("workspace.stepReviewHelp")],[Download,t("workspace.stepSave"),t("workspace.stepSaveHelp")],[UserRound,t("workspace.stepPatient"),t("workspace.stepPatientHelp")]];

  return <main>
    <div><h1 className="text-3xl font-bold tracking-[-0.03em] text-[#071b4a] sm:text-4xl">{t("workspace.greeting", { name: displayName })}</h1><p className="mt-2.5 text-[15px] text-slate-600 sm:text-base">{t("workspace.subtitle")}</p><div className="mt-5 flex flex-wrap gap-3"><Button onClick={() => onNavigate("analyze")} className="min-h-11 px-5"><Play size={18} />{t("nav.analyzeMovement")}</Button><Button onClick={() => onNavigate("history")} variant="secondary" className="min-h-11 px-5"><Video size={18} />{t("workspace.viewSessions")}</Button></div></div>

    {error ? <div className="mt-7 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}<button onClick={load} className="ms-3 font-bold underline">{t("common.refresh")}</button></div> : null}
    <div className="mt-8 grid gap-5 xl:grid-cols-[minmax(0,1fr)_355px]">
      <section className="overflow-hidden rounded-xl border border-[#dce3ee] bg-white" aria-labelledby="recent-sessions-heading">
        <div className="flex items-center justify-between px-5 py-5"><h2 id="recent-sessions-heading" className="text-xl font-extrabold tracking-[-0.02em] text-[#071b4a]">{t("workspace.recentSessions")}</h2><button onClick={load} className="grid h-10 w-10 place-items-center rounded-lg text-slate-500 hover:bg-slate-100" aria-label={t("common.refresh")}><RefreshCw size={17} /></button></div>
        {loading ? <div className="grid min-h-64 place-items-center border-t border-slate-200"><LoadingSpinner label={t("history.loading")} /></div> : sessions.length ? <div className="overflow-x-auto"><table className="w-full min-w-[640px] text-left rtl:text-right"><thead><tr className="border-y border-slate-200 text-sm font-semibold text-slate-500"><th className="px-5 py-3">{t("workspace.patient")}</th><th className="px-5 py-3">{t("common.exercise")}</th><th className="px-5 py-3">{t("workspace.recorded")}</th><th className="px-5 py-3">{t("common.status")}</th><th className="w-12" /></tr></thead><tbody>{sessions.map((session) => { const state = statusPresentation(session.status); const StatusIcon = state.Icon; const exerciseId = session.exercise_id || session.exercise; return <tr key={session.session_id} className="border-b border-slate-200 text-sm transition last:border-0 hover:bg-slate-50"><td className="px-5 py-4 font-semibold text-[#071b4a]"><span className="inline-flex items-center gap-2"><UserRound size={17} className="text-slate-400" />{session.patient_id ? t("workspace.assignedPatient") : (user?.full_name || t("workspace.personalSession"))}</span></td><td className="px-5 py-4 text-slate-700">{exerciseId ? exerciseText(exerciseId).name : session.exercise_display_name}</td><td className="px-5 py-4 text-slate-600">{formatSessionDate(session.created_at, locale)}</td><td className={`px-5 py-4 font-semibold ${state.className}`}><span className="inline-flex items-center gap-2"><StatusIcon size={18} />{session.status ? pretty(state.label) : state.label}</span></td><td className="px-3"><button onClick={() => onNavigate("history")} className="grid h-10 w-10 place-items-center rounded-lg text-slate-400 hover:bg-blue-50 hover:text-blue-700" aria-label={t("history.viewDetails")}><ChevronRight size={18} className="rtl:rotate-180" /></button></td></tr>; })}</tbody></table></div> : <div className="grid min-h-64 place-items-center border-t border-slate-200 p-8 text-center"><div><UploadCloud className="mx-auto text-slate-300" size={32} /><p className="mt-3 font-bold text-[#071b4a]">{t("history.emptyTitle")}</p><p className="mt-2 text-sm text-slate-500">{t("history.emptyDescription")}</p></div></div>}
        {sessions.length ? <div className="border-t border-slate-200 px-5 py-4"><button onClick={() => onNavigate("history")} className="inline-flex min-h-10 items-center gap-2 text-sm font-bold text-blue-700 hover:text-blue-800">{t("workspace.viewAllSessions")}<ChevronRight size={16} className="rtl:rotate-180" /></button></div> : null}
      </section>

      <aside className="rounded-xl border border-[#dce3ee] bg-white p-6" aria-labelledby="workspace-status-heading"><h2 id="workspace-status-heading" className="text-xl font-extrabold tracking-[-0.02em] text-[#071b4a]">{t("workspace.status")}</h2><div className="mt-4 divide-y divide-slate-200">{[[MailCheck, t("workspace.accountAccess")],[ShieldCheck, user?.role === "super_admin" ? t("workspace.protectedAdmin") : t("workspace.role", { role: pretty(user?.role) })],[Activity, t("workspace.analysisReady")]].map(([Icon, label]) => <div key={label} className="flex min-h-[76px] items-center gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-emerald-50 text-emerald-700"><Icon size={21} /></span><span className="text-sm font-semibold text-slate-700">{label}</span></div>)}</div><button onClick={() => onNavigate("profile")} className="mt-4 inline-flex min-h-10 items-center gap-2 text-sm font-bold text-blue-700 hover:text-blue-800">{t("workspace.viewSecurity")}<ChevronRight size={16} className="rtl:rotate-180" /></button></aside>
    </div>

    <section className="mt-5 rounded-xl border border-[#dce3ee] bg-white px-5 py-5 sm:px-6" aria-labelledby="workflow-heading"><h2 id="workflow-heading" className="text-lg font-bold tracking-[-0.02em] text-[#071b4a]">{t("workspace.continueWorkflow")}</h2><div className="mt-5 grid gap-5 sm:grid-cols-2 xl:grid-cols-5">{workflow.map(([Icon,title,description],index)=><div key={title} className="relative flex gap-3 xl:block"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700"><Icon size={19} /></span><div className="xl:mt-3"><p className="text-sm font-semibold text-[#071b4a]"><span className="me-1.5 text-xs text-blue-600">{index+1}.</span>{title}</p><p className="mt-1.5 text-xs leading-5 text-slate-500">{description}</p></div></div>)}</div></section>
  </main>;
}
