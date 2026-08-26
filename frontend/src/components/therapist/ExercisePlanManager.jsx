import { useMemo, useState } from "react";
import { CheckCircle2, ClipboardList, Pause, Play, Plus, Trash2 } from "lucide-react";
import { SUPPORTED_EXERCISES } from "../../data/exercises.js";
import { createPatientExercisePlan, updatePatientExercisePlanStatus } from "../../services/api.js";
import { useLocale } from "../../i18n/LocaleContext.jsx";
import Select from "../common/Select.jsx";
import { Alert, Badge, Button, Card, EmptyState, LoadingSpinner } from "../common/UI.jsx";

const fieldClass = "min-h-11 w-full rounded-[11px] border border-clinical-line bg-white px-3 text-sm text-clinical-ink outline-none transition placeholder:text-slate-400 hover:border-blue-300 focus:border-blue-400 focus:ring-4 focus:ring-blue-100";
const newItem = () => ({ exercise_id: "bodyweight_squat", sets: 3, reps: 8, days_per_week: 3, instructions: "" });

export default function ExercisePlanManager({ patientId, plans, onPlansChange }) {
  const { t, exerciseText } = useLocale();
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState([newItem()]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const exerciseOptions = useMemo(() => SUPPORTED_EXERCISES.map((exercise) => ({
    value: exercise.exercise_id,
    label: exerciseText(exercise.exercise_id).name,
  })), [exerciseText]);

  function updateItem(index, field, value) {
    setItems((current) => current.map((item, itemIndex) => (
      itemIndex === index ? { ...item, [field]: value } : item
    )));
  }

  async function createPlan(event) {
    event.preventDefault();
    if (!title.trim() || !items.length) return;
    setSaving(true);
    setError("");
    try {
      const created = await createPatientExercisePlan(patientId, {
        title: title.trim(),
        notes: notes.trim() || null,
        items: items.map((item) => ({
          ...item,
          sets: Number(item.sets),
          reps: Number(item.reps),
          days_per_week: Number(item.days_per_week),
          instructions: item.instructions.trim() || null,
        })),
      });
      onPlansChange([created, ...plans]);
      setTitle("");
      setNotes("");
      setItems([newItem()]);
    } catch {
      setError(t("therapist.planSaveError"));
    } finally {
      setSaving(false);
    }
  }

  async function changeStatus(plan, status) {
    setError("");
    try {
      const updated = await updatePatientExercisePlanStatus(patientId, plan.plan_id, status);
      onPlansChange(plans.map((entry) => entry.plan_id === updated.plan_id ? updated : entry));
    } catch {
      setError(t("therapist.planStatusError"));
    }
  }

  return <div className="grid gap-5 xl:grid-cols-[minmax(320px,.78fr)_minmax(0,1.22fr)]">
    <Card className="self-start p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-clinical-blue ring-1 ring-blue-100"><ClipboardList size={19} /></span>
        <div><h2 className="font-bold text-clinical-ink">{t("therapist.createPlan")}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{t("therapist.planHelp")}</p></div>
      </div>
      <form className="mt-5 space-y-4" onSubmit={createPlan}>
        <label className="block"><span className="mb-1.5 block text-xs font-semibold text-slate-700">{t("therapist.planTitle")}</span><input className={fieldClass} value={title} onChange={(event) => setTitle(event.target.value)} maxLength={120} required /></label>
        <label className="block"><span className="mb-1.5 block text-xs font-semibold text-slate-700">{t("therapist.planNotes")}</span><textarea className={`${fieldClass} min-h-20 py-3`} value={notes} onChange={(event) => setNotes(event.target.value)} maxLength={2000} /></label>
        <div className="space-y-3">
          {items.map((item, index) => <div key={index} className="rounded-xl border border-clinical-line bg-slate-50/70 p-3">
            <div className="flex items-center justify-between gap-2"><p className="text-xs font-bold text-clinical-ink">{t("therapist.planExercise", { count: index + 1 })}</p>{items.length > 1 ? <button type="button" className="rounded-lg p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600" aria-label={t("therapist.removeExercise")} onClick={() => setItems((current) => current.filter((_, itemIndex) => itemIndex !== index))}><Trash2 size={16} /></button> : null}</div>
            <Select ariaLabel={t("therapist.exercise")} className="mt-2" options={exerciseOptions} value={item.exercise_id} onChange={(value) => updateItem(index, "exercise_id", value)} />
            <div className="mt-3 grid grid-cols-3 gap-2">
              {["sets", "reps", "days_per_week"].map((field) => <label key={field}><span className="mb-1 block text-[11px] font-semibold text-slate-500">{t(`therapist.${field}`)}</span><input type="number" className={fieldClass} min="1" max={field === "days_per_week" ? "7" : field === "sets" ? "20" : "100"} value={item[field]} onChange={(event) => updateItem(index, field, event.target.value)} required /></label>)}
            </div>
            <label className="mt-3 block"><span className="mb-1 block text-[11px] font-semibold text-slate-500">{t("therapist.instructions")}</span><input className={fieldClass} value={item.instructions} onChange={(event) => updateItem(index, "instructions", event.target.value)} maxLength={1000} /></label>
          </div>)}
        </div>
        <Button type="button" variant="secondary" className="w-full" onClick={() => setItems((current) => [...current, newItem()])}><Plus size={16} />{t("therapist.addExercise")}</Button>
        {error ? <Alert>{error}</Alert> : null}
        <Button type="submit" className="w-full" disabled={saving || !title.trim()}>{saving ? <LoadingSpinner label={t("therapist.savingPlan")} /> : <><ClipboardList size={16} />{t("therapist.savePlan")}</>}</Button>
      </form>
    </Card>
    <Card className="p-5 sm:p-6">
      <div className="flex items-end justify-between gap-4"><div><h2 className="font-bold text-clinical-ink">{t("therapist.assignedPlans")}</h2><p className="mt-1 text-xs text-slate-500">{t("therapist.assignedPlansHelp")}</p></div><Badge tone="blue">{plans.length}</Badge></div>
      {plans.length ? <div className="mt-5 space-y-3">{plans.map((plan) => <article key={plan.plan_id} className="rounded-xl border border-clinical-line p-4">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><div className="flex flex-wrap items-center gap-2"><h3 className="font-bold text-clinical-ink">{plan.title}</h3><Badge tone={plan.status === "active" ? "teal" : plan.status === "paused" ? "amber" : "slate"}>{t(`therapist.planStatus.${plan.status}`)}</Badge></div>{plan.notes ? <p className="mt-2 text-xs leading-5 text-slate-500">{plan.notes}</p> : null}</div><div className="flex gap-1">{plan.status !== "active" ? <Button variant="ghost" className="min-h-9 px-3" onClick={() => changeStatus(plan, "active")}><Play size={15} />{t("therapist.activate")}</Button> : <Button variant="ghost" className="min-h-9 px-3" onClick={() => changeStatus(plan, "paused")}><Pause size={15} />{t("therapist.pause")}</Button>}{plan.status !== "completed" ? <Button variant="ghost" className="min-h-9 px-3" onClick={() => changeStatus(plan, "completed")}><CheckCircle2 size={15} />{t("therapist.complete")}</Button> : null}</div></div>
        <ul className="mt-4 divide-y divide-slate-100 rounded-xl bg-slate-50 px-3">{plan.items.map((item) => <li key={item.item_id} className="py-3 text-sm"><div className="flex flex-wrap items-center justify-between gap-2"><span className="font-semibold text-clinical-ink">{exerciseText(item.exercise_id).name}</span><span className="text-xs font-medium text-slate-500">{t("therapist.prescription", { sets: item.sets, reps: item.reps, days: item.days_per_week })}</span></div>{item.instructions ? <p className="mt-1 text-xs leading-5 text-slate-500">{item.instructions}</p> : null}</li>)}</ul>
      </article>)}</div> : <div className="mt-5"><EmptyState compact icon={ClipboardList} title={t("therapist.noPlans")} description={t("therapist.noPlansHelp")} /></div>}
    </Card>
  </div>;
}
