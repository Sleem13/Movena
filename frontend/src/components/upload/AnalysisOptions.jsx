import { BrainCircuit, ChartNoAxesCombined, FileText, ScanSearch } from "lucide-react";
import { Card, Badge } from "../common/UI.jsx";

const options = [
  { key: "include_overlay", title: "Annotated video", description: "Draw a pose overlay for movement review.", icon: ScanSearch },
  { key: "generate_report", title: "PDF session report", description: "Create a temporary downloadable report.", icon: FileText },
  { key: "include_frame_data", title: "Angle trend data", description: "Include sampled frame-level angles for charts.", icon: ChartNoAxesCombined },
  { key: "include_ml", title: "ML second opinion", description: "Add the optional experimental baseline output.", icon: BrainCircuit, experimental: true },
];

export default function AnalysisOptions({ value, onChange, disabled }) {
  return <Card className="p-5"><div className="mb-4"><h2 className="text-base font-bold text-clinical-ink">Analysis options</h2><p className="mt-1 text-xs leading-5 text-slate-500">Choose optional artifacts and detail. The rule-based analysis always runs.</p></div><div className="grid gap-2 sm:grid-cols-2">{options.map(({ key, title, description, icon: Icon, experimental }) => <label key={key} className={`flex cursor-pointer gap-3 rounded-xl border p-3.5 transition ${value[key] ? "border-blue-200 bg-blue-50/70" : "border-slate-200 hover:border-slate-300"}`}><input aria-label={title} type="checkbox" className="mt-1 h-4 w-4 accent-blue-600" checked={value[key]} disabled={disabled} onChange={(event) => onChange({ ...value, [key]: event.target.checked })} /><Icon className="mt-0.5 shrink-0 text-clinical-blue" size={18} aria-hidden="true" /><span><span className="flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-800">{title}{experimental && <Badge tone="amber">Experimental</Badge>}</span><span className="mt-1 block text-xs leading-5 text-slate-500">{description}</span></span></label>)}</div></Card>;
}
