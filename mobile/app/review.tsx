import { useCallback, useState } from "react";
import { Alert, StyleSheet, View } from "react-native";
import { getPatientAdherence, getPatients, acknowledgeResponse, type AdherenceResponse, type PatientSummary } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, Choice, Field } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";

type ReviewItem = AdherenceResponse & { patient_name: string };
const dispositions = [["contacted_patient", "Contacted patient"], ["plan_modified", "Plan modified"], ["appointment_scheduled", "Appointment scheduled"], ["referred_for_medical_review", "Medical review"], ["reviewed_no_change", "Reviewed, no change"]] as const;
export default function ReviewScreen() { return <CareAccess roles={["therapist"]} active="review"><ReviewContent /></CareAccess>; }
function ReviewContent() {
  const [selected, setSelected] = useState<ReviewItem | null>(null); const [disposition, setDisposition] = useState("contacted_patient"); const [note, setNote] = useState(""); const [busy, setBusy] = useState(false);
  const fetchQueue = useCallback(async () => { const patients: PatientSummary[] = await getPatients(); const lists = await Promise.all(patients.map(async (patient) => (await getPatientAdherence(patient.patient_id)).map((item) => ({ ...item, patient_name: patient.display_name })))); return lists.flat().filter((item) => item.clinician_review_required && !item.reviewed_at).sort((a, b) => b.scheduled_date.localeCompare(a.scheduled_date)); }, []);
  const { data, loading, error, reload } = useCareResource(fetchQueue);
  const submit = async () => { if (!selected) return; if (disposition === "reviewed_no_change" && !note.trim()) return Alert.alert("Add a rationale", "Document why no change is needed."); try { setBusy(true); await acknowledgeResponse(selected.patient_id, selected.adherence_id, { disposition, note: note.trim() || null, clinician_attestation: true }); setSelected(null); setNote(""); await reload(); } catch (cause) { Alert.alert("Could not save review", cause instanceof Error ? cause.message : "Please try again."); } finally { setBusy(false); } };
  return <AppShell active="review"><BrandHeader title="Review queue" subtitle="Exercise responses that need clinical follow-up." />
      {loading ? <Loading label="Loading review queue" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : !data?.length ? <EmptyState title="No responses waiting" message="New symptom and exercise follow-ups will appear here." /> : data.map((item) => <Card key={item.adherence_id} tone="warning"><View style={styles.row}><StatusBadge label="Follow-up needed" tone="warning" /><Body muted>{new Date(item.scheduled_date).toLocaleDateString()}</Body></View><Heading>{item.patient_name}</Heading><Body>{item.supportive_instruction || "Review the recorded response and contact the patient when appropriate."}</Body>{item.symptom_flags.length ? <Body muted>Reported: {item.symptom_flags.map((flag) => flag.replaceAll("_", " ")).join(", ")}</Body> : null}<PrimaryButton title="Review response" onPress={() => { setSelected(item); setDisposition("contacted_patient"); setNote(""); }} /></Card>)}
    {selected ? <Card tone="blue"><Heading>Record clinical follow-up</Heading><Body>{selected.patient_name}</Body><Choice options={dispositions} value={disposition} onChange={setDisposition} /><Field label={disposition === "reviewed_no_change" ? "Clinical rationale" : "Review note (optional)"} multiline value={note} onChangeText={setNote} /><Body muted>I confirm that I reviewed this response using clinical judgment.</Body><PrimaryButton title={busy ? "Saving…" : "Complete review"} disabled={busy} onPress={submit} /><PrimaryButton title="Cancel" secondary onPress={() => setSelected(null)} /></Card> : null}
  </AppShell>;
}
const styles = StyleSheet.create({ row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 10 } });
