import AnalysisOptions from "../components/upload/AnalysisOptions.jsx";
import CameraGuide from "../components/upload/CameraGuide.jsx";
import UploadCard from "../components/upload/UploadCard.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";

export default function UploadSquat(props) {
  return <main className="mx-auto w-full max-w-7xl px-6 py-12"><PageHeader eyebrow="Squat analyzer" title="Upload a movement video" description="Choose a clear recording and optional outputs. Processing stays centered on the current rule-based squat analysis." /><div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]"><div className="space-y-5"><UploadCard {...props} /><AnalysisOptions value={props.options} onChange={props.onOptionsChange} disabled={props.isLoading} /></div><CameraGuide /></div></main>;
}
