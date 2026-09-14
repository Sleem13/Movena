"use client";
import { useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { usePreferences } from "../Preferences";
import { useResource } from "../Resource";
import { ResourceState } from "./Views";
import { AnalyzeView } from "../analysis/Views";
import { api } from "../../lib/api";
import type { PlanItem, Today } from "../../lib/types";
const symptomFlags = [
  "pain_increase",
  "dizziness",
  "faintness",
  "unusual_shortness_of_breath",
  "chest_discomfort",
  "new_numbness_or_weakness",
  "instability",
  "other",
] as const;

export function CheckInView({ id }: { id: string }) {
  const resource = useResource<Today>("patient/today");
  const { t } = usePreferences();
  if (!resource.data)
    return <ResourceState {...resource} retry={resource.refresh} />;
  const item = resource.data.plan_items?.find((item) => item.item_id === id);
  if (!item)
    return (
      <section className="panel">
        <p>{t("unavailable")}</p>
        <Link className="text-link" href="/workspace/today">
          {t("back")}
        </Link>
      </section>
    );
  return (
    <CheckInForm
      key={`${id}:${resource.data.date}`}
      item={item}
      today={resource.data}
    />
  );
}

function CheckInForm({ item, today }: { item: PlanItem; today: Today }) {
  const { t, exerciseName } = usePreferences();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [symptoms, setSymptoms] = useState(item.symptoms_changed ?? false);
  const [stopped, setStopped] = useState(item.stopped_due_to_symptoms ?? false);
  const [flags, setFlags] = useState<string[]>(item.symptom_flags ?? []);
  const [analysisSession, setAnalysisSession] = useState(
    item.analysis_session_id ?? null,
  );
  const [analyzing, setAnalyzing] = useState(false);
  const submission = useRef<{ body: string; key: string } | null>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setError("");
    setBusy(true);
    const data = new FormData(event.currentTarget);
    const optional = (key: string) =>
      data.get(key) !== "" && data.get(key) !== null
        ? Number(data.get(key))
        : null;
    const body = JSON.stringify({
      plan_item_id: item.item_id,
      scheduled_date: today.date,
      completion_status: data.get("completion_status"),
      pain_before: optional("pain_before"),
      pain_after: optional("pain_after"),
      difficulty: optional("difficulty"),
      fatigue: optional("fatigue"),
      perceived_exertion: optional("perceived_exertion"),
      symptoms_changed: symptoms,
      stopped_due_to_symptoms: stopped,
      symptom_flags: [...flags].sort(),
      safety_acknowledged: data.get("safety") === "on",
      note: data.get("note") || null,
      analysis_session_id: analysisSession,
    });
    if (submission.current?.body !== body)
      submission.current = { body, key: crypto.randomUUID() };
    try {
      await api("patient/adherence", {
        method: "POST",
        body,
        headers: { "Idempotency-Key": submission.current.key },
      });
      setSaved(true);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (saved)
    return (
      <section className="panel narrow">
        <div className="hero-icon">
          <Check />
        </div>
        <h2 role="status">{t("saved")}</h2>
        <Link href="/workspace/today" className="primary">
          {t("done")}
          <ArrowRight size={18} />
        </Link>
      </section>
    );
  return (
    <div className="narrow">
      <Link className="text-link" href="/workspace/today">
        {t("back")}
      </Link>
      <section className="panel">
        <h2>{exerciseName(item.exercise_id)}</h2>
        <p className="muted">
          {item.sets} {t("sets")} · {item.reps} {t("reps")}
        </p>
        {item.instructions && <p>{item.instructions}</p>}
        {item.precautions && <p className="notice">{item.precautions}</p>}
        {analysisSession && (
          <p className="success" role="status">
            {t("analysisAttached")}
          </p>
        )}
        <button
          className="secondary"
          disabled={busy}
          aria-expanded={analyzing}
          onClick={() => setAnalyzing(!analyzing)}
        >
          {t(analyzing ? "back" : "analyze")}
        </button>
        {analyzing && (
          <AnalyzeView
            initialExercise={item.exercise_id}
            patientId={today.patient_id}
            onCompleted={(id) => {
              setAnalysisSession(id);
              setAnalyzing(false);
            }}
          />
        )}
        <form onSubmit={submit}>
          <fieldset disabled={busy}>
            <label>
              {t("status")}
              <select
                name="completion_status"
                defaultValue={item.completion_status ?? "completed"}
              >
                <option value="completed">{t("complete")}</option>
                <option value="partial">{t("partial")}</option>
                <option value="not_completed">{t("missed")}</option>
              </select>
            </label>
            <div className="form-columns">
              <label>
                {t("painBefore")}
                <input
                  type="number"
                  min={0}
                  max={10}
                  name="pain_before"
                  defaultValue={item.pain_before ?? ""}
                />
              </label>
              <label>
                {t("painAfter")}
                <input
                  type="number"
                  min={0}
                  max={10}
                  name="pain_after"
                  defaultValue={item.pain_after ?? ""}
                />
              </label>
            </div>
            <div className="form-columns">
              <label>
                {t("difficulty")}
                <input
                  type="number"
                  min={1}
                  max={5}
                  name="difficulty"
                  defaultValue={item.difficulty ?? ""}
                />
              </label>
              <label>
                {t("fatigue")}
                <input
                  type="number"
                  min={1}
                  max={5}
                  name="fatigue"
                  defaultValue={item.fatigue ?? ""}
                />
              </label>
            </div>
            <label>
              {t("exertion")}
              <input
                type="number"
                min={0}
                max={10}
                name="perceived_exertion"
                defaultValue={item.perceived_exertion ?? ""}
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={symptoms}
                onChange={(e) => setSymptoms(e.target.checked)}
              />
              {t("symptoms")}
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={stopped}
                onChange={(e) => setStopped(e.target.checked)}
              />
              {t("stopped")}
            </label>
            <fieldset>
              <legend>{t("symptomFlags")}</legend>
              {symptomFlags.map((flag) => (
                <label className="check-label" key={flag}>
                  <input
                    type="checkbox"
                    checked={flags.includes(flag)}
                    onChange={(event) =>
                      setFlags((old) =>
                        event.target.checked
                          ? [...old, flag]
                          : old.filter((value) => value !== flag),
                      )
                    }
                  />
                  {t(`flag_${flag}`)}
                </label>
              ))}
            </fieldset>
            {(symptoms || stopped || flags.length > 0) && (
              <div className="notice">
                <p>{t("safety")}</p>
                <label className="checkbox">
                  <input type="checkbox" required name="safety" />
                  {t("acknowledge")}
                </label>
              </div>
            )}
            <label>
              {t("notes")}
              <textarea
                name="note"
                maxLength={1000}
                rows={3}
                defaultValue={item.patient_comment ?? ""}
              />
            </label>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            <button className="primary">
              {t(busy ? "loading" : "save")}
              <Check size={18} />
            </button>
          </fieldset>
        </form>
      </section>
    </div>
  );
}
