import { useEffect, useRef, useState } from "react";
import {
  ArrowRight, BarChart3, ChevronRight, ClipboardList, Dumbbell,
  History, Home, LogIn, Menu, PanelLeftClose,
  PanelLeftOpen, Radio, ShieldCheck, UploadCloud, User,
  Users, X,
} from "lucide-react";

import BrandLogo from "../brand/BrandLogo.jsx";
import { ENABLE_REALTIME_COACHING_SPIKE } from "../../config/featureFlags.js";
import LanguageSelector from "../../i18n/LanguageSelector.jsx";
import ThemeSelector from "../../theme/ThemeSelector.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const workspaceSections = [
  { labelKey: "nav.workspace", items: [
    { id: "workspace", labelKey: "nav.overview", icon: Home },
    { id: "analyze", labelKey: "nav.analyzeMovement", icon: UploadCloud },
    { id: "history", labelKey: "nav.sessions", icon: ClipboardList },
    { id: "results", labelKey: "nav.results", icon: BarChart3, requiresReport: true },
  ] },
  { labelKey: "nav.care", items: [
    { id: "therapist", labelKey: "nav.patients", icon: Users, roles: ["therapist", "admin", "super_admin"] },
    { id: "exercises", labelKey: "nav.exercises", icon: Dumbbell },
  ] },
  { labelKey: "nav.tools", items: [
    { id: "admin", labelKey: "nav.admin", icon: ShieldCheck, roles: ["super_admin"] },
    { id: "coach", labelKey: "nav.coach", icon: Radio, featureEnabled: ENABLE_REALTIME_COACHING_SPIKE },
  ] },
];

const workspacePages = new Set(["workspace", "analyze", "history", "therapist", "exercises", "admin", "coach", "results", "profile"]);

function visibleItems(items, user, hasReport) {
  return items.filter((item) =>
    (!item.requiresReport || hasReport) &&
    (!item.requiresUser || user) &&
    item.featureEnabled !== false &&
    (!item.roles || item.roles.includes(user?.role)),
  );
}

function Brand({ compact = false, forceLabel = false, prominent = false, onClick }) {
  return <button onClick={onClick} className="group min-w-0 rounded-xl text-left transition hover:opacity-90" aria-label="PhysioVision AI home">
    <BrandLogo compact={compact} className={forceLabel ? "" : compact ? "" : "[&>span]:hidden sm:[&>span]:block"} markClassName={prominent ? "h-14 w-14 rounded-2xl" : compact ? "h-12 w-12" : ""} />
  </button>;
}

export function Navbar({ currentPage, hasReport, onNavigate, user }) {
  const { t } = useLocale();
  const landing = currentPage === "home";
  const accessPlatform = () => onNavigate(user ? "workspace" : "register");
  return <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur-xl">
    <nav aria-label="Primary navigation" className="mx-auto flex min-h-[5rem] max-w-[1400px] items-center justify-between gap-4 px-5 sm:px-8 lg:px-12">
      <Brand onClick={() => onNavigate("home")} />
      <div className="flex min-w-0 items-center gap-1.5">
        {landing ? <div className="hidden items-center gap-1 xl:flex">
          <a href="#how-it-works" className="rounded-lg px-3.5 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-clinical-sky hover:text-clinical-blue">{t("home.howNav")}</a>
          <a href="#benefits" className="rounded-lg px-3.5 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-clinical-sky hover:text-clinical-blue">{t("home.benefitsNav")}</a>
          <a href="#safety" className="rounded-lg px-3.5 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-clinical-sky hover:text-clinical-blue">{t("home.safetyNav")}</a>
        </div> : <button type="button" onClick={() => onNavigate("home")} className="hidden rounded-lg px-3.5 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-clinical-sky hover:text-clinical-blue sm:block">{t("nav.home")}</button>}
        <ThemeSelector />
        <LanguageSelector />
        <button aria-label={user ? t("nav.profile") : t("nav.login")} onClick={() => onNavigate(user ? "profile" : "login")} className="hidden min-h-11 shrink-0 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 text-sm font-bold text-clinical-ink transition hover:border-blue-200 hover:bg-clinical-sky xl:inline-flex">{user ? <User size={17} /> : <LogIn size={17} />}<span>{user ? t("nav.profile") : t("nav.login")}</span></button>
        <button type="button" onClick={accessPlatform} className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-xl bg-clinical-blue px-3.5 text-sm font-bold text-white shadow-[0_8px_20px_rgba(37,99,235,0.18)] transition hover:-translate-y-0.5 hover:bg-blue-700 sm:px-4">{t(user ? "home.openWorkspace" : "home.getStarted")}<ArrowRight className="hidden sm:block" size={16} /></button>
      </div>
    </nav>
  </header>;
}

