import AnalysisOptions from "../components/upload/AnalysisOptions.jsx";
import CameraGuide from "../components/upload/CameraGuide.jsx";
import UploadCard from "../components/upload/UploadCard.jsx";
import { Card } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";

export default function UploadSquat(props) {
  const names = { bodyweight_squat: "squat", sit_to_stand: "sit-to-stand", knee_extension: "knee extension" };
  return <main className="mx-auto w-full max-w-7xl px-6 py-12"><PageHeader eyebrow="Movement analyzer" title="Upload a movement video" description={`Choose a clear recording for the rule-based ${names[props.exercise]} analyzer.`} /><div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]"><div className="space-y-5"><Card className="p-5"><label htmlFor="exercise-selector" className="text-sm font-bold text-clinical-ink">Exercise</label><p className="mt-1 text-xs text-slate-500">Select the movement shown in the recording. Manual selection remains primary.</p><select id="exercise-selector" aria-label="Exercise selector" className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-semibold text-slate-800" value={props.exercise} disabled={props.isLoading} onChange={(event) => props.onExerciseChange(event.target.value)}><option value="bodyweight_squat">Bodyweight Squat</option><option value="sit_to_stand">Sit-to-Stand</option><option value="knee_extension">Knee Extension</option></select></Card><UploadCard {...props} /><AnalysisOptions exercise={props.exercise} value={props.options} onChange={props.onOptionsChange} disabled={props.isLoading} /></div><CameraGuide exercise={props.exercise} /></div></main>;
}
