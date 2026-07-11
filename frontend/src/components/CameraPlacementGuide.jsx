import { Camera, CheckCircle2 } from "lucide-react";

const tips = [
  "Use a side view for squat depth and trunk lean.",
  "Use a front view when reviewing possible knee valgus.",
  "Keep your full body visible from shoulders to feet.",
  "Place the camera on a stable surface in good lighting.",
  "Record 3-5 comfortable repetitions when safe to do so.",
  "Avoid very loose clothing that hides the hips, knees, or ankles when possible.",
];

export default function CameraPlacementGuide() {
  return (
    <aside className="mb-6 w-full max-w-2xl rounded-lg border border-clinical-line bg-white p-5 shadow-panel">
      <div className="flex items-center gap-2">
        <Camera size={20} className="text-clinical-teal" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-clinical-ink">Camera placement guide</h2>
      </div>
      <ul className="mt-4 grid gap-2 text-sm text-slate-700">
        {tips.map((tip) => (
          <li key={tip} className="flex gap-2">
            <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-clinical-teal" aria-hidden="true" />
            <span>{tip}</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