function WorkspaceNav({ currentPage, hasReport, onNavigate, user, collapsed, closeMobile }) {
  const { t } = useLocale();
  return <nav className="mt-6 space-y-5" aria-label="Workspace navigation">
    {workspaceSections.map((section) => {
      const items = visibleItems(section.items, user, hasReport);
      if (!items.length) return null;
      return <div key={section.labelKey}>
        {!collapsed ? <p className="mb-2 px-3 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">{t(section.labelKey)}</p> : null}
        <div className="space-y-1">{items.map(({ id, labelKey, icon: Icon }) => {
          const active = currentPage === id;
          return <button key={id} onClick={() => { onNavigate(id); closeMobile?.(); }} aria-current={active ? "page" : undefined} title={collapsed ? t(labelKey) : undefined} className={`group relative flex min-h-11 w-full items-center gap-3 rounded-[11px] px-3 text-left text-sm font-semibold transition ${active ? "bg-blue-50 text-blue-700 shadow-[inset_0_0_0_1px_rgba(37,99,235,0.08)]" : "text-slate-600 hover:bg-slate-50 hover:text-[#071b4a]"}`}>
            {active ? <span className="absolute -left-3 top-2 h-7 w-1 rounded-r-full bg-blue-600" /> : null}
            <Icon size={19} strokeWidth={1.9} className="shrink-0" />
            {!collapsed ? <span className="truncate">{t(labelKey)}</span> : null}
          </button>;
        })}</div>
      </div>;
    })}
  </nav>;
}

function Sidebar({ currentPage, hasReport, onNavigate, user, collapsed, setCollapsed, mobileOpen, setMobileOpen, mobilePanelRef }) {
  const { t } = useLocale();
  const inner = <div className="flex h-full flex-col px-3.5 py-5">
    <div className={`flex items-center justify-between ${collapsed ? "px-0" : "px-1"}`}><Brand compact={collapsed && !mobileOpen} forceLabel={mobileOpen} prominent={!collapsed || mobileOpen} onClick={() => onNavigate("workspace")} />{mobileOpen ? <button className="grid h-10 w-10 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 lg:hidden" onClick={() => setMobileOpen(false)} aria-label={t("common.close")}><X size={20} /></button> : null}</div>
    <WorkspaceNav currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} collapsed={collapsed} closeMobile={() => setMobileOpen(false)} />
    <button onClick={() => setCollapsed((value) => !value)} className="mt-auto hidden min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-50 hover:text-[#071b4a] lg:flex" aria-label={collapsed ? t("nav.expand") : t("nav.collapse")}>
      {collapsed ? <PanelLeftOpen size={19} /> : <PanelLeftClose size={19} />}{!collapsed ? <span>{t("nav.collapse")}</span> : null}
    </button>
  </div>;
  return <>
    <aside className={`workspace-sidebar fixed inset-y-0 left-0 z-40 hidden border-r border-clinical-line bg-white transition-[width] duration-200 lg:block ${collapsed ? "w-[80px]" : "w-[252px]"}`}>{inner}</aside>
    {mobileOpen ? <div className="fixed inset-0 z-50 lg:hidden"><button className="absolute inset-0 bg-slate-950/35" aria-label={t("common.close")} onClick={() => setMobileOpen(false)} /><aside ref={mobilePanelRef} role="dialog" aria-modal="true" aria-label={t("nav.openMenu")} tabIndex={-1} className="workspace-mobile-sidebar absolute inset-y-0 left-0 w-[min(86vw,320px)] border-r border-slate-200 bg-white shadow-2xl">{inner}</aside></div> : null}
  </>;
}

