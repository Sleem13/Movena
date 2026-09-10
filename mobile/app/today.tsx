import { useCallback, useEffect, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useFocusEffect, useLocalSearchParams, useRouter } from "expo-router";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, Check, Choice, Field, NavRow, careStyles } from "@/src/components/CareUI";
import { CarePlanItem } from "@/src/components/CarePlanItem";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton } from "@/src/components/UI";
import { getToday, logAdherence, type PlanItem, type Today } from "@/src/api/care";
import { colors } from "@/src/config/theme";
import { calendarDate, exerciseName, linkedAnalysisForItem, optionalScore, symptomOptions } from "@/src/utils/care";

const completionOptions = [["completed", "Completed"], ["partial", "Partly completed"], ["not_completed", "Not completed"]] as const;
const emptyForm = { completion_status: "completed", pain_before: "", pain_after: "", difficulty: "", fatigue: "", perceived_exertion: "", symptoms_changed: false, stopped_due_to_symptoms: false, symptom_flags: [] as string[], safety_acknowledged: false, note: "" };

export default function TodayScreen() {
  return <CareAccess roles={["patient"]} active="today"><TodayContent /></CareAccess>;
}

function TodayContent() {
  const router = useRouter();
  const params = useLocalSearchParams<{ planItemId?: string; analysisSessionId?: string }>();
  const [data, setData] = useState<Today | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<PlanItem | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [notice, setNotice] = useState<{ message: string; review: boolean } | null>(null);
  const [error, setError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const requestGeneration = useRef(0);
  const submitting = useRef(false);
  const submitKey = useRef("");
  const openedAnalysisItem = useRef("");

  const load = useCallback(async () => {
    const request = ++requestGeneration.current;
    setLoading(true); setError("");
    try {
      const next = await getToday();
      if (request !== requestGeneration.current) return;
      setData(next);
      setExpandedId((current) => current || next.plan_items.find((item) => !item.completion_status)?.item_id || next.plan_items[0]?.item_id || null);
    } catch (cause) {
      if (request === requestGeneration.current) setError(cause instanceof Error ? cause.message : "Could not load your plan.");
    } finally { if (request === requestGeneration.current) setLoading(false); }
  }, []);
  useFocusEffect(useCallback(() => { void load(); return () => { requestGeneration.current++; }; }, [load]));

  const open = useCallback((item: PlanItem) => {
    setSelected(item); setExpandedId(item.item_id); setNotice(null); setSaveError("");
    submitKey.current = `${Date.now()}-${Math.random()}`;
    setForm({ ...emptyForm, completion_status: item.completion_status || "completed", pain_before: item.pain_before?.toString() || "", pain_after: item.pain_after?.toString() || "", difficulty: item.difficulty?.toString() || "", fatigue: item.fatigue?.toString() || "", perceived_exertion: item.perceived_exertion?.toString() || "", symptoms_changed: item.symptoms_changed || false, stopped_due_to_symptoms: item.stopped_due_to_symptoms || false, symptom_flags: item.symptom_flags || [], note: item.patient_comment || "" });
  }, []);
  useEffect(() => {
    if (!params.planItemId || openedAnalysisItem.current === params.planItemId) return;
    const item = data?.plan_items.find((row) => row.item_id === params.planItemId);
    if (item) { openedAnalysisItem.current = params.planItemId; open(item); }
  }, [data, open, params.planItemId]);

  const checkedIn = data?.plan_items.filter((item) => Boolean(item.completion_status)).length || 0;
  const completed = data?.plan_items.filter((item) => item.completion_status === "completed").length || 0;
  const progress = data?.plan_items.length ? checkedIn / data.plan_items.length : 0;
  const hasSymptoms = form.symptoms_changed || form.stopped_due_to_symptoms || form.symptom_flags.length > 0;
  const save = async () => {
    if (!selected || !data || submitting.current) return;
    setSaveError("");
    try {
      const payload = { plan_item_id: selected.item_id, scheduled_date: data.date, completion_status: form.completion_status, pain_before: optionalScore(form.pain_before, "Pain before", 0, 10), pain_after: optionalScore(form.pain_after, "Pain after", 0, 10), difficulty: optionalScore(form.difficulty, "Difficulty", 1, 5), fatigue: optionalScore(form.fatigue, "Fatigue", 1, 5), perceived_exertion: optionalScore(form.perceived_exertion, "Effort", 0, 10), symptoms_changed: form.symptoms_changed, stopped_due_to_symptoms: form.stopped_due_to_symptoms, symptom_flags: form.symptom_flags, safety_acknowledged: form.safety_acknowledged, note: form.note.trim() || null, analysis_session_id: linkedAnalysisForItem(params.planItemId, params.analysisSessionId, selected) };
      if (hasSymptoms && !form.safety_acknowledged) throw new Error("Confirm the safety message before saving symptoms.");
      submitting.current = true; setSaving(true);
      const response = await logAdherence(payload, submitKey.current) as { supportive_instruction?: string; clinician_review_required?: boolean };
      setNotice({ message: response.supportive_instruction || "Your check-in was saved.", review: Boolean(response.clinician_review_required) });
      setSelected(null); await load();
    } catch (cause) {
      setSaveError(cause instanceof Error ? cause.message : "Could not save your check-in. Please try again.");
    } finally { submitting.current = false; setSaving(false); }
  };
  const dateLabel = data ? calendarDate(data.date).toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" }) : "Today";

  return <AppShell active="today">
    <BrandHeader title="Your plan, today" subtitle={dateLabel} />
    {notice ? <Card tone={notice.review ? "warning" : "blue"}><Heading>{notice.review ? "Shared for therapist review" : "Check-in saved"}</Heading><Body>{notice.message}</Body></Card> : null}
    {loading && !data ? <Loading label="Loading your plan" /> : null}
    {error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={load} />} /> : null}
    {data ? <>
      <View style={styles.summary}>
        <View style={styles.summaryText}><Text style={styles.summaryTitle}>{checkedIn} of {data.plan_items.length} checked in</Text><Text style={styles.summaryDetail}>{completed} fully completed</Text></View>
        <Text style={styles.percent}>{Math.round(progress * 100)}%</Text>
        <View accessibilityRole="progressbar" accessibilityValue={{ min: 0, max: data.plan_items.length, now: checkedIn }} style={styles.track}><View style={[styles.bar, { width: `${Math.round(progress * 100)}%` }]} /></View>
      </View>
      <View style={careStyles.section}>
        <View style={styles.sectionHeading}><Heading>{data.plan_title || "Today’s plan"}</Heading><Body muted>{data.plan_items.length} {data.plan_items.length === 1 ? "exercise" : "exercises"}</Body></View>
        {data.plan_items.length ? data.plan_items.map((item, index) => <View key={item.item_id} style={styles.itemWrap}>
          <CarePlanItem item={item} index={index} expanded={expandedId === item.item_id} disabled={saving} onToggle={() => setExpandedId((current) => current === item.item_id ? null : item.item_id)} onCheckIn={() => open(item)} onMovementCheck={() => router.push({ pathname: "/upload/[id]", params: { id: item.exercise_id, planItemId: item.item_id, scheduledDate: data.date } })} />
          {selected?.item_id === item.item_id ? <CheckInForm item={selected} form={form} setForm={setForm} hasSymptoms={hasSymptoms} saving={saving} saveError={saveError} onSave={save} onCancel={() => { if (!saving) { setSelected(null); setSaveError(""); } }} /> : null}
        </View>) : <EmptyState title="Rest day" message="No exercises are scheduled today. Your next care task will appear here." />}
      </View>
      <View style={styles.appointment}><View style={styles.appointmentIcon}><Ionicons name="calendar-outline" size={22} color={colors.primary} /></View><View style={careStyles.flex}><Text style={styles.appointmentTitle}>Next appointment</Text><Text style={styles.appointmentDate}>{data.upcoming_appointment ? new Date(data.upcoming_appointment.starts_at).toLocaleString() : "No appointment scheduled"}</Text><Text style={styles.appointmentMeta}>{data.upcoming_appointment?.delivery_mode === "video" ? "Private video appointment" : data.upcoming_appointment ? "In-person appointment" : "Your confirmed sessions will appear here."}</Text></View><Pressable accessibilityRole="button" accessibilityLabel="View appointments" onPress={() => router.push("/appointments")} style={styles.arrow}><Ionicons name="chevron-forward" size={20} color={colors.muted} /></Pressable></View>
      <NavRow title="Explore movement checks" detail="Record an exercise outside today’s plan" icon="videocam-outline" onPress={() => router.push("/identify")} />
    </> : null}
  </AppShell>;
}

