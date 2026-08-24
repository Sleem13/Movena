import { useEffect, useRef, useState } from "react";
import {
  Accessibility, BarChart3, ChevronRight, ClipboardList, Dumbbell,
  HeartPulse, History, Home, Info, Library, LogIn, Menu, PanelLeftClose,
  PanelLeftOpen, Radio, ShieldCheck, UploadCloud, User,
  Users, X,
} from "lucide-react";

import { ENABLE_REALTIME_COACHING_SPIKE } from "../../config/featureFlags.js";
import LanguageSelector from "../../i18n/LanguageSelector.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const publicItems = [
  { id: "home", labelKey: "nav.home", icon: HeartPulse },
  { id: "exercises", labelKey: "nav.exercises", icon: Library },
  { id: "about", labelKey: "nav.about", icon: Info },
];

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

function Brand({ compact = false, forceLabel = false, onClick }) {
  return <button onClick={onClick} className="group flex min-w-0 items-center gap-3 rounded-xl text-left" aria-label="PhysioVision AI home">
    <span className="grid h-10 w-10 shrink-0 place-items-center text-cyan-600 transition group-hover:text-blue-700"><Accessibility size={33} strokeWidth={2.3} /></span>
    {!compact ? <span className={`${forceLabel ? "block" : "hidden sm:block"} truncate text-[19px] font-extrabold tracking-[-0.035em] text-[#071b4a]`}>PhysioVision AI</span> : null}
  </button>;
}

