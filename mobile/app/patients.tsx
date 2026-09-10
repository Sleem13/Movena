import { useCallback, useMemo, useState } from "react";
import { StyleSheet, TextInput, View } from "react-native";
import { useRouter } from "expo-router";
import { getPatientAdherence, getPatients, type PatientSummary } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, NavRow, careStyles } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";
import { colors } from "@/src/config/theme";
import { initials } from "@/src/utils/care";

type Workspace = { patients: PatientSummary[]; reviewCount: number };
export default function PatientsScreen() { return <CareAccess roles={["therapist"]} active="patients"><PatientsContent /></CareAccess>; }
function PatientsContent() {
  const router = useRouter(); const [query, setQuery] = useState("");
  const fetchWorkspace = useCallback(async (): Promise<Workspace> => { const patients = await getPatients(); const responses = await Promise.all(patients.map((patient) => getPatientAdherence(patient.patient_id).catch(() => []))); return { patients, reviewCount: responses.flat().filter((row) => row.clinician_review_required && !row.reviewed_at).length }; }, []);
  const { data, loading, error, reload } = useCareResource(fetchWorkspace);
  const visible = useMemo(() => (data?.patients || []).filter((patient) => `${patient.display_name} ${patient.clinical_group || ""}`.toLowerCase().includes(query.trim().toLowerCase())), [data, query]);
  return <AppShell active="patients"><BrandHeader title="Your patients" subtitle="Focus on the next follow-up." />
    {data?.reviewCount ? <Card tone="warning"><Heading>{data.reviewCount} {data.reviewCount === 1 ? "response needs" : "responses need"} review</Heading><Body muted>Review symptoms and exercise responses that need clinical follow-up.</Body><PrimaryButton title="Open review queue" onPress={() => router.push("/review")} /></Card> : null}
    <TextInput accessibilityRole="search" accessibilityLabel="Search patients" value={query} onChangeText={setQuery} placeholder="Search patients" placeholderTextColor={colors.muted} style={styles.search} />
    <View style={careStyles.section}><Heading>Connected patients</Heading>{loading ? <Loading label="Loading patients" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : visible.length ? visible.map((patient) => <NavRow key={patient.patient_id} initials={initials(patient.display_name)} title={patient.display_name} detail={[patient.clinical_group, patient.session_count ? `${patient.session_count} movement checks` : "View plan and check-ins"].filter(Boolean).join(" · ")} onPress={() => router.push({ pathname: "/patient/[id]", params: { id: patient.patient_id } })} />) : <EmptyState title={query ? "No matching patients" : "No connected patients"} message={query ? "Try another name or clinical group." : "Invite a patient from Care connections."} />}</View>
    <PrimaryButton title="Care connections" secondary onPress={() => router.push("/care-team")} />
  </AppShell>;
}
const styles = StyleSheet.create({ search: { minHeight: 52, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.surface, color: colors.text, paddingHorizontal: 16, fontSize: 16 } });