function CheckInForm({ item, form, setForm, hasSymptoms, saving, saveError, onSave, onCancel }: { item: PlanItem; form: typeof emptyForm; setForm: React.Dispatch<React.SetStateAction<typeof emptyForm>>; hasSymptoms: boolean; saving: boolean; saveError: string; onSave: () => void; onCancel: () => void }) {
  return <Card tone="blue"><Heading>Check in: {exerciseName(item.exercise_id)}</Heading><Body muted>Share what you completed and how it felt. Scores are optional.</Body>
    <Choice options={completionOptions} value={form.completion_status} onChange={(value) => setForm((current) => ({ ...current, completion_status: value }))} />
    <View style={styles.fields}><Field label="Pain before (0–10, optional)" keyboardType="number-pad" editable={!saving} value={form.pain_before} onChangeText={(value) => setForm((current) => ({ ...current, pain_before: value }))} /><Field label="Pain after (0–10, optional)" keyboardType="number-pad" editable={!saving} value={form.pain_after} onChangeText={(value) => setForm((current) => ({ ...current, pain_after: value }))} /><Field label="Difficulty (1–5, optional)" keyboardType="number-pad" editable={!saving} value={form.difficulty} onChangeText={(value) => setForm((current) => ({ ...current, difficulty: value }))} /><Field label="Effort (0–10, optional)" keyboardType="number-pad" editable={!saving} value={form.perceived_exertion} onChangeText={(value) => setForm((current) => ({ ...current, perceived_exertion: value }))} /></View>
    <Field label="Fatigue (1–5, optional)" keyboardType="number-pad" editable={!saving} value={form.fatigue} onChangeText={(value) => setForm((current) => ({ ...current, fatigue: value }))} />
    <Check label="I noticed new or worsening symptoms" checked={form.symptoms_changed} disabled={saving} onChange={(value) => setForm((current) => ({ ...current, symptoms_changed: value }))} /><Check label="I stopped because of symptoms" checked={form.stopped_due_to_symptoms} disabled={saving} onChange={(value) => setForm((current) => ({ ...current, stopped_due_to_symptoms: value }))} />
    {hasSymptoms ? <View style={styles.symptoms}><Text style={careStyles.label}>What did you notice?</Text>{symptomOptions.map(([key, label]) => <Check key={key} label={label} checked={form.symptom_flags.includes(key)} disabled={saving} onChange={(checked) => setForm((current) => ({ ...current, symptom_flags: checked ? [...current.symptom_flags, key] : current.symptom_flags.filter((value) => value !== key) }))} />)}<Card tone="warning"><Body>This check-in is not monitored in real time and does not replace urgent or clinical care.</Body><Check label="I understand this safety message" checked={form.safety_acknowledged} disabled={saving} onChange={(value) => setForm((current) => ({ ...current, safety_acknowledged: value }))} /></Card></View> : null}
    <Field label="Note for your therapist (optional)" multiline maxLength={1000} editable={!saving} value={form.note} onChangeText={(value) => setForm((current) => ({ ...current, note: value }))} />
    {saveError ? <ErrorState message={saveError} /> : null}<PrimaryButton title={saving ? "Saving…" : "Save check-in"} disabled={saving} onPress={onSave} /><PrimaryButton title="Cancel" secondary disabled={saving} onPress={onCancel} />
  </Card>;
}

