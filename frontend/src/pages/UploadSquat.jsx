import AnalysisOptions from "../components/upload/AnalysisOptions.jsx";
import CameraGuide from "../components/upload/CameraGuide.jsx";
import UploadCard from "../components/upload/UploadCard.jsx";
import { Card } from "../components/common/UI.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { exerciseById } from "../data/exercises.js";
import { useLocale } from "../i18n/LocaleContext.jsx";

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
  const exercises = props.exercises || [];
  const selected = translatedExercise(exerciseById(props.exercise, exercises), exerciseText);
  const supported = exercises.filter((item) => item.supported_in_app);
  const planned = exercises.filter((item) => !item.supported_in_app);
  const selectedName = exerciseText(props.exercise);

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-12">
      <PageHeader
        eyebrow={t("upload.eyebrow")}
        title={t("upload.title")}
        description={t("upload.description", { exercise: selectedName.short })}
      />
      <div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-5">
          <Card className="p-5">
            <label htmlFor="exercise-selector" className="text-sm font-bold text-clinical-ink">
              {t("common.exercise")}
            </label>
            <p className="mt-1 text-xs text-slate-500">{t("upload.exerciseHelp")}</p>
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
          <UploadCard {...props} />
          <AnalysisOptions exercise={props.exercise} value={props.options} onChange={props.onOptionsChange} disabled={props.isLoading} />
        </div>
        <CameraGuide exercise={props.exercise} metadata={selected} />
      </div>
    </main>
  );
}
