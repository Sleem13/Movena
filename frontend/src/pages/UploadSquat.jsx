import { useEffect, useState } from "react";
import { BrainCircuit, X } from "lucide-react";
import AnalysisOptions from "../components/upload/AnalysisOptions.jsx";
import CameraGuide from "../components/upload/CameraGuide.jsx";
import UploadCard from "../components/upload/UploadCard.jsx";
import RecognitionUploadCard from "../components/recognition/RecognitionUploadCard.jsx";
import { Button, Card, LoadingSpinner } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { exerciseById } from "../data/exercises.js";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { getRecognitionModels } from "../services/api.js";

function translatedExercise(exercise, exerciseText) {
  const text = exerciseText(exercise.exercise_id);
  return {
    ...exercise,
    display_name: text.name,
    body_region: text.bodyRegion,
    exercise_family: text.family,
    recommended_camera_view: text.cameraView,
    required_landmarks: text.landmarks,
    movement_description: text.description,
    expected_movement_pattern: text.pattern,
    safety_notes: text.safety,
  };
}

export default function UploadSquat(props) {
  const { t, exerciseText } = useLocale();
  const [showRecognition, setShowRecognition] = useState(false);
  const [recognitionModels, setRecognitionModels] = useState(null);
  const [desktopLayout, setDesktopLayout] = useState(() => typeof window !== "undefined" && window.innerWidth >= 1024);
  const exercises = props.exercises || [];
  const selected = translatedExercise(exerciseById(props.exercise, exercises), exerciseText);
  const supported = exercises.filter((item) => item.supported_in_app);
  const planned = exercises.filter((item) => !item.supported_in_app);
  const selectedName = exerciseText(props.exercise);

  useEffect(() => {
    if (!showRecognition || recognitionModels !== null) return undefined;
    let cancelled = false;
    getRecognitionModels()
      .then((result) => { if (!cancelled) setRecognitionModels(result.models || []); })
      .catch(() => { if (!cancelled) setRecognitionModels([]); });
    return () => { cancelled = true; };
  }, [showRecognition, recognitionModels]);

  useEffect(() => {
    const media = window.matchMedia?.("(min-width: 1024px)");
    if (!media) return undefined;
    const updateLayout = () => setDesktopLayout(media.matches);
    updateLayout();
    media.addEventListener?.("change", updateLayout);
    return () => media.removeEventListener?.("change", updateLayout);
  }, []);

  function confirmRecognition(exerciseId, recognizedFile) {
    props.onRecognitionConfirm?.(exerciseId, recognizedFile);
    setShowRecognition(false);
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-5 py-8 sm:px-8 lg:px-10 lg:py-10">
      <PageHeader
        title={t("upload.title")}
        description={t("upload.description", { exercise: selectedName.short })}
      />
      <div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-5">
          <Card className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <label htmlFor="exercise-selector" className="text-sm font-bold text-clinical-ink">
                  {t("common.exercise")}
                </label>
                <p className="mt-1 text-xs text-slate-500">{t("upload.exerciseHelp")}</p>
              </div>
              <Button type="button" variant="secondary" onClick={() => setShowRecognition((current) => !current)} disabled={props.isLoading} className="shrink-0" aria-expanded={showRecognition} aria-controls="analyze-recognition-panel">
                {showRecognition ? <X size={17} aria-hidden="true" /> : <BrainCircuit size={17} aria-hidden="true" />}
                {showRecognition ? t("upload.closeIdentification") : t("upload.identifyInstead")}
              </Button>
            </div>
            <select
              id="exercise-selector"
              aria-label="Exercise selector"
              className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-semibold text-slate-800"
              value={props.exercise}
              disabled={props.isLoading}
              onChange={(event) => props.onExerciseChange(event.target.value)}
            >
              <optgroup label={t("upload.supportedGroup")}>
                {supported.map((item) => (
                  <option key={item.exercise_id} value={item.exercise_id}>
                    {exerciseText(item.exercise_id).name}
                  </option>
                ))}
              </optgroup>
              <optgroup label={t("upload.plannedGroup")}>
                {planned.map((item) => (
                  <option key={item.exercise_id} value={item.exercise_id} disabled>
                    {exerciseText(item.exercise_id).name} - {t("status.planned")}
                  </option>
                ))}
              </optgroup>
            </select>
            <div className="mt-4 grid gap-3 rounded-xl bg-blue-50 p-4 text-sm sm:grid-cols-2">
              <div>
                <p className="text-xs font-bold uppercase text-clinical-blue">{t("upload.recommendedView")}</p>
                <p className="mt-1 text-slate-700">{selected.recommended_camera_view}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-clinical-blue">{t("upload.requiredVisibility")}</p>
                <p className="mt-1 text-slate-700">{selected.required_landmarks?.join(", ")}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-clinical-blue">{t("upload.instruction")}</p>
                <p className="mt-1 text-slate-700">{selected.expected_movement_pattern}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-clinical-blue">{t("upload.safety")}</p>
                <p className="mt-1 text-slate-700">{selected.safety_notes}</p>
              </div>
            </div>
          </Card>
          {showRecognition ? (
            <div id="analyze-recognition-panel">
              {recognitionModels === null ? (
                <Card className="flex min-h-40 items-center justify-center p-6">
                  <LoadingSpinner label={t("upload.identificationLoading")} />
                </Card>
              ) : (
                <RecognitionUploadCard models={recognitionModels} onConfirmSuggestion={confirmRecognition} />
              )}
            </div>
          ) : null}
          {!desktopLayout ? <CameraGuide exercise={props.exercise} metadata={selected} compact /> : null}
          <UploadCard {...props} />
          <AnalysisOptions exercise={props.exercise} value={props.options} onChange={props.onOptionsChange} disabled={props.isLoading} />
        </div>
        {desktopLayout ? <CameraGuide exercise={props.exercise} metadata={selected} /> : null}
      </div>
    </main>
  );
}