function WorkspaceTopbar({ user, onNavigate, onOpenMenu }) {
  const { t } = useLocale();
  const displayName = user?.full_name || user?.email?.split("@")[0] || t("profile.developmentUser");
  const initials = displayName.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  return <header className="sticky top-0 z-30 flex h-[68px] items-center justify-between border-b border-clinical-line bg-white/95 px-4 backdrop-blur-xl sm:px-6">
    <button className="grid h-11 w-11 place-items-center rounded-xl text-slate-600 hover:bg-slate-100 lg:hidden" onClick={onOpenMenu} aria-label={t("nav.openMenu")}><Menu size={22} /></button>
    <div className="hidden lg:block" />
    <div className="flex items-center gap-2 sm:gap-3"><ThemeSelector /><LanguageSelector /><span className="hidden h-7 w-px bg-slate-200 sm:block" /><button onClick={() => onNavigate("profile")} className="flex min-h-11 items-center gap-2.5 rounded-xl px-2 text-sm text-[#071b4a] transition hover:bg-slate-50"><span className="grid h-9 w-9 place-items-center rounded-full bg-[#071b4a] text-xs font-bold tracking-wide text-white">{initials || <User size={18} />}</span><span className="hidden max-w-44 text-left sm:block"><span className="block truncate font-semibold leading-4">{displayName}</span><span className="mt-0.5 block text-[11px] font-medium text-slate-500">{user?.role ? user.role.replaceAll("_", " ") : t("nav.profile")}</span></span><ChevronRight className="hidden text-slate-400 sm:block rtl:rotate-180" size={16} /></button></div>
  </header>;
}

function MobileWorkspaceNav({ currentPage, onNavigate }) {
  const { t } = useLocale();
  const items = [
    ["workspace", t("nav.overview"), Home], ["analyze", t("nav.analyze"), UploadCloud],
    ["history", t("nav.sessions"), History],
  ];
  return <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-3 border-t border-slate-200 bg-white/95 px-4 pb-[max(.5rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur-xl lg:hidden" aria-label="Mobile workspace navigation">
    {items.map(([id, label, Icon]) => <button key={id} onClick={() => onNavigate(id)} aria-current={currentPage === id ? "page" : undefined} className={`flex min-h-12 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-bold ${currentPage === id ? "text-blue-700" : "text-slate-500"}`}><Icon size={19} /><span>{label}</span></button>)}
  </nav>;
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return <div className="mb-7 flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between"><div>{eyebrow ? <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-teal-700">{eyebrow}</p> : null}<h1 className="text-balance text-[1.75rem] font-bold leading-tight tracking-[-0.025em] text-[#071b4a] sm:text-[2rem]">{title}</h1>{description ? <p className="mt-2.5 max-w-3xl text-sm leading-6 text-slate-600 sm:text-[15px]">{description}</p> : null}</div>{actions ? <div className="shrink-0">{actions}</div> : null}</div>;
}

export default function AppShell({ currentPage, hasReport, onNavigate, user, children }) {
  const { t } = useLocale();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const mobilePanelRef = useRef(null);
  const workspace = Boolean(user) && workspacePages.has(currentPage);
  useEffect(() => {
    if (!mobileOpen) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    mobilePanelRef.current?.focus();
    function handleKeyDown(event) {
      if (event.key === "Escape") setMobileOpen(false);
      if (event.key !== "Tab") return;
      const focusable = [...(mobilePanelRef.current?.querySelectorAll('button:not([disabled]), a[href], select:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])') || [])];
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => { document.body.style.overflow = previousOverflow; document.removeEventListener("keydown", handleKeyDown); };
  }, [mobileOpen]);
  if (workspace) return <div className={`workspace min-h-screen bg-clinical-panel text-[#071b4a] ${collapsed ? "lg:pl-[80px]" : "lg:pl-[252px]"}`}>
    <Sidebar currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} collapsed={collapsed} setCollapsed={setCollapsed} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} mobilePanelRef={mobilePanelRef} />
    <div className="min-w-0"><WorkspaceTopbar user={user} onNavigate={onNavigate} onOpenMenu={() => setMobileOpen(true)} /><div key={currentPage} className="app-page pb-24 lg:pb-0">{children}</div></div>
    <MobileWorkspaceNav currentPage={currentPage} onNavigate={onNavigate} />
  </div>;
  return <div className="flex min-h-screen flex-col bg-white"><Navbar currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} /><div key={currentPage} className="app-page flex-1">{children}</div><footer className="mt-auto border-t border-slate-200 bg-white"><div className="mx-auto flex max-w-[1400px] flex-col gap-5 px-5 py-8 sm:px-8 md:flex-row md:items-center md:justify-between lg:px-12"><BrandLogo markClassName="h-9 w-9 rounded-[11px]" /><p className="max-w-2xl text-xs leading-5 text-slate-500 md:text-right rtl:md:text-left">{t("footer.disclaimer")}</p></div></footer></div>;
}
