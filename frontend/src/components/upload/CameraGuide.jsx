import { Camera, CheckCircle2, Lightbulb, ScanLine } from "lucide-react";
import { Card } from "../common/UI.jsx";

const squatTips = [
  ["Side view", "Best for squat depth and trunk lean."],
  ["Front view", "Best for reviewing possible knee valgus."],
  ["Full body visible", "Keep shoulders, hips, knees, ankles, and feet in frame."],
  ["Stable and bright", "Use a fixed camera position with even lighting."],
  ["Record 3–5 reps", "Move at a comfortable, controlled pace when safe."],
  ["Clear joint outline", "Avoid very loose clothing when possible."],
];
const chairTips = [
  ["Side or oblique view", "Place the phone on a stable surface beside the chair when possible."],
  ["Body and chair visible", "Show the full body or at least shoulders, hips, knees, ankles, and chair."],
  ["Use a stable chair", "Confirm the chair is secure before recording."],
  ["Stable and bright", "Use a fixed camera position with even lighting."],
  ["Record 3–5 reps", "Show complete sitting, rising, standing, lowering, and return-to-sitting cycles."],
  ["Stop when needed", "Stop if pain, dizziness, or unusual discomfort occurs."],
];
const kneeExtensionTips = [
  ["Side view", "Place the camera beside the exercising leg so the hip, knee, and ankle remain visible."],
  ["Seated position visible", "Show the chair, thigh, lower leg, and foot throughout the recording."],
  ["Stable chair", "Use a secure chair and keep the camera fixed."],
  ["Stable and bright", "Use even lighting and avoid clothing that hides the knee outline."],
  ["Record 3–5 reps", "Begin with the knee flexed, extend comfortably, then return to the start position."],
  ["Stop when needed", "Stop if pain, dizziness, or unusual discomfort occurs."],
];
const shoulderAbductionTips = [
  ["Front view", "Place the camera in front so the shoulder, elbow, wrist, and trunk remain visible."],
  ["Upper body visible", "Keep both shoulders, both arms, and the hips in frame."],
  ["Stable posture", "Stand or sit securely and keep the camera fixed."],
  ["Stable and bright", "Use even lighting and clothing that does not hide the arm outline."],
  ["Record 3–5 reps", "Begin with the arm near the side, raise it outward comfortably, then return."],
  ["Stop when needed", "Stop if pain, dizziness, numbness, or unusual discomfort occurs."],
];
const hipAbductionTips = [
  ["Front view", "Place the camera in front so the pelvis, hip, knee, ankle, and trunk remain visible."],
  ["Full lower body visible", "Keep both hips and the moving leg in frame from pelvis to foot."],
  ["Stable support", "Use a safe stable setup and keep the camera fixed."],
  ["Stable and bright", "Use even lighting and clothing that does not hide the hip and leg outline."],
  ["Record 3–5 reps", "Begin near neutral, move one leg outward comfortably, then return."],
  ["Stop when needed", "Stop if pain, dizziness, numbness, or unusual discomfort occurs."],
];

export default function CameraGuide({ exercise = "bodyweight_squat" }) {
  const tips = exercise === "sit_to_stand" ? chairTips : exercise === "knee_extension" ? kneeExtensionTips : exercise === "shoulder_abduction" ? shoulderAbductionTips : exercise === "hip_abduction" ? hipAbductionTips : squatTips;
  return <Card className="overflow-hidden"><div className="bg-gradient-to-br from-clinical-navy to-clinical-blue p-6 text-white"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-white/15"><Camera size={22} aria-hidden="true" /></span><div><p className="text-xs font-semibold uppercase tracking-widest text-blue-100">Before recording</p><h2 className="mt-1 text-xl font-bold">Camera placement guide</h2></div></div><div className="mt-6 grid grid-cols-2 gap-3"><div className="rounded-xl bg-white/10 p-3"><ScanLine size={18} aria-hidden="true" /><p className="mt-2 text-xs leading-5 text-blue-50">Keep the lens near hip height and the movement area fully framed.</p></div><div className="rounded-xl bg-white/10 p-3"><Lightbulb size={18} aria-hidden="true" /><p className="mt-2 text-xs leading-5 text-blue-50">Avoid strong backlight and moving backgrounds.</p></div></div></div><ul className="grid gap-1 p-5">{tips.map(([title, text]) => <li key={title} className="flex gap-3 rounded-xl px-2 py-2.5"><CheckCircle2 className="mt-0.5 shrink-0 text-clinical-teal" size={17} aria-hidden="true" /><div><p className="text-sm font-semibold text-slate-800">{title}</p><p className="mt-0.5 text-xs leading-5 text-slate-500">{text}</p></div></li>)}</ul></Card>;
}