const styles = StyleSheet.create({
  summary: { padding: 18, borderWidth: 1, borderColor: colors.border, borderRadius: 16, backgroundColor: colors.card, flexDirection: "row", flexWrap: "wrap", alignItems: "center", gap: 10 }, summaryText: { flex: 1, minWidth: 180, gap: 3 }, summaryTitle: { color: colors.text, fontSize: 17, fontWeight: "800" }, summaryDetail: { color: colors.muted, fontSize: 13 }, percent: { color: colors.text, fontSize: 15, fontWeight: "800" }, track: { width: "100%", height: 8, borderRadius: 4, backgroundColor: "#E7E7E3", overflow: "hidden" }, bar: { height: 8, borderRadius: 4, backgroundColor: colors.teal },
  sectionHeading: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12 }, itemWrap: { gap: 10 }, fields: { gap: 12 }, symptoms: { gap: 4 },
  appointment: { flexDirection: "row", alignItems: "center", gap: 13, padding: 17, borderWidth: 1, borderColor: colors.border, borderRadius: 16, backgroundColor: colors.card }, appointmentIcon: { width: 44, height: 44, borderRadius: 14, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" }, appointmentTitle: { color: colors.text, fontSize: 15, fontWeight: "800" }, appointmentDate: { color: colors.text, fontSize: 14, lineHeight: 20 }, appointmentMeta: { color: colors.muted, fontSize: 12, lineHeight: 18 }, arrow: { width: 44, height: 44, alignItems: "center", justifyContent: "center" },
});