export function Navbar({ currentPage, hasReport, onNavigate, user }) {
  const { t } = useLocale();
  const visible = visibleItems(publicItems, user, hasReport);
  return <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
    <nav aria-label="Primary navigation" className="mx-auto flex min-h-[4.5rem] max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
      <Brand onClick={() => onNavigate("home")} />
      <div className="flex min-w-0 items-center gap-1 overflow-x-auto py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {visible.map(({ id, labelKey, icon: Icon }) => <button key={id} onClick={() => onNavigate(id)} aria-label={t(labelKey)} aria-current={currentPage === id ? "page" : undefined} className={`relative hidden min-h-11 shrink-0 items-center gap-2 rounded-xl px-3 text-sm font-semibold transition sm:inline-flex ${currentPage === id ? "bg-blue-50 text-blue-700" : "text-slate-500 hover:bg-slate-50 hover:text-[#071b4a]"}`}><Icon size={17} /><span className="hidden lg:inline">{t(labelKey)}</span></button>)}
        {user ? <button aria-label={t("nav.workspace")} onClick={() => onNavigate("workspace")} className="inline-flex h-11 w-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 text-sm font-bold text-white transition hover:bg-blue-700 sm:w-auto sm:px-4"><Home size={17} /><span className="hidden sm:inline">{t("nav.workspace")}</span></button> : null}
        <LanguageSelector />
        <button aria-label={user ? t("nav.profile") : t("nav.login")} onClick={() => onNavigate(user ? "profile" : "login")} className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl transition ${["profile", "login", "register"].includes(currentPage) ? "bg-[#071b4a] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>{user ? <User size={17} /> : <LogIn size={17} />}</button>
      </div>
    </nav>
  </header>;
}

function WorkspaceNav({ currentPage, hasReport, onNavigate, user, collapsed, closeMobile }) {
  const { t } = useLocale();
  return <nav className="mt-7 space-y-6" aria-label="Workspace navigation">
    {workspaceSections.map((section) => {
      const items = visibleItems(section.items, user, hasReport);
      if (!items.length) return null;
      return <div key={section.labelKey}>
        {!collapsed ? <p className="mb-2 px-3 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">{t(section.labelKey)}</p> : null}
        <div className="space-y-1">{items.map(({ id, labelKey, icon: Icon }) => {
          const active = currentPage === id;
          return <button key={id} onClick={() => { onNavigate(id); closeMobile?.(); }} aria-current={active ? "page" : undefined} title={collapsed ? t(labelKey) : undefined} className={`group relative flex min-h-12 w-full items-center gap-3 rounded-xl px-3 text-left text-[15px] font-semibold transition ${active ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-50 hover:text-[#071b4a]"}`}>
            {active ? <span className="absolute -left-3 top-2 h-8 w-1 rounded-r-full bg-blue-600" /> : null}
            <Icon size={20} strokeWidth={1.9} className="shrink-0" />
            {!collapsed ? <span className="truncate">{t(labelKey)}</span> : null}
          </button>;
        })}</div>
      </div>;
    })}
  </nav>;
}

function Sidebar({ currentPage, hasReport, onNavigate, user, collapsed, setCollapsed, mobileOpen, setMobileOpen, mobilePanelRef }) {
  const { t } = useLocale();
  const inner = <div className="flex h-full flex-col px-3 py-5">
    <div className="flex items-center justify-between px-1"><Brand compact={collapsed} forceLabel={mobileOpen} onClick={() => onNavigate("workspace")} />{mobileOpen ? <button className="grid h-10 w-10 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 lg:hidden" onClick={() => setMobileOpen(false)} aria-label={t("common.close")}><X size={20} /></button> : null}</div>
    <WorkspaceNav currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} collapsed={collapsed} closeMobile={() => setMobileOpen(false)} />
    <button onClick={() => setCollapsed((value) => !value)} className="mt-auto hidden min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-50 hover:text-[#071b4a] lg:flex" aria-label={collapsed ? t("nav.expand") : t("nav.collapse")}>
      {collapsed ? <PanelLeftOpen size={19} /> : <PanelLeftClose size={19} />}{!collapsed ? <span>{t("nav.collapse")}</span> : null}
    </button>
  </div>;
  return <>
    <aside className={`workspace-sidebar fixed inset-y-0 left-0 z-40 hidden border-r border-slate-200 bg-white transition-[width] duration-200 lg:block ${collapsed ? "w-[84px]" : "w-[272px]"}`}>{inner}</aside>
    {mobileOpen ? <div className="fixed inset-0 z-50 lg:hidden"><button className="absolute inset-0 bg-slate-950/35" aria-label={t("common.close")} onClick={() => setMobileOpen(false)} /><aside ref={mobilePanelRef} role="dialog" aria-modal="true" aria-label={t("nav.openMenu")} tabIndex={-1} className="workspace-mobile-sidebar absolute inset-y-0 left-0 w-[min(86vw,320px)] border-r border-slate-200 bg-white shadow-2xl">{inner}</aside></div> : null}
  </>;
}

function WorkspaceTopbar({ user, onNavigate, onOpenMenu }) {
  const { t } = useLocale();
  const displayName = user?.email?.split("@")[0] || user?.full_name || t("profile.developmentUser");
  return <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-xl sm:px-7">
    <button className="grid h-11 w-11 place-items-center rounded-xl text-slate-600 hover:bg-slate-100 lg:hidden" onClick={onOpenMenu} aria-label={t("nav.openMenu")}><Menu size={22} /></button>
    <div className="hidden lg:block" />
    <div className="flex items-center gap-2 sm:gap-4"><LanguageSelector /><span className="hidden h-8 w-px bg-slate-200 sm:block" /><button onClick={() => onNavigate("profile")} className="flex min-h-11 items-center gap-2 rounded-xl px-2 text-sm font-semibold text-[#071b4a] transition hover:bg-slate-50"><span className="grid h-9 w-9 place-items-center rounded-full bg-[#071b4a] text-white"><User size={18} /></span><span className="hidden max-w-36 truncate sm:block">{displayName}</span><ChevronRight className="hidden text-slate-400 sm:block rtl:rotate-180" size={16} /></button></div>
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
  return <div className="mb-8 flex flex-col gap-5 border-b border-slate-200 pb-7 lg:flex-row lg:items-end lg:justify-between"><div>{eyebrow ? <p className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-teal-700">{eyebrow}</p> : null}<h1 className="text-balance text-3xl font-extrabold tracking-[-0.025em] text-[#071b4a] sm:text-[2.5rem] sm:leading-tight">{title}</h1>{description ? <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">{description}</p> : null}</div>{actions ? <div>{actions}</div> : null}</div>;
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
  if (workspace) return <div className={`workspace min-h-screen bg-white text-[#071b4a] ${collapsed ? "lg:pl-[84px]" : "lg:pl-[272px]"}`}>
    <Sidebar currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} collapsed={collapsed} setCollapsed={setCollapsed} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} mobilePanelRef={mobilePanelRef} />
    <div className="min-w-0"><WorkspaceTopbar user={user} onNavigate={onNavigate} onOpenMenu={() => setMobileOpen(true)} /><div key={currentPage} className="app-page pb-24 lg:pb-0">{children}</div></div>
    <MobileWorkspaceNav currentPage={currentPage} onNavigate={onNavigate} />
  </div>;
  return <div className="min-h-screen"><Navbar currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} user={user} /><div key={currentPage} className="app-page">{children}</div><footer className="mt-16 border-t border-slate-200 bg-white"><div className="mx-auto max-w-7xl px-6 py-8 text-xs leading-5 text-slate-500 sm:flex sm:items-center sm:justify-between"><p className="font-semibold">{t("footer.product")}</p><p>{t("footer.disclaimer")}</p></div></footer></div>;
}
