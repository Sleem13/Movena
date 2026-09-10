import {
  ArrowRight,
  ArrowLeft,
  PersonStanding,
  Camera,
  CircleCheck,
  Clock3,
  ChevronRight,
  Search,
  ShieldCheck,
  X,
} from "lucide-react";
import { Badge, Button, Card, EmptyState } from "../components/common/UI.jsx";
import Select from "../components/common/Select.jsx";
import ExerciseInstructions from "../components/exercises/ExerciseInstructions.jsx";
import ExerciseIllustration from "../components/exercises/ExerciseIllustration.jsx";
import { useMemo, useState } from "react";
import { PageHeader } from "../components/layout/AppShell.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";

function localizeExercise(exercise, exerciseText, locale) {
  if (exercise.guidance_available) return locale === "ar" ? { ...exercise, ...exercise.localized_ar } : exercise;
  if (exercise.recognition_status === "experimental_candidate_data_available")
    return exercise;
  const text = exerciseText(exercise.exercise_id);
  return {
    ...exercise,
    display_name: text.name,
    body_region: text.bodyRegion,
    exercise_family: text.family,
    recommended_camera_view: text.cameraView,
    movement_description: text.description,
    safety_notes: text.safety,
    ...(locale === "ar" ? exercise.localized_ar : {}),
  };
}

