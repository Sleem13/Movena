import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

export function Button({ as: Component = "button", variant = "primary", className = "", children, ...props }) {
  const styles = {
    primary: "bg-clinical-blue text-white hover:bg-blue-700 active:scale-[0.98]",
    secondary: "border border-clinical-line bg-white text-clinical-ink shadow-sm hover:border-blue-300 hover:bg-clinical-sky active:scale-[0.98]",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-clinical-ink",
  };
  return <Component data-variant={variant} className={`ui-button inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition duration-150 ease-out disabled:scale-100 disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`} {...props}>{children}</Component>;
}

export function Card({ as: Component = "section", className = "", children, ...props }) {
  return <Component className={`surface-card min-w-0 rounded-lg border border-clinical-line bg-white ${className}`} {...props}>{children}</Component>;
}

export function Badge({ tone = "blue", children, className = "" }) {
  const tones = { blue: "bg-blue-50 text-blue-700 ring-blue-100", teal: "bg-teal-50 text-teal-700 ring-teal-100", amber: "bg-amber-50 text-amber-800 ring-amber-200", slate: "bg-slate-100 text-slate-700 ring-slate-200", red: "bg-red-50 text-red-700 ring-red-100" };
  return <span data-tone={tone} className={`ui-badge inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${tones[tone]} ${className}`}>{children}</span>;
}

export function Alert({ title, children, tone = "error", className = "" }) {
  const tones = tone === "warning" ? "border-amber-200 bg-amber-50 text-amber-950" : tone === "info" ? "border-blue-200 bg-blue-50 text-blue-950" : tone === "success" ? "border-teal-200 bg-teal-50 text-teal-950" : "border-red-200 bg-red-50 text-red-800";
  return <div role={tone === "error" ? "alert" : undefined} className={`flex gap-3 rounded-xl border px-4 py-3 text-sm leading-6 ${tones} ${className}`}><AlertCircle className="mt-0.5 shrink-0" size={18} aria-hidden="true" /><div>{title && <p className="font-semibold">{title}</p>}<div className={title ? "mt-1" : ""}>{children}</div></div></div>;
}

export function LoadingSpinner({ label = "Loading" }) {
  return <span className="inline-flex items-center gap-2"><LoaderCircle className="animate-spin" size={18} aria-hidden="true" /><span>{label}</span></span>;
}

export function EmptyState({ title, description, icon: Icon = Inbox, compact = false, actions }) {
  return <div className={`flex flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-300 bg-white text-center ${compact ? "p-5" : "px-6 py-10"}`}><span className="mb-3 grid h-11 w-11 place-items-center rounded-xl bg-clinical-sky text-blue-600 ring-1 ring-blue-100"><Icon size={20} aria-hidden="true" /></span><p className="text-sm font-semibold text-clinical-ink">{title}</p>{description && <p className="mt-1 max-w-md text-xs leading-5 text-slate-500">{description}</p>}{actions ? <div className="mt-5 flex flex-wrap justify-center gap-2">{actions}</div> : null}</div>;
}
