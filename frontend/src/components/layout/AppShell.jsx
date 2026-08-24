import {
  Activity,
  BarChart3,
  HeartPulse,
  History,
  Info,
  Library,
  LogIn,
  Radio,
  Stethoscope,
  UploadCloud,
  User,
  ShieldCheck,
} from "lucide-react";
import { ENABLE_REALTIME_COACHING_SPIKE } from "../../config/featureFlags.js";
import LanguageSelector from "../../i18n/LanguageSelector.jsx";
import { useLocale } from "../../i18n/LocaleContext.jsx";

const items = [
  { id: "home", labelKey: "nav.home", icon: HeartPulse },
  { id: "exercises", labelKey: "nav.exercises", icon: Library },
  { id: "analyze", labelKey: "nav.analyze", icon: UploadCloud },
  { id: "results", labelKey: "nav.results", icon: BarChart3, requiresReport: true },
  { id: "history", labelKey: "nav.history", icon: History, requiresUser: true },
  {
    id: "therapist",
    labelKey: "nav.therapist",
    icon: Stethoscope,
    roles: ["therapist", "admin", "super_admin"],
  },
  { id: "admin", labelKey: "nav.admin", icon: ShieldCheck, roles: ["super_admin"] },
  {
    id: "coach",
    labelKey: "nav.coach",
    icon: Radio,
    featureEnabled: ENABLE_REALTIME_COACHING_SPIKE,
  },
  { id: "about", labelKey: "nav.about", icon: Info },
];

export function Navbar({ currentPage, hasReport, onNavigate, user }) {
  const { t } = useLocale();
  const visible = items.filter(
    (i) =>
      (!i.requiresReport || hasReport) &&
      (!i.requiresUser || user) &&
      (i.featureEnabled !== false) &&
      (!i.roles || i.roles.includes(user?.role)),
  );

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 shadow-[0_1px_12px_rgba(31,62,89,0.04)] backdrop-blur-xl">
      <nav
        aria-label="Primary navigation"
        className="mx-auto flex min-h-[4.5rem] max-w-7xl items-center justify-between gap-4 px-4 sm:px-6"
      >
        <button
          onClick={() => onNavigate("home")}
          className="group flex shrink-0 items-center gap-3 rounded-xl text-left"
          aria-label="PhysioVision AI home"
        >
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-gradient-to-br from-clinical-blue to-clinical-teal text-white shadow-sm transition group-hover:scale-105">
            <Activity size={20} />
          </span>
          <span>
            <span className="block text-sm font-extrabold tracking-tight text-clinical-ink sm:text-base">PhysioVision AI</span>
            <span className="hidden text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400 sm:block">
              {t("brand.tagline")}
            </span>
          </span>
        </button>
        <div className="flex min-w-0 items-center gap-1 overflow-x-auto py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {visible.map(({ id, labelKey, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              aria-label={t(labelKey)}
              aria-current={currentPage === id ? "page" : undefined}
              className={`nav-item relative inline-flex min-h-10 shrink-0 items-center gap-2 rounded-xl px-3 text-sm font-semibold transition duration-200 ${
                currentPage === id
                  ? "nav-item-active bg-blue-50 text-clinical-blue shadow-sm ring-1 ring-blue-100"
                  : "text-slate-500 hover:bg-slate-50 hover:text-clinical-ink"
              }`}
            >
              <Icon size={16} aria-hidden="true" />
              <span className="hidden lg:inline">{t(labelKey)}</span>
            </button>
          ))}
          <LanguageSelector />
          <button
            aria-label={user ? t("nav.profile") : t("nav.login")}
            onClick={() => onNavigate(user ? "profile" : "login")}
            className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl transition ${
              currentPage === "profile" || currentPage === "login" || currentPage === "register"
                ? "bg-clinical-ink text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {user ? <User size={16} /> : <LogIn size={16} />}
          </button>
        </div>
      </nav>
    </header>
  );
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="page-header mb-8 flex flex-col gap-5 border-b border-slate-200/80 pb-7 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal before:h-px before:w-6 before:bg-clinical-teal">
          {eyebrow}
        </p>
        <h1 className="mt-3 text-balance text-3xl font-extrabold tracking-tight text-clinical-ink sm:text-4xl">{title}</h1>
        {description && (
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">{description}</p>
        )}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
}

export default function AppShell({
  currentPage,
  hasReport,
  onNavigate,
  user,
  children,
}) {
  const { t } = useLocale();

  return (
    <div className="min-h-screen">
      <Navbar
        currentPage={currentPage}
        hasReport={hasReport}
        onNavigate={onNavigate}
        user={user}
      />
      <div key={currentPage} className="app-page">{children}</div>
      <footer className="mt-16 border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-8 text-xs leading-5 text-slate-500 sm:flex sm:items-center sm:justify-between">
          <p className="font-semibold">{t("footer.product")}</p>
          <p>{t("footer.disclaimer")}</p>
        </div>
      </footer>
    </div>
  );
}