function ExerciseCard({ exercise, onAnalyze }) {
  const { t, locale } = useLocale();
  const { user } = useAuth();
  const supported = exercise.supported_in_app;
  const recognitionCandidate =
    exercise.recognition_status === "experimental_candidate_data_available";
  return (
    <Card
      as="article"
      className={`exercise-card group flex h-full flex-col overflow-hidden p-0 transition duration-200 ${supported ? "hover:border-blue-200" : "bg-slate-50/70"}`}
    >
      <div
        className="exercise-media"
      >
        <ExerciseIllustration
          exerciseId={exercise.exercise_id}
          label={`${exercise.display_name} ${t("exercises.posePreview")}`}
          supported={supported}
        />
      </div>
      <div className="exercise-card-body flex flex-1 flex-col">
        <div className="exercise-availability">
          <Badge
            tone={supported ? "teal" : recognitionCandidate ? "blue" : "slate"}
          >
            {supported ? <CircleCheck size={16} fill="currentColor" className="supported-check" /> : null}
            {exercise.guidance_available ? (locale === "ar" ? "دليل تمرين · دون تحليل آلي" : "Exercise guide · no AI analysis") : supported
              ? t("status.supported")
              : recognitionCandidate
                ? t("status.recognitionResearch")
                : t("status.planned")}
          </Badge>
        </div>
        <h2 className="text-lg font-bold text-clinical-ink">
          {exercise.display_name}
        </h2>
        <div className="exercise-metadata">
          <span><PersonStanding size={20} aria-hidden="true" />{exercise.body_region}</span>
          {!exercise.guidance_available ? <span><Camera size={20} aria-hidden="true" />{exercise.recommended_camera_view}</span> : null}
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {exercise.movement_description}
        </p>
        <div className="exercise-safety flex items-start gap-3 text-sm leading-5 text-slate-600">
          <ShieldCheck className="mt-0.5 shrink-0" size={21} />
          <div><p className="mb-1 font-semibold text-clinical-ink">{t("upload.safety")}</p><p>{exercise.safety_notes}</p></div>
        </div>
        <div className="mt-auto pt-5">
          <ExerciseInstructions exercise={exercise} />
          {supported ? (
            <Button
              className="w-full"
              onClick={() => onAnalyze(exercise.exercise_id)}
            >
              {user?.role === "patient"
                ? t("exercises.startExercise")
                : user?.role === "therapist"
                  ? t("exercises.reviewExercise")
                  : t("exercises.analyzeThis")}
              <ArrowRight size={16} />
            </Button>
          ) : exercise.guidance_available ? null : (
            <Button className="w-full" variant="secondary" disabled>
              <Clock3 size={16} />
              {t("status.notAvailable")}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

export default function ExerciseLibrary({ exercises, onAnalyze }) {
  const { t, exerciseText, locale } = useLocale();
  const [query, setQuery] = useState("");
  const [availability, setAvailability] = useState("all");
  const [bodyRegion, setBodyRegion] = useState("all");
  const [page, setPage] = useState(0);
  const translatedExercises = useMemo(
    () => exercises.map((item) => localizeExercise(item, exerciseText, locale)),
    [exerciseText, exercises, locale],
  );
  const bodyRegions = useMemo(
    () =>
      Array.from(
        new Set(
          translatedExercises
            .filter((item) => item.supported_in_app || item.guidance_available)
            .map((item) => item.body_region),
        ),
      ).sort(),
    [translatedExercises],
  );
  const filteredExercises = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return translatedExercises.filter((item) => {
      const matchesQuery =
        !normalizedQuery ||
        [
          item.display_name,
          item.body_region,
          item.exercise_family,
          item.movement_description,
          item.recommended_camera_view,
        ].some((value) =>
          String(value).toLowerCase().includes(normalizedQuery),
        );
      const matchesAvailability =
        availability === "all" ||
        (availability === "supported"
          ? item.supported_in_app
          : !item.supported_in_app);
      const matchesBodyRegion =
        bodyRegion === "all" || item.body_region === bodyRegion;
      return matchesQuery && matchesAvailability && matchesBodyRegion;
    });
  }, [availability, bodyRegion, query, translatedExercises]);
  const supported = filteredExercises.filter((item) => item.supported_in_app);
  const planned = filteredExercises.filter((item) => !item.supported_in_app);
  const pageCount = Math.max(1, Math.ceil(supported.length / 3));
  const currentPage = Math.min(page, pageCount - 1);
  const visibleExercises = supported.slice(currentPage * 3, currentPage * 3 + 3);
  const hasActiveFilters =
    query || availability !== "all" || bodyRegion !== "all";
  function resetFilters() {
    setQuery("");
    setAvailability("all");
    setBodyRegion("all");
    setPage(0);
  }
  const matchLabel =
    filteredExercises.length === 1
      ? t("exercises.matchSingular")
      : t("exercises.matchPlural");
  const matchVerb =
    filteredExercises.length === 1
      ? t("exercises.matchVerbSingular")
      : t("exercises.matchVerbPlural");

  return (
    <main className="exercise-library">
      <PageHeader
        eyebrow={t("exercises.eyebrow")}
        title={t("exercises.title")}
        description={t("exercises.description")}
      />
      <section
        className="exercise-filters"
        aria-label="Exercise filters"
      >
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_190px_210px_44px]">
          <label className="relative block">
            <span className="sr-only">{t("exercises.search")}</span>
            <Search
              className="pointer-events-none absolute start-3 top-1/2 -translate-y-1/2 text-slate-400"
              size={18}
              aria-hidden="true"
            />
            <input
              value={query}
              onChange={(event) => { setQuery(event.target.value); setPage(0); }}
              type="search"
              className="h-11 w-full rounded-lg border border-slate-200 bg-white ps-10 pe-3 text-sm text-clinical-ink placeholder:text-slate-400 focus:border-clinical-blue focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder={t("exercises.searchPlaceholder")}
            />
          </label>
          <Select
            ariaLabel={t("exercises.availability")}
            value={availability}
            onChange={(value) => { setAvailability(value); setPage(0); }}
            options={[
              { value: "all", label: t("exercises.allAvailability") },
              { value: "supported", label: t("exercises.supportedOnly") },
              { value: "planned", label: locale === "ar" ? "أدلة دون تحليل" : "Guides / no analysis" },
            ]}
          />
          <Select
            ariaLabel={t("exercises.bodyRegion")}
            value={bodyRegion}
            onChange={(value) => { setBodyRegion(value); setPage(0); }}
            options={[
              { value: "all", label: t("exercises.allRegions") },
              ...bodyRegions.map((region) => ({
                value: region,
                label: region,
              })),
            ]}
          />
          <Button
            type="button"
            variant="ghost"
            onClick={resetFilters}
            disabled={!hasActiveFilters}
            aria-label="Clear exercise filters"
            title={t("common.clear")}
            className="px-0"
          >
            <X size={16} />
            <span className="clear-filters-label">{t("exercises.clearFilters")}</span>
          </Button>
        </div>
        <p role="status" aria-live="polite" className="mt-3 text-xs text-slate-500">
          {t("exercises.matchCount", {
            count: filteredExercises.length,
            label: matchLabel,
            verb: matchVerb,
          })}
        </p>
      </section>
      {filteredExercises.length === 0 ? (
        <EmptyState
          title={t("exercises.noMatch")}
          description={t("exercises.noMatchDescription")}
          actions={<Button variant="secondary" onClick={resetFilters}><X size={16} />{t("common.clear")}</Button>}
        />
      ) : (
        <>
          <section aria-labelledby="supported-exercises">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2
                  id="supported-exercises"
                  className="text-xl font-bold text-clinical-ink"
                >
                  {t("exercises.supportedTitle")}
                </h2>
                <p className="sr-only">
                  {t("exercises.supportedDescription")}
                </p>
              </div>
              <span className="sr-only"><Badge tone="teal">
                {t("exercises.availableCount", { count: supported.length })}
              </Badge></span>
              {pageCount > 1 ? <nav className="exercise-pagination" aria-label={t("exercises.pages")}>
                <Button variant="ghost" onClick={() => setPage(currentPage - 1)} disabled={currentPage === 0} aria-label={t("exercises.previous")} title={t("exercises.previous")}><ArrowLeft size={18} className="rtl:rotate-180" /></Button>
                <span aria-live="polite">{currentPage + 1} / {pageCount}</span>
                <Button variant="ghost" onClick={() => setPage(currentPage + 1)} disabled={currentPage === pageCount - 1} aria-label={t("exercises.next")} title={t("exercises.next")}><ArrowRight size={18} className="rtl:rotate-180" /></Button>
              </nav> : null}
            </div>
            {supported.length ? (
              <div className="exercise-responsive-grid mt-5 grid gap-5">
                {visibleExercises.map((item) => (
                  <ExerciseCard
                    key={item.exercise_id}
                    exercise={item}
                    onAnalyze={onAnalyze}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                compact
                title={t("exercises.noSupported")}
                description={t("exercises.adjustSupported")}
              />
            )}
          </section>
          <details
            className="research-disclosure"
            open={hasActiveFilters ? true : undefined}
          >
            <summary><ChevronRight size={18} /><span>{locale === "ar" ? "أدلة التمارين والتغطية المخطط لها" : "Exercise guides and planned coverage"}</span></summary>
            <div className="my-5 border-s-2 border-teal-600 ps-4">
              <h3 className="text-sm font-semibold text-clinical-ink">{locale === "ar" ? "إرشادات لخطة معالجك" : "Guidance for your therapist's plan"}</h3>
              <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">{locale === "ar" ? "يمكن قراءة الأدلة واستخدام التمارين في خطة المعالج؛ لا يتوفر لها تحليل آلي." : "Read the guides and use these exercises in therapist-assigned plans. Automated analysis is not available for these movements."}</p>
            </div>
          <section
            className="mt-5"
            aria-labelledby="planned-exercises"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2
                  id="planned-exercises"
                  className="text-xl font-bold text-clinical-ink"
                >
                  {locale === "ar" ? "أدلة التمارين" : "Exercise guides"}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {locale === "ar" ? "يحدد المعالج الجرعة والاحتياطات المناسبة لك." : "Your therapist selects the appropriate dosage and precautions."}
                </p>
              </div>
              <Badge tone="slate">
                {planned.length}
              </Badge>
            </div>
            {planned.length ? (
              <div className="exercise-responsive-grid mt-5 grid gap-5">
                {planned.map((item) => (
                  <ExerciseCard
                    key={item.exercise_id}
                    exercise={item}
                    onAnalyze={onAnalyze}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                compact
                title={t("exercises.noPlanned")}
                description={t("exercises.adjustPlanned")}
              />
            )}
          </section>
          </details>
        </>
      )}
    </main>
  );
}
