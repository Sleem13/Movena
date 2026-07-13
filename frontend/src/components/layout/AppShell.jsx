import { Activity, BarChart3, HeartPulse, Info, UploadCloud } from "lucide-react";

const items = [
  { id: "home", label: "Home", icon: HeartPulse },
  { id: "analyze", label: "Analyze", icon: UploadCloud },
  { id: "results", label: "Results", icon: BarChart3, requiresReport: true },
  { id: "about", label: "About", icon: Info },
];

export function Navbar({ currentPage, hasReport, onNavigate }) {
  return <header className="sticky top-0 z-30 border-b border-clinical-line/80 bg-white/90 backdrop-blur-xl"><nav aria-label="Primary navigation" className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 sm:px-6"><button type="button" onClick={() => onNavigate("home")} className="flex items-center gap-3 py-3 text-left"><span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-clinical-blue to-clinical-teal text-white shadow-sm"><Activity size={21} aria-hidden="true" /></span><span><span className="block text-sm font-bold tracking-tight text-clinical-ink">PhysioVision AI</span><span className="hidden text-[11px] text-slate-500 sm:block">Movement intelligence</span></span></button><div className="flex items-center gap-1">{items.filter((item) => !item.requiresReport || hasReport).map(({ id, label, icon: Icon }) => <button key={id} type="button" onClick={() => onNavigate(id)} aria-current={currentPage === id ? "page" : undefined} className={`inline-flex min-h-10 items-center gap-2 rounded-xl px-3 text-sm font-medium transition ${currentPage === id ? "bg-blue-50 text-clinical-blue" : "text-slate-600 hover:bg-slate-100 hover:text-clinical-ink"}`}><Icon size={16} aria-hidden="true" /><span className="hidden sm:inline">{label}</span></button>)}</div></nav></header>;
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">{eyebrow}</p><h1 className="mt-2 text-3xl font-bold tracking-tight text-clinical-ink sm:text-4xl">{title}</h1>{description && <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">{description}</p>}</div>{actions && <div className="flex flex-wrap gap-3">{actions}</div>}</div>;
}

export default function AppShell({ currentPage, hasReport, onNavigate, children }) {
  return <div className="min-h-screen"><Navbar currentPage={currentPage} hasReport={hasReport} onNavigate={onNavigate} />{children}<footer className="mt-14 border-t border-clinical-line bg-white"><div className="mx-auto max-w-7xl px-6 py-6 text-xs leading-5 text-slate-500"><p className="font-semibold text-slate-600">PhysioVision AI · Educational movement support</p><p className="mt-1">This analysis is for exercise monitoring and educational support only. It does not replace assessment, diagnosis, or treatment by a licensed physiotherapist or healthcare professional.</p></div></footer></div>;
}
