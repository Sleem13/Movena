import { useCallback } from "react";
import { View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getCoachingDashboard, getPatient, getPatientAdherence, type AdherenceResponse, type CoachingDashboard, type PatientDetail } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, NavRow, careStyles } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";
import { completionLabel } from "@/src/utils/care";

type PatientWorkspace = { patient: PatientDetail; adherence: AdherenceResponse[]; coaching: CoachingDashboard };
export default function PatientScreen() { return <CareAccess roles={["therapist", "admin", "super_admin"]} active="patients"><PatientContent /></CareAccess>; }
function PatientContent() {
  const router = useRouter(); const { id = "" } = useLocalSearchParams<{ id: string }>();
  const fetchPatient = useCallback(async (): Promise<PatientWorkspace> => { const [patient, adherence, coaching] = await Promise.all([getPatient(id), getPatientAdherence(id), getCoachingDashboard(id)]); return { patient, adherence, coaching }; }, [id]);
  const { data, loading, error, reload } = useCareResource(fetchPatient);
  return <AppShell active="patients"><BrandHeader title={data?.patient.display_name || "Patient"} subtitle={data?.patient.clinical_group || "Plan, goals, and recent exercise responses."} />
    {loading ? <Loading label="Loading patient" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : data ? <>
      <View style={careStyles.row}><Card tone="blue"><Body muted>Movement checks</Body><Heading>{data.patient.progress.total_sessions}</Heading></Card><Card><Body muted>Active goals</Body><Heading>{data.coaching.summary.active_goals}</Heading></Card></View>
      {data.adherence.some((row) => row.clinician_review_required && !row.reviewed_at) ? <Card tone="warning"><Heading>Follow-up needed</Heading><Body>One or more exercise responses are waiting for clinical review.</Body><PrimaryButton title="Open review queue" onPress={() => router.push("/review")} /></Card> : null}
      <View style={careStyles.section}><Heading>Goals</Heading>{data.coaching.goals.length ? data.coaching.goals.slice(0, 3).map((goal) => <Card key={goal.goal_id}><StatusBadge label={`${goal.progress_percent}%`} tone="blue" /><Heading>{goal.title}</Heading><Body>{goal.specific_action}</Body><Body muted>Target {new Date(goal.target_date).toLocaleDateString()}</Body></Card>) : <EmptyState title="No shared goals" message="Add goals from the clinical web workspace with the patient's agreement." />}</View>
      <View style={careStyles.section}><Heading>Recent check-ins</Heading>{data.adherence.length ? data.adherence.slice(0, 5).map((row) => <Card key={row.adherence_id}><View style={careStyles.row}><StatusBadge label={completionLabel(row.completion_status)} tone={row.clinician_review_required && !row.reviewed_at ? "warning" : "muted"} /><Body muted>{new Date(row.scheduled_date).toLocaleDateString()}</Body></View>{row.note ? <Body>{row.note}</Body> : null}<Body muted>Pain {row.pain_before ?? "—"} → {row.pain_after ?? "—"} · effort {row.perceived_exertion ?? "—"}/10</Body></Card>) : <EmptyState title="No check-ins yet" message="Patient exercise responses will appear here." />}</View>
      <NavRow title="Care connection" detail="Review this patient's connection status" icon="people-outline" onPress={() => router.push("/care-team")} />
    </> : null}
  </AppShell>;
}
