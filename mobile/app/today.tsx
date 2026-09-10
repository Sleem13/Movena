import { useEffect, useMemo, useRef, useState } from "react";
import { Alert, Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useLocalSearchParams, useRouter } from "expo-router";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, Check, Choice, Field, NavRow, careStyles } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { getToday, logAdherence, type PlanItem, type Today } from "@/src/api/care";
import { colors } from "@/src/config/theme";
import { completionLabel, exerciseName, optionalScore, symptomOptions } from "@/src/utils/care";

const completionOptions = [["completed", "Completed"], ["partial", "Partly completed"], ["not_completed", "Not completed"]] as const;

export default function TodayScreen() {
  return <CareAccess roles={["patient"]} active="today"><TodayContent /></CareAccess>;
}

function TodayContent() {
  const router = useRouter();
  const params = useLocalSearchParams<{ planItemId?: string; analysisSessionId?: string }>();
  const [data, setData] = useState<Today | null>(null);
  const [selected, setSelected] = useState<PlanItem | null>(null);
  const [form, setForm] = useState({ completion_status: "completed", pain_before: "", pain_after: "", difficulty: "", fatigue: "", perceived_exertion: "", symptoms_changed: false, stopped_due_to_symptoms: false, symptom_flags: [] as string[], safety_acknowledged: false, note: "" });
  const [notice, setNotice] = useState<{ message: string; review: boolean } | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const submitKey = useRef("");
  const openedAnalysisItem = useRef("");
  const load = async () => { setBusy(true); setError(""); try { setData(await getToday()); } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not load your plan."); } finally { setBusy(false); } };
  useEffect(() => { void load(); }, []);
  const open = (item: PlanItem) => {
    setSelected(item); setNotice(null); submitKey.current = `${Date.now()}-${Math.random()}`;
    setForm({ completion_status: item.completion_status || "completed", pain_before: item.pain_before?.toString() || "", pain_after: item.pain_after?.toString() || "", difficulty: item.difficulty?.toString() || "", fatigue: item.fatigue?.toString() || "", perceived_exertion: item.perceived_exertion?.toString() || "", symptoms_changed: item.symptoms_changed || false, stopped_due_to_symptoms: item.stopped_due_to_symptoms || false, symptom_flags: item.symptom_flags || [], safety_acknowledged: false, note: item.patient_comment || "" });
  };
  useEffect(() => {
    if (!params.planItemId || openedAnalysisItem.current === params.planItemId) return;
    const item = data?.plan_items.find((row) => row.item_id === params.planItemId);
    if (item) { openedAnalysisItem.current = params.planItemId; open(item); }
  }, [data, params.planItemId]);
  const completed = data?.plan_items.filter((item) => item.completion_status).length || 0;
  const progress = data?.plan_items.length ? completed / data.plan_items.length : 0;
  const hasSymptoms = form.symptoms_changed || form.stopped_due_to_symptoms || form.symptom_flags.length > 0;
  const save = async () => {
    if (!selected || !data) return;
    try {
      const payload = { plan_item_id: selected.item_id, scheduled_date: data.date, completion_status: form.completion_status, pain_before: optionalScore(form.pain_before, "Pain before", 0, 10), pain_after: optionalScore(form.pain_after, "Pain after", 0, 10), difficulty: optionalScore(form.difficulty, "Difficulty", 1, 5), fatigue: optionalScore(form.fatigue, "Fatigue", 1, 5), perceived_exertion: optionalScore(form.perceived_exertion, "Effort", 0, 10), symptoms_changed: form.symptoms_changed, stopped_due_to_symptoms: form.stopped_due_to_symptoms, symptom_flags: form.symptom_flags, safety_acknowledged: form.safety_acknowledged, note: form.note.trim() || null, analysis_session_id: params.analysisSessionId || selected.analysis_session_id || null };
      if (hasSymptoms && !form.safety_acknowledged) throw new Error("Confirm the safety message before saving symptoms.");
      setBusy(true); const response = await logAdherence(payload, submitKey.current);
      const result = response as { supportive_instruction?: string; clinician_review_required?: boolean };
      setNotice({ message: result.supportive_instruction || "Your check-in was saved.", review: Boolean(result.clinician_review_required) });
      setSelected(null); await load();
    } catch (cause) { Alert.alert("Could not save check-in", cause instanceof Error ? cause.message : "Please try again."); setBusy(false); }
  };
  return <AppShell active="today">
    <BrandHeader title="Your plan, today" subtitle="One step at a time." />
    {notice ? <Card tone={notice.review ? "warning" : "blue"}><Heading>{notice.review ? "Your therapist needs to review this" : "Check-in saved"}</Heading><Body>{notice.message}</Body></Card> : null}
    {busy && !data ? <Loading label="Loading your plan" /> : null}
    {error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={load} />} /> : null}
    {data ? <>
      <View style={styles.summary}><Text style={styles.summaryTitle}>Your daily plan</Text><Text style={styles.summaryText}>{completed} of {data.plan_items.length} exercises checked in</Text><View accessibilityRole="progressbar" accessibilityValue={{ min: 0, max: data.plan_items.length, now: completed }} style={styles.track}><View style={[styles.bar, { width: `${Math.round(progress * 100)}%` }]} /></View></View>
      <View style={careStyles.section}><Heading>Prescribed exercises</Heading>
        {data.plan_items.length ? data.plan_items.map((item, index) => <View key={item.item_id} style={styles.exerciseRow}><View style={styles.number}><Text style={styles.numberText}>{index + 1}</Text></View><View style={careStyles.flex}><Text style={careStyles.rowTitle}>{exerciseName(item.exercise_id)}</Text><Text style={careStyles.detail}>{item.sets} sets × {item.reps} reps{item.duration_minutes ? ` · ${item.duration_minutes} min` : ""}</Text>{item.created_by_name ? <Text style={styles.therapist}>From {item.created_by_name}</Text> : null}{item.precautions ? <Text style={styles.precaution}>Precaution: {item.precautions}</Text> : null}</View>{item.completion_status ? <StatusBadge label={completionLabel(item.completion_status)} tone={item.clinician_review_required ? "warning" : "success"} /> : <Pressable accessibilityRole="button" onPress={() => open(item)} style={styles.checkIn}><Text style={styles.checkInText}>Check in</Text></Pressable>}</View>) : <EmptyState title="Rest day" message="No exercises are scheduled today." />}
      </View>
      <NavRow title="Movement check" detail="Record an exercise for review" icon="videocam-outline" onPress={() => router.push("/identify")} />
      <View style={careStyles.section}><Heading>Next appointment</Heading><NavRow title={data.upcoming_appointment ? new Date(data.upcoming_appointment.starts_at).toLocaleString() : "No appointment scheduled"} detail={data.upcoming_appointment?.delivery_mode === "video" ? "Private video appointment" : undefined} icon="calendar-outline" onPress={() => router.push("/appointments")} /></View>
    </> : null}
    {selected ? <Card tone="blue"><Heading>Exercise check-in</Heading><Body>{exerciseName(selected.exercise_id)}</Body><Choice options={completionOptions} value={form.completion_status} onChange={(value) => setForm((current) => ({ ...current, completion_status: value }))} /><View style={styles.fields}><Field label="Pain before (0–10)" keyboardType="number-pad" value={form.pain_before} onChangeText={(value) => setForm((current) => ({ ...current, pain_before: value }))} /><Field label="Pain after (0–10)" keyboardType="number-pad" value={form.pain_after} onChangeText={(value) => setForm((current) => ({ ...current, pain_after: value }))} /><Field label="Difficulty (1–5)" keyboardType="number-pad" value={form.difficulty} onChangeText={(value) => setForm((current) => ({ ...current, difficulty: value }))} /><Field label="Effort (0–10)" keyboardType="number-pad" value={form.perceived_exertion} onChangeText={(value) => setForm((current) => ({ ...current, perceived_exertion: value }))} /></View>
      <Field label="Fatigue (1–5)" keyboardType="number-pad" value={form.fatigue} onChangeText={(value) => setForm((current) => ({ ...current, fatigue: value }))} />
      <Check label="I noticed new or worsening symptoms" checked={form.symptoms_changed} onChange={(value) => setForm((current) => ({ ...current, symptoms_changed: value }))} /><Check label="I stopped because of symptoms" checked={form.stopped_due_to_symptoms} onChange={(value) => setForm((current) => ({ ...current, stopped_due_to_symptoms: value }))} />
      {hasSymptoms ? <View style={styles.symptoms}><Text style={careStyles.label}>What did you notice?</Text>{symptomOptions.map(([key, label]) => <Check key={key} label={label} checked={form.symptom_flags.includes(key)} onChange={(checked) => setForm((current) => ({ ...current, symptom_flags: checked ? [...current.symptom_flags, key] : current.symptom_flags.filter((item) => item !== key) }))} />)}<Card tone="warning"><Body>This check-in is not monitored in real time and does not replace urgent or clinical care.</Body><Check label="I understand this safety message" checked={form.safety_acknowledged} onChange={(value) => setForm((current) => ({ ...current, safety_acknowledged: value }))} /></Card></View> : null}
      <Field label="Note for your therapist (optional)" multiline value={form.note} onChangeText={(value) => setForm((current) => ({ ...current, note: value }))} /><PrimaryButton title={busy ? "Saving…" : "Save check-in"} disabled={busy} onPress={save} /><PrimaryButton title="Cancel" secondary onPress={() => setSelected(null)} />
    </Card> : null}
  </AppShell>;
}

const styles = StyleSheet.create({
  summary: { backgroundColor: colors.paleBlue, borderRadius: 18, padding: 20, gap: 8 }, summaryTitle: { color: colors.text, fontWeight: "800", fontSize: 18 }, summaryText: { color: colors.muted, fontSize: 15 }, track: { height: 8, borderRadius: 4, backgroundColor: "#DCE6F4", overflow: "hidden", marginTop: 7 }, bar: { height: 8, borderRadius: 4, backgroundColor: colors.primary },
  exerciseRow: { minHeight: 92, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: colors.border, flexDirection: "row", alignItems: "center", gap: 12 }, number: { width: 42, height: 42, borderRadius: 21, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" }, numberText: { color: colors.primaryDark, fontSize: 16, fontWeight: "800" }, checkIn: { minHeight: 44, justifyContent: "center", backgroundColor: colors.primary, borderRadius: 12, paddingHorizontal: 14 }, checkInText: { color: "#FFFFFF", fontSize: 14, fontWeight: "700" }, therapist: { color: colors.muted, fontSize: 12 }, precaution: { color: "#9A6700", fontSize: 12, lineHeight: 18 }, fields: { gap: 12 }, symptoms: { gap: 4 },
});
