import { createPortal } from "react-dom";
import { useEffect, useRef, useState } from "react";
import { BrainCircuit, Check, Dumbbell, X } from "lucide-react";
import AnalysisOptions from "../components/upload/AnalysisOptions.jsx";
import CameraGuide from "../components/upload/CameraGuide.jsx";
import UploadCard from "../components/upload/UploadCard.jsx";
import RecognitionUploadCard from "../components/recognition/RecognitionUploadCard.jsx";
import { Button, Card, LoadingSpinner } from "../components/common/UI.jsx";
import Select from "../components/common/Select.jsx";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
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

function ExercisePickerDialog({ exercises, onChoose, onClose }) {
  const { t, exerciseText } = useLocale();
  const dialogRef = useRef(null);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialogRef.current?.focus();
    function closeOnEscape(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [onClose]);

  return createPortal(
    <div
      className="fixed inset-0 z-[120] grid place-items-center overflow-y-auto bg-slate-950/55 p-4 backdrop-blur-sm"
      onMouseDown={onClose}
    >
      <section
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="exercise-picker-title"
        tabIndex={-1}
        className="my-auto w-full max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_30px_90px_rgba(7,20,38,0.28)] outline-none"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 bg-gradient-to-r from-white via-blue-50/40 to-teal-50/40 p-6 sm:p-7">
          <div className="flex gap-4">
            <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200">
              <Dumbbell size={23} aria-hidden="true" />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-clinical-teal">
                {t("upload.pickerEyebrow")}
              </p>
              <h2
                id="exercise-picker-title"
                className="mt-1 text-2xl font-extrabold tracking-tight text-clinical-ink"
              >
                {t("upload.pickerTitle")}
              </h2>
              <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">
                {t("upload.pickerDescription")}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
            aria-label={t("common.close")}
          >
            <X size={19} />
          </button>
        </div>
        <div className="grid max-h-[60vh] gap-3 overflow-y-auto p-5 sm:grid-cols-2 sm:p-6">
          {exercises.map((exercise) => {
            const text = exerciseText(exercise.exercise_id);
            return (
              <button
                key={exercise.exercise_id}
                type="button"
                onClick={() => onChoose(exercise.exercise_id)}
                className="group flex min-h-28 items-start gap-4 rounded-2xl border border-slate-200 bg-white p-4 text-start transition hover:-translate-y-0.5 hover:border-blue-300 hover:bg-blue-50/40 hover:shadow-lg hover:shadow-blue-100 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-blue-100"
              >
                <span className="mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-500 transition group-hover:bg-blue-600 group-hover:text-white">
                  <Dumbbell size={18} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block font-bold text-clinical-ink">
                    {text.name}
                  </span>
                  <span className="mt-1 block text-xs font-semibold uppercase tracking-wide text-clinical-teal">
                    {text.bodyRegion}
                  </span>
                  <span className="mt-2 block text-xs leading-5 text-slate-500">
                    {text.cameraView}
                  </span>
                </span>
                <Check
                  size={18}
                  className="mt-2 shrink-0 text-transparent transition group-hover:text-clinical-teal"
                />
              </button>
            );
          })}
        </div>
      </section>
    </div>,
    document.body,
  );
}

