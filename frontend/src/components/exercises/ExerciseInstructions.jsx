import { useLocale } from "../../i18n/LocaleContext.jsx";

export default function ExerciseInstructions({ exercise }) {
  const { locale } = useLocale();
  if (!exercise.instructions?.length) return null;
  return <details className="mb-3">
    <summary className="min-h-11 cursor-pointer rounded-xl border border-clinical-line p-3 font-semibold focus-visible:outline focus-visible:outline-2">{locale === "ar" ? "عرض التعليمات" : "View instructions"}</summary>
    <ol className="my-3 list-decimal space-y-2 ps-5 text-sm">{exercise.instructions.map((step) => <li key={step}>{step}</li>)}</ol>
    <p className="text-sm">{exercise.dosage_guidance}</p>
    <p className="mt-2 text-sm">{locale === "ar" ? "توقف عند ألم حاد أو دوخة أو أعراض جديدة واطلب المشورة. بعد الإصابة أو الجراحة اتبع تعليمات فريقك العلاجي." : "Stop for sharp pain, dizziness, or new symptoms and seek advice. After injury or surgery, follow your care team's restrictions."}</p>
    {exercise.reference_note ? <p className="mt-2 text-sm">{exercise.reference_note}</p> : null}
    {exercise.source_urls?.map((url) => <a className="mt-2 block min-h-11 p-2 text-clinical-blue underline" key={url} href={url} target="_blank" rel="noreferrer">{locale === "ar" ? "مرجع التمرين" : "Exercise reference"}: {new URL(url).hostname}</a>)}
  </details>;
}
