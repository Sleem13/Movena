import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

export function Button({ as: Component = "button", variant = "primary", className = "", children, ...props }) {
  const styles = {
    primary: "bg-clinical-blue text-white hover:bg-blue-700 shadow-sm",
    secondary: "border border-clinical-line bg-white text-clinical-ink hover:border-blue-300 hover:bg-blue-50",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-clinical-ink",
  };
  return <Component className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`} {...props}>{children}</Component>;
}

export function Card({ as: Component = "section", className = "", children, ...props }) {
  return <Component className={`rounded-2xl border border-clinical-line bg-white shadow-panel ${className}`} {...props}>{children}</Component>;
}

export function Badge({ tone = "blue", children, className = "" }) {
  const tones = { blue: "bg-blue-50 text-blue-700 ring-blue-100", teal: "bg-teal-50 text-teal-700 ring-teal-100", amber: "bg-amber-50 text-amber-800 ring-amber-200", slate: "bg-slate-100 text-slate-700 ring-slate-200", red: "bg-red-50 text-red-700 ring-red-100" };
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${tones[tone]} ${className}`}>{children}</span>;
}

export function Alert({ title, children, tone = "error" }) {
  const tones = tone === "warning" ? "border-amber-200 bg-amber-50 text-amber-950" : "border-red-200 bg-red-50 text-red-800";
  return <div role={tone === "error" ? "alert" : undefined} className={`flex gap-3 rounded-xl border p-4 text-sm ${tones}`}><AlertCircle className="mt-0.5 shrink-0" size={18} aria-hidden="true" /><div>{title && <p className="font-semibold">{title}</p>}<div className={title ? "mt-1" : ""}>{children}</div></div></div>;
}

export function LoadingSpinner({ label = "Loading" }) {
  return <span className="inline-flex items-center gap-2"><LoaderCircle className="animate-spin" size={18} aria-hidden="true" /><span>{label}</span></span>;
}

export function EmptyState({ title, description, icon: Icon = Inbox, compact = false }) {
  return <div className={`flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 text-center ${compact ? "p-5" : "p-8"}`}><span className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-white text-slate-400 shadow-sm"><Icon size={20} aria-hidden="true" /></span><p className="text-sm font-semibold text-slate-700">{title}</p>{description && <p className="mt-1 max-w-md text-xs leading-5 text-slate-500">{description}</p>}</div>;
}