export default function UploadSquat(props) {
  const { t, exerciseText } = useLocale();
  const { user } = useAuth();
  const [showRecognition, setShowRecognition] = useState(false);
  const [showExercisePicker, setShowExercisePicker] = useState(false);
  const [recognitionModels, setRecognitionModels] = useState(null);
  const [desktopLayout, setDesktopLayout] = useState(
    () => typeof window !== "undefined" && window.innerWidth >= 1024,
  );
  const exercises = props.exercises || [];
  const supported = exercises.filter((item) => item.supported_in_app);
  const planned = exercises.filter((item) => !item.supported_in_app);
  const selectedExercise = exercises.find(
    (item) => item.exercise_id === props.exercise,
  );
  const selected = selectedExercise
    ? translatedExercise(selectedExercise, exerciseText)
    : null;
  const selectedName = props.exercise
    ? exerciseText(props.exercise)
    : { short: t("upload.movement") };

  useEffect(() => {
    if (!showRecognition || recognitionModels !== null) return undefined;
    let cancelled = false;
    getRecognitionModels()
      .then((result) => {
        if (!cancelled) setRecognitionModels(result.models || []);
      })
      .catch(() => {
        if (!cancelled) setRecognitionModels([]);
      });
    return () => {
      cancelled = true;
    };
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

  function requestAnalysis(event) {
    if (!props.exercise) {
      event?.preventDefault?.();
      setShowExercisePicker(true);
      return;
    }
    props.onSubmit(event);
  }

  function chooseExercise(exerciseId) {
    props.onExerciseChange(exerciseId);
    setShowExercisePicker(false);
  }

  return (
    <main>
      <PageHeader
        eyebrow={
          user?.role === "patient"
            ? t("upload.patientEyebrow")
            : t("upload.reviewEyebrow")
        }
        title={
          user?.role === "patient"
            ? t("upload.patientTitle")
            : t("upload.reviewTitle")
        }
        description={
          user?.role === "patient"
            ? t("upload.patientDescription")
            : t("upload.reviewDescription", { exercise: selectedName.short })
        }
      />
      <div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-5">
          <Card className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <label
                  htmlFor="exercise-selector"
                  className="text-sm font-bold text-clinical-ink"
                >
                  {t("common.exercise")}
                </label>
                <p className="mt-1 text-xs text-slate-500">
                  {t("upload.exerciseHelp")}
                </p>
              </div>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowRecognition((current) => !current)}
                disabled={props.isLoading}
                className="shrink-0"
                aria-expanded={showRecognition}
                aria-controls="analyze-recognition-panel"
              >
                {showRecognition ? (
                  <X size={17} aria-hidden="true" />
                ) : (
                  <BrainCircuit size={17} aria-hidden="true" />
                )}
                {showRecognition
                  ? t("upload.closeIdentification")
                  : t("upload.identifyInstead")}
              </Button>
            </div>
            <Select
              id="exercise-selector"
              ariaLabel="Exercise selector"
              className="mt-3"
              buttonClassName="min-h-12 font-semibold"
              value={props.exercise}
              disabled={props.isLoading}
              onChange={props.onExerciseChange}
              options={[
                {
                  value: "",
                  label: t("upload.chooseExercise"),
                  disabled: true,
                },
                {
                  label: t("upload.supportedGroup"),
                  options: supported.map((item) => ({
                    value: item.exercise_id,
                    label: exerciseText(item.exercise_id).name,
                  })),
                },
                {
                  label: t("upload.plannedGroup"),
                  options: planned.map((item) => ({
                    value: item.exercise_id,
                    label: `${exerciseText(item.exercise_id).name} - ${t("status.planned")}`,
                    disabled: true,
                  })),
                },
              ]}
            />
            {selected ? (
              <div className="mt-4 grid gap-3 rounded-xl bg-blue-50 p-4 text-sm sm:grid-cols-2">
                <div>
                  <p className="text-xs font-bold uppercase text-clinical-blue">
                    {t("upload.recommendedView")}
                  </p>
                  <p className="mt-1 text-slate-700">
                    {selected.recommended_camera_view}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-clinical-blue">
                    {t("upload.requiredVisibility")}
                  </p>
                  <p className="mt-1 text-slate-700">
                    {selected.required_landmarks?.join(", ")}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-clinical-blue">
                    {t("upload.instruction")}
                  </p>
                  <p className="mt-1 text-slate-700">
                    {selected.expected_movement_pattern}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase text-clinical-blue">
                    {t("upload.safety")}
                  </p>
                  <p className="mt-1 text-slate-700">{selected.safety_notes}</p>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowExercisePicker(true)}
                className="mt-4 flex w-full items-center gap-3 rounded-xl border border-dashed border-blue-300 bg-blue-50/40 p-4 text-start transition hover:border-blue-400 hover:bg-blue-50"
              >
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white text-clinical-blue shadow-sm">
                  <Dumbbell size={18} />
                </span>
                <span>
                  <span className="block text-sm font-bold text-clinical-ink">
                    {t("upload.noExerciseTitle")}
                  </span>
                  <span className="mt-1 block text-xs leading-5 text-slate-500">
                    {t("upload.noExerciseDescription")}
                  </span>
                </span>
              </button>
            )}
          </Card>
          {showRecognition ? (
            <div id="analyze-recognition-panel">
              {recognitionModels === null ? (
                <Card className="flex min-h-40 items-center justify-center p-6">
                  <LoadingSpinner label={t("upload.identificationLoading")} />
                </Card>
              ) : (
                <RecognitionUploadCard
                  models={recognitionModels}
                  onConfirmSuggestion={confirmRecognition}
                />
              )}
            </div>
          ) : null}
          {!desktopLayout && selected ? (
            <CameraGuide
              exercise={props.exercise}
              metadata={selected}
              compact
            />
          ) : null}
          <UploadCard {...props} onSubmit={requestAnalysis} />
          <details className="group rounded-[14px] border border-clinical-line bg-white shadow-panel">
            <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between px-5 text-sm font-bold text-clinical-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400">
              {t("upload.advancedOptions")}
              <span
                aria-hidden="true"
                className="text-lg text-slate-400 transition group-open:rotate-45"
              >
                +
              </span>
            </summary>
            <div className="border-t border-slate-100">
              <AnalysisOptions
                exercise={props.exercise}
                value={props.options}
                onChange={props.onOptionsChange}
                disabled={props.isLoading}
              />
            </div>
          </details>
        </div>
        {desktopLayout && selected ? (
          <CameraGuide exercise={props.exercise} metadata={selected} />
        ) : null}
      </div>
      {showExercisePicker ? (
        <ExercisePickerDialog
          exercises={supported}
          onChoose={chooseExercise}
          onClose={() => setShowExercisePicker(false)}
        />
      ) : null}
    </main>
  );
}
