"use client";
import { useRef, useState, type FormEvent } from "react";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "./Views";
import { api } from "../../lib/api";
import { planNumbers, planTexts, planPayload } from "../../lib/plans.mjs";
import type {
  ExercisePlanDetail,
  ExercisePlanCreate,
  ExercisePlanStatusUpdate,
} from "../../../../../packages/contracts/generated";
import { coreClient } from "../../../../../packages/contracts/client";
import type { Exercise } from "../../lib/types";
const client = coreClient(api);
const weekdays = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
] as const;
export function PlansView({ patientId }: { patientId: string }) {
  const { t, exerciseName, locale } = usePreferences();
  const plans = useResource<ExercisePlanDetail[]>(
    patientId
      ? `therapist/patients/${encodeURIComponent(patientId)}/exercise-plans`
      : null,
  );
  const [editing, setEditing] = useState<{ seed?: ExercisePlanDetail } | null>(
      null,
    ),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [saved, setSaved] = useState(false);
  async function status(
    row: ExercisePlanDetail,
    value: ExercisePlanStatusUpdate["status"],
  ) {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      await client.updatePlanStatus(patientId, row.plan_id, { status: value });
      plans.refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="plan-workspace">
      <div className="section-heading">
        <h2>{t("carePlans")}</h2>
        <button
          className="primary"
          disabled={busy}
          onClick={() => {
            setEditing({});
            setSaved(false);
          }}
        >
          {t("newPlan")}
        </button>
      </div>
      {saved && (
        <p role="status" className="success">
          {t("planSaved")}
        </p>
      )}
      {error && <p role="alert">{error}</p>}
      {editing && (
        <PlanEditor
          key={editing.seed?.plan_id ?? "new"}
          patientId={patientId}
          seed={editing.seed}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            setSaved(true);
            plans.refresh();
          }}
        />
      )}
      <ResourceState {...plans} retry={plans.refresh} />
      {plans.data?.length === 0 && <p className="empty">{t("noPlans")}</p>}
      {plans.data?.map((row) => (
        <article className="panel" key={row.plan_id}>
          <h3>{row.title}</h3>
          <p>
            {t(
              row.status === "active"
                ? "planActive"
                : row.status === "paused"
                  ? "planPaused"
                  : "planCompleted",
            )}{" "}
            · {row.created_by_name ?? t("unavailable")}
          </p>
          {row.notes && <p>{row.notes}</p>}
          <p>
            {row.start_date
              ? new Date(row.start_date).toLocaleDateString(locale)
              : t("unavailable")}{" "}
            –{" "}
            {row.end_date
              ? new Date(row.end_date).toLocaleDateString(locale)
              : t("unavailable")}
          </p>
          <details>
            <summary>
              {t("exercises")} ({row.items?.length ?? 0})
            </summary>
            {row.items?.map((item) => (
              <div className="review-response" key={item.item_id}>
                <h4>{exerciseName(item.exercise_id)}</h4>
                <dl>
                  {planNumbers.map(([field, label]) => (
                    <div key={String(field)}>
                      <dt>{t(label as "sets")}</dt>
                      <dd>{item[field as "sets"] ?? t("unavailable")}</dd>
                    </div>
                  ))}
                </dl>
                {planTexts.map(
                  ([field, label]) =>
                    item[field as "instructions"] && (
                      <p key={String(field)}>
                        <strong>{t(label as "instructions")}: </strong>
                        {item[field as "instructions"]}
                      </p>
                    ),
                )}
                <p>
                  {(item.schedule_days ?? [])
                    .map((day) => t(weekdays[day]))
                    .join(" · ")}
                </p>
                {item.requested_media_upload && <p>{t("requestMedia")}</p>}
                {item.requires_ai_analysis && <p>{t("requireAnalysis")}</p>}
              </div>
            ))}
          </details>
          <div className="button-row">
            <button
              className="secondary"
              disabled={busy}
              onClick={() => setEditing({ seed: row })}
            >
              {t("revisePlan")}
            </button>
            {row.status !== "completed" && (
              <button
                className="secondary"
                disabled={busy}
                onClick={() =>
                  status(row, row.status === "active" ? "paused" : "active")
                }
              >
                {t(row.status === "active" ? "pausePlan" : "resumePlan")}
              </button>
            )}
            {row.status !== "completed" && (
              <button
                className="secondary"
                disabled={busy}
                onClick={() => status(row, "completed")}
              >
                {t("completePlan")}
              </button>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
function PlanEditor({
  patientId,
  seed,
  onClose,
  onSaved,
}: {
  patientId: string;
  seed?: ExercisePlanDetail;
  onClose: () => void;
  onSaved: () => void;
}) {
  const { t, exerciseName } = usePreferences();
  const exercises = useResource<Exercise[]>("exercises");
  const [ids, setIds] = useState(
    () => seed?.items?.map((_, i) => String(i)) ?? ["0"],
  );
  const next = useRef(ids.length);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const request = useRef<{ body: string; key: string } | null>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setError("");
    let values: ExercisePlanCreate;
    try {
      values = planPayload(
        new FormData(event.currentTarget),
        ids,
      ) as ExercisePlanCreate;
    } catch (e) {
      setError(t((e as Error).message as "invalidDosage"));
      return;
    }
    const body = JSON.stringify(values);
    if (request.current?.body !== body)
      request.current = { body, key: crypto.randomUUID() };
    setBusy(true);
    try {
      await client.createPlan(patientId, values, request.current.key);
      onSaved();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (!exercises.data)
    return (
      <section className="panel">
        <ResourceState {...exercises} retry={exercises.refresh} />
        <button className="secondary" onClick={onClose}>
          {t("back")}
        </button>
      </section>
    );
  return (
    <section className="panel">
      <h3>{t(seed ? "revisePlan" : "newPlan")}</h3>
      <p className="notice">{t("planVersionNotice")}</p>
      <ResourceState {...exercises} retry={exercises.refresh} />
      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <label>
            {t("planTitle")}
            <input
              name="title"
              required
              maxLength={120}
              defaultValue={seed?.title}
            />
          </label>
          <label>
            {t("planNotes")}
            <textarea
              name="notes"
              maxLength={2000}
              defaultValue={seed?.notes ?? ""}
            />
          </label>
          <div className="two-columns">
            <label>
              {t("startDate")}
              <input
                type="date"
                name="start_date"
                defaultValue={seed?.start_date?.slice(0, 10)}
              />
            </label>
            <label>
              {t("endDate")}
              <input
                type="date"
                name="end_date"
                defaultValue={seed?.end_date?.slice(0, 10)}
              />
            </label>
          </div>
          {ids.map((id, index) => {
            const item = seed?.items?.[Number(id)];
            return (
              <fieldset className="plan-item" key={id}>
                <legend>
                  {t("exercise")} {index + 1}
                </legend>
                <label>
                  {t("exercise")}
                  <select
                    name={`${id}:exercise_id`}
                    required
                    defaultValue={item?.exercise_id ?? ""}
                  >
                    <option value="">{t("chooseExercise")}</option>
                    {exercises.data?.map((ex) => (
                      <option
                        key={ex.exercise_id || ex.id}
                        value={ex.exercise_id || ex.id}
                      >
                        {exerciseName(ex.exercise_id || ex.id || "")}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="plan-fields">
                  {planNumbers
                    .slice(0, 3)
                    .map(([field, label, min, max, required]) => (
                      <label key={String(field)}>
                        {t(label as "sets")}
                        <input
                          name={`${id}:${field}`}
                          type="number"
                          required={Boolean(required)}
                          min={Number(min)}
                          max={Number(max)}
                          step="1"
                          defaultValue={item?.[field as "sets"] ?? ""}
                        />
                      </label>
                    ))}
                </div>
                <label>
                  {t("instructions")}
                  <textarea
                    name={`${id}:instructions`}
                    maxLength={1000}
                    defaultValue={item?.instructions ?? ""}
                  />
                </label>
                <details>
                  <summary>{t("advancedPlan")}</summary>
                  <div className="plan-fields">
                    {planNumbers.slice(3).map(([field, label, min, max]) => (
                      <label key={String(field)}>
                        {t(label as "sets")}
                        <input
                          name={`${id}:${field}`}
                          type="number"
                          min={Number(min)}
                          max={Number(max)}
                          step={
                            String(field).startsWith("target_") ? "any" : "1"
                          }
                          defaultValue={item?.[field as "sets"] ?? ""}
                        />
                      </label>
                    ))}
                  </div>
                  {planTexts.slice(1).map(([field, label, max]) => (
                    <label key={String(field)}>
                      {t(label as "instructions")}
                      <textarea
                        name={`${id}:${field}`}
                        maxLength={Number(max)}
                        defaultValue={item?.[field as "instructions"] ?? ""}
                      />
                    </label>
                  ))}
                  <fieldset>
                    <legend>{t("scheduleDays")}</legend>
                    <div className="weekday-choices">
                      {weekdays.map((day, i) => (
                        <label className="check-label" key={day}>
                          <input
                            type="checkbox"
                            name={`${id}:schedule_days`}
                            value={i}
                            defaultChecked={item?.schedule_days?.includes(i)}
                          />
                          {t(day)}
                        </label>
                      ))}
                    </div>
                  </fieldset>
                  <label className="check-label">
                    <input
                      type="checkbox"
                      name={`${id}:requested_media_upload`}
                      defaultChecked={item?.requested_media_upload}
                    />
                    {t("requestMedia")}
                  </label>
                  <label className="check-label">
                    <input
                      type="checkbox"
                      name={`${id}:requires_ai_analysis`}
                      defaultChecked={item?.requires_ai_analysis}
                    />
                    {t("requireAnalysis")}
                  </label>
                </details>
                <button
                  type="button"
                  className="text-button"
                  disabled={ids.length === 1}
                  onClick={() => setIds(ids.filter((value) => value !== id))}
                >
                  {t("removeExercise")}
                </button>
              </fieldset>
            );
          })}
          <button
            type="button"
            className="secondary"
            disabled={ids.length >= 20}
            onClick={() => setIds([...ids, String(next.current++)])}
          >
            {t("addExercise")}
          </button>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <div className="button-row">
            <button className="primary" disabled={!exercises.data}>
              {t(busy ? "loading" : "publishPlan")}
            </button>
            <button className="secondary" type="button" onClick={onClose}>
              {t("back")}
            </button>
          </div>
        </fieldset>
      </form>
    </section>
  );
}
