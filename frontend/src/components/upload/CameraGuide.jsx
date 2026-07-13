import { Camera, CheckCircle2, Lightbulb, ScanLine } from "lucide-react";
import { Card } from "../common/UI.jsx";

const tips = [
  ["Side view", "Best for squat depth and trunk lean."],
  ["Front view", "Best for reviewing possible knee valgus."],
  ["Full body visible", "Keep shoulders, hips, knees, ankles, and feet in frame."],
  ["Stable and bright", "Use a fixed camera position with even lighting."],
  ["Record 3–5 reps", "Move at a comfortable, controlled pace when safe."],
  ["Clear joint outline", "Avoid very loose clothing when possible."],
];

export default function CameraGuide() {
  return <Card className="overflow-hidden"><div className="bg-gradient-to-br from-clinical-navy to-clinical-blue p-6 text-white"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-white/15"><Camera size={22} aria-hidden="true" /></span><div><p className="text-xs font-semibold uppercase tracking-widest text-blue-100">Before recording</p><h2 className="mt-1 text-xl font-bold">Camera placement guide</h2></div></div><div className="mt-6 grid grid-cols-2 gap-3"><div className="rounded-xl bg-white/10 p-3"><ScanLine size={18} aria-hidden="true" /><p className="mt-2 text-xs leading-5 text-blue-50">Keep the lens near hip height and perpendicular to the movement plane.</p></div><div className="rounded-xl bg-white/10 p-3"><Lightbulb size={18} aria-hidden="true" /><p className="mt-2 text-xs leading-5 text-blue-50">Avoid strong backlight and moving backgrounds.</p></div></div></div><ul className="grid gap-1 p-5">{tips.map(([title, text]) => <li key={title} className="flex gap-3 rounded-xl px-2 py-2.5"><CheckCircle2 className="mt-0.5 shrink-0 text-clinical-teal" size={17} aria-hidden="true" /><div><p className="text-sm font-semibold text-slate-800">{title}</p><p className="mt-0.5 text-xs leading-5 text-slate-500">{text}</p></div></li>)}</ul></Card>;
}
