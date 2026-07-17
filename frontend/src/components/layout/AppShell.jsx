import {
  Activity,
  BarChart3,
  HeartPulse,
  History,
  Info,
  LogIn,
  Stethoscope,
  UploadCloud,
  User,
} from "lucide-react";
const items = [
  { id: "home", label: "Home", icon: HeartPulse },
  { id: "analyze", label: "Analyze", icon: UploadCloud },
  { id: "results", label: "Results", icon: BarChart3, requiresReport: true },
  { id: "history", label: "History", icon: History, requiresUser: true },
  {
    id: "therapist",
    label: "Therapist",
    icon: Stethoscope,
    roles: ["therapist", "admin"],
  },
  { id: "about", label: "About", icon: Info },
];
export function Navbar({ currentPage, hasReport, onNavigate, user }) {
  const visible = items.filter(
    (i) =>
      (!i.requiresReport || hasReport) &&
      (!i.requiresUser || user) &&
      (!i.roles || i.roles.includes(user?.role)),
  );
  return (
    <header className="sticky top-0 z-30 border-b bg-white/90">
      <nav
        aria-label="Primary navigation"
        className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-4"
      >
        <button
          onClick={() => onNavigate("home")}
          className="flex items-center gap-2 font-bold"
        >
          <Activity size={21} />
          PhysioVision AI
        </button>
        <div className="flex items-center gap-1">
          {visible.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              aria-current={currentPage === id ? "page" : undefined}
              className="rounded-xl px-3 py-2 text-sm"
            >
              <Icon size={16} className="inline" />{" "}
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
          <button
            aria-label={user ? "Profile" : "Log in"}
            onClick={() => onNavigate(user ? "profile" : "login")}
            className="rounded-xl px-3 py-2"
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
    <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">
          {eyebrow}
        </p>
        <h1 className="mt-2 text-3xl font-bold">{title}</h1>
        {description && (
          <p className="mt-3 max-w-2xl text-slate-600">{description}</p>
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
  return (
    <div className="min-h-screen">
      <Navbar
        currentPage={currentPage}
        hasReport={hasReport}
        onNavigate={onNavigate}
        user={user}
      />
      {children}
      <footer className="mt-14 border-t bg-white">
        <div className="mx-auto max-w-7xl px-6 py-6 text-xs text-slate-500">
          <p className="font-semibold">
            PhysioVision AI · Educational movement support
          </p>
          <p>
            This analysis does not replace assessment, diagnosis, or treatment
            by a licensed professional.
          </p>
        </div>
      </footer>
    </div>
  );
}
