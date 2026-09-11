import { useCallback, useRef, useState } from "react";
import { StyleSheet, View } from "react-native";
import { getPatientAdherence, getPatients, acknowledgeResponse, type AdherenceResponse } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, Check, Choice, Field } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";
import { completionLabel, needsReview } from "@/src/utils/care";

type ReviewItem = AdherenceResponse & { patient_name: string };
const dispositions = [["contacted_patient", "Contacted patient"], ["plan_modified", "Plan modified"], ["appointment_scheduled", "Appointment scheduled"], ["referred_for_medical_review", "Medical review"], ["reviewed_no_change", "Reviewed, no change"]] as const;
export default function ReviewScreen() {
  return <CareAccess roles={["therapist", "admin", "super_admin"]} active="review"><ReviewContent /></CareAccess>;
}
function ReviewContent() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [disposition, setDisposition] = useState("contacted_patient");
  const [note, setNote] = useState("");
  const [attested, setAttested] = useState(false);
  const [busy, setBusy] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [savedName, setSavedName] = useState("");
  const submitting = useRef(false);
  const fetchQueue = useCallback(async () => {
    const patients = await getPatients();
    const lists = await Promise.all(patients.map(async (patient) =>
      (await getPatientAdherence(patient.patient_id)).map((item) => ({ ...item, patient_name: patient.display_name }))));
    return lists.flat().filter(needsReview).sort((a, b) => b.scheduled_date.localeCompare(a.scheduled_date));
  }, []);
  const { data, loading, error, reload } = useCareResource(fetchQueue);
  const rationaleRequired = disposition === "reviewed_no_change";
  const canSubmit = attested && (!rationaleRequired || Boolean(note.trim()));
  const open = (item: ReviewItem) => {
    setSelectedId(item.adherence_id);
    setDisposition("contacted_patient"); setNote(""); setAttested(false);
    setSaveError(""); setSavedName("");
  };
  const submit = async (item: ReviewItem) => {
    if (submitting.current || !canSubmit) return;
    submitting.current = true; setBusy(true); setSaveError("");
    try {
      await acknowledgeResponse(item.patient_id, item.adherence_id, {
        disposition, note: note.trim() || null, clinician_attestation: attested,
      });
      setSelectedId(null); setSavedName(item.patient_name);
      await reload();
    } catch (cause) {
      setSaveError(cause instanceof Error ? cause.message : "Could not save this review. Please try again.");
    } finally { submitting.current = false; setBusy(false); }
  };
  return <AppShell active="review">
    <BrandHeader title="Review queue" subtitle="Exercise responses that need clinical follow-up." />
    {savedName ? <Card tone="blue"><Heading>Review saved</Heading><Body>Clinical follow-up recorded for {savedName}.</Body></Card> : null}
    {loading ? <Loading label="Loading review queue" /> : error ? (
      <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} />
    ) : !data?.length ? (
      <EmptyState title="No responses waiting" message="New symptom and exercise follow-ups will appear here." />
    ) : data.map((item) => <Card key={item.adherence_id} tone="warning">
      <View style={styles.row}><StatusBadge label="Follow-up needed" tone="warning" /><Body muted>{new Date(`${item.scheduled_date}T12:00:00`).toLocaleDateString()}</Body></View>
      <Heading>{item.patient_name}</Heading>
      <StatusBadge label={completionLabel(item.completion_status)} tone="muted" />
      <Body>Pain before: {item.pain_before ?? "Not reported"} · after: {item.pain_after ?? "Not reported"}</Body>
      <Body muted>Effort: {item.perceived_exertion == null ? "Not reported" : `${item.perceived_exertion}/10`} · difficulty: {item.difficulty == null ? "Not reported" : `${item.difficulty}/5`} · fatigue: {item.fatigue == null ? "Not reported" : `${item.fatigue}/5`}</Body>
      {item.symptoms_changed ? <Body>New or worsening symptoms reported.</Body> : null}
      {item.stopped_due_to_symptoms ? <Body>Stopped exercise because of symptoms.</Body> : null}
      {item.symptom_flags.length ? <Body>Reported: {item.symptom_flags.map((flag) => flag.replaceAll("_", " ")).join(", ")}</Body> : null}
      {item.note ? <View><Heading>Patient note</Heading><Body>{item.note}</Body></View> : null}
      {item.supportive_instruction ? <View><Heading>Guidance shown to patient</Heading><Body>{item.supportive_instruction}</Body></View> : null}
      {selectedId === item.adherence_id ? <Card tone="blue">
        <Heading>Record clinical follow-up</Heading>
        <Choice options={dispositions} value={disposition} onChange={(value) => { if (!busy) setDisposition(value); }} />
        <Field label={rationaleRequired ? "Clinical rationale (required)" : "Review note (optional)"} multiline maxLength={2000} editable={!busy} value={note} onChangeText={setNote} />
        {rationaleRequired && !note.trim() ? <Body muted>Explain why no change is needed before completing this review.</Body> : null}
        <Check label="I reviewed this response using clinical judgment" checked={attested} disabled={busy} onChange={setAttested} />
        {saveError ? <ErrorState message={saveError} /> : null}
        <PrimaryButton title={busy ? "Saving…" : "Complete review"} disabled={busy || !canSubmit} onPress={() => submit(item)} />
        <PrimaryButton title="Cancel" secondary disabled={busy} onPress={() => setSelectedId(null)} />
      </Card> : <PrimaryButton title="Review response" disabled={busy} onPress={() => open(item)} />}
    </Card>)}
  </AppShell>;
}
const styles = StyleSheet.create({ row: { flexDirection: "row", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 10 } });
